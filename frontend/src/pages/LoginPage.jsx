import { useAuth } from "react-oidc-context";
import { Link, Navigate, useLocation } from "react-router-dom";

export default function LoginPage() {
  const auth = useAuth();
  const location = useLocation();

  const loggedOut = new URLSearchParams(location.search).get("loggedOut") === "1";

  if (auth.isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  function handleLogin() {
    auth.signinRedirect();
  }

  return (
    <main className="page">
      <section className="card auth-card">
        <h1>Portfolio Manager</h1>

        {loggedOut && <p className="success">Successfully logged out.</p>}

        <p>
          Sign in or create an account with AWS Cognito to manage your investment
          portfolios.
        </p>

        <div className="auth-actions">
          <button
            type="button"
            className="auth-button"
            onClick={handleLogin}
            disabled={auth.isLoading}
          >
            {auth.isLoading ? "Loading..." : "Sign In"}
          </button>

          <Link className="auth-button auth-link-button" to="/signup">
            Sign Up
          </Link>
        </div>

        {auth.error && <p className="error">{auth.error.message}</p>}
      </section>
    </main>
  );
}
