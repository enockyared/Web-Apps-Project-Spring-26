import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { exchangeCodeForTokens } from "../auth/cognito";
import { useAuth } from "../auth/AuthContext";

export default function CallbackPage() {
  const navigate = useNavigate();
  const { saveTokens } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    async function completeLogin() {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");

        if (!code) {
          throw new Error("No authorization code was returned from Cognito.");
        }

        const tokens = await exchangeCodeForTokens(code);
        saveTokens(tokens);

        window.history.replaceState({}, document.title, "/callback");
        navigate("/", { replace: true });
      } catch (err) {
        setError(err.message || "Login failed. Please try again.");
      }
    }

    completeLogin();
  }, [navigate, saveTokens]);

  return (
    <main className="page">
      <section className="card">
        <h1>Completing sign in...</h1>
        {error && (
          <>
            <p className="error">{error}</p>
            <button onClick={() => navigate("/login")}>Back to Login</button>
          </>
        )}
      </section>
    </main>
  );
}
