import json
from functools import wraps
from urllib.request import urlopen

import jwt
from flask import current_app, g, jsonify, request


class AuthError(Exception):
    pass


def _get_jwks():

    region = current_app.config.get("COGNITO_REGION")
    user_pool_id = current_app.config.get("COGNITO_USER_POOL_ID")

    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"

    with urlopen(jwks_url) as response:
        jwks = json.loads(response.read())

    return jwks


def validate_token(token: str) -> dict:
    jwks = _get_jwks()

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if not rsa_key:
        raise AuthError("Unable to find appropriate key")

    region = current_app.config.get("COGNITO_REGION")
    user_pool_id = current_app.config.get("COGNITO_USER_POOL_ID")
    audience = current_app.config.get("COGNITO_APP_CLIENT_ID")

    issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"

    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=audience,
        issuer=issuer,
    )

    return payload


def _extract_bearer_token() -> str:
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise AuthError("Authorization header missing")

    parts = auth_header.split()

    if len(parts) != 2 or parts[0] != "Bearer":
        raise AuthError("Authorization header must be 'Bearer <token>'")

    return parts[1]


def require_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = _extract_bearer_token()

            payload = validate_token(token)

            g.current_user = payload
            g.username = payload.get("cognito:username") or payload.get("username")
            g.user_id = payload.get("sub")

        except AuthError as e:
            return jsonify({
                "error": "Forbidden",
                "detail": str(e)
            }), 403

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Forbidden",
                "detail": "Token expired"
            }), 403

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Forbidden",
                "detail": "Invalid token"
            }), 403

        except Exception as e:
            return jsonify({
                "error": "Forbidden",
                "detail": f"Authentication failed: {str(e)}"
            }), 403

        return f(*args, **kwargs)

    return decorated