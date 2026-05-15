const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
const redirectUri = import.meta.env.VITE_COGNITO_REDIRECT_URI;
const logoutUri = import.meta.env.VITE_COGNITO_LOGOUT_URI;

export function getLoginUrl() {
  const params = new URLSearchParams({
    response_type: "code",
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: "openid email profile",
  });

  return `${cognitoDomain}/oauth2/authorize?${params.toString()}`;
}

export function getLogoutUrl() {
  const params = new URLSearchParams({
    client_id: clientId,
    logout_uri: logoutUri,
  });

  return `${cognitoDomain}/logout?${params.toString()}`;
}

export async function exchangeCodeForTokens(code) {
  const tokenUrl = `${cognitoDomain}/oauth2/token`;

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: clientId,
    code,
    redirect_uri: redirectUri,
  });

  const response = await fetch(tokenUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  if (!response.ok) {
    throw new Error("Unable to complete login. Please try again.");
  }

  return response.json();
}
