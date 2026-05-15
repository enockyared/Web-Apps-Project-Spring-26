import { useEffect } from "react";

const COGNITO_DOMAIN =
  "https://us-east-1fajubhcm0.auth.us-east-1.amazoncognito.com";
const CLIENT_ID = "4kmni8v5627kbkbu2mu08anole";
const REDIRECT_URI = "http://localhost:5173";

export default function SignupPage() {
  useEffect(() => {
    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      response_type: "code",
      scope: "phone openid email",
      redirect_uri: REDIRECT_URI,
    });

    window.location.href = `${COGNITO_DOMAIN}/signup?${params.toString()}`;
  }, []);

  return (
    <main className="page">
      <section className="card">
        <h1>Redirecting to sign up...</h1>
        <p>You are being sent to the Cognito sign up page.</p>
      </section>
    </main>
  );
}
