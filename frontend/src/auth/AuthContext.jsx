import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { getLogoutUrl } from "./cognito";

const AuthContext = createContext(null);

const ID_TOKEN_KEY = "id_token";
const ACCESS_TOKEN_KEY = "access_token";

function isTokenExpired(token) {
  if (!token) {
    return true;
  }

  try {
    const decoded = jwtDecode(token);
    if (!decoded.exp) {
      return true;
    }

    return decoded.exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}

function getUsernameFromToken(token) {
  if (!token) {
    return "";
  }

  try {
    const decoded = jwtDecode(token);
    return decoded["cognito:username"] || decoded.username || decoded.email || "";
  } catch {
    return "";
  }
}

export function AuthProvider({ children }) {
  const [idToken, setIdToken] = useState(() => localStorage.getItem(ID_TOKEN_KEY));
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem(ACCESS_TOKEN_KEY));

  const isAuthenticated = Boolean(idToken) && !isTokenExpired(idToken);
  const username = isAuthenticated ? getUsernameFromToken(idToken) : "";

  useEffect(() => {
    if (idToken && isTokenExpired(idToken)) {
      localStorage.removeItem(ID_TOKEN_KEY);
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      setIdToken(null);
      setAccessToken(null);
    }
  }, [idToken]);

  function saveTokens(tokens) {
    if (!tokens?.id_token) {
      throw new Error("Login completed, but no identity token was returned.");
    }

    localStorage.setItem(ID_TOKEN_KEY, tokens.id_token);
    setIdToken(tokens.id_token);

    if (tokens.access_token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
      setAccessToken(tokens.access_token);
    }
  }

  function logout() {
    localStorage.removeItem(ID_TOKEN_KEY);
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    setIdToken(null);
    setAccessToken(null);
    window.location.href = getLogoutUrl();
  }

  const value = useMemo(
    () => ({
      idToken,
      accessToken,
      username,
      isAuthenticated,
      saveTokens,
      logout,
    }),
    [idToken, accessToken, username, isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }

  return context;
}
