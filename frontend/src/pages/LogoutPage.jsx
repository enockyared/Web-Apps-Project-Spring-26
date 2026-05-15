import { useEffect } from "react";
import { setAuthToken } from "../api/client";

const COGNITO_DOMAIN =
  "https://us-east-1fajubhcm0.auth.us-east-1.amazoncognito.com";
const CLIENT_ID = "4kmni8v5627kbkbu2mu08anole";
const LOGOUT_URI = "http://localhost:5173/login?loggedOut=1";

function clearOidcStorage() {
  Object.keys(localStorage).forEach((key) => {
    if (
      key.startsWith("oidc.") ||
      key.includes("cognito") ||
      key.includes("id_token") ||
      key.includes("access_token")
    ) {
      localStorage.removeItem(key);
    }
  });

  Object.keys(sessionStorage).forEach((key) => {
    if (
      key.startsWith("oidc.") ||
      key.includes("cognito") ||
      key.includes("id_token") ||
      key.includes("access_token")
    ) {
      sessionStorage.removeItem(key);
    }
  });
}

export default function LogoutPage() {
  useEffect(() => {
    setAuthToken("");
    clearOidcStorage();

    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      logout_uri: LOGOUT_URI,
    });

    const timer = setTimeout(() => {
      window.location.href = `${COGNITO_DOMAIN}/logout?${params.toString()}`;
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="page">
      <section className="card">
        <h1>Successfully logged out</h1>
        <p>You have been signed out and will be returned to the login page.</p>
      </section>
    </main>
  );
}