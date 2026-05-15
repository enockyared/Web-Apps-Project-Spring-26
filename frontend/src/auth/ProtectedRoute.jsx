import { Navigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";

export default function ProtectedRoute({ children }) {
  const auth = useAuth();

  if (auth.isLoading) {
    return (
      <main className="page">
        <section className="card">
          <p>Loading...</p>
        </section>
      </main>
    );
  }

  if (!auth.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
