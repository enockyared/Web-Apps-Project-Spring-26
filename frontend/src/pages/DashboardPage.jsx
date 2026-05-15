import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import AlertMessage from "../components/AlertMessage";
import CreatePortfolioForm from "../components/CreatePortfolioForm";
import PortfolioList from "../components/PortfolioList";
import { setAuthToken, getApiErrorMessage } from "../api/client";
import { getUser } from "../api/users";
import {
  createPortfolio,
  deletePortfolio,
  getPortfolio,
  getPortfolioTransactions,
  getUserPortfolios,
} from "../api/portfolios";

function getApiUsername(auth) {
  return (
    auth.user?.profile?.["cognito:username"] ||
    auth.user?.profile?.username ||
    auth.user?.profile?.sub ||
    ""
  );
}

function getDisplayUsername(auth) {
  return auth.user?.profile?.email || getApiUsername(auth);
}

function getToken(auth) {
  return auth.user?.id_token || auth.user?.access_token || "";
}

function formatCurrency(value) {
  const amount = Number(value || 0);

  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

export default function DashboardPage() {
  const auth = useAuth();
  const navigate = useNavigate();

  const apiUsername = getApiUsername(auth);
  const displayUsername = getDisplayUsername(auth);
  const token = getToken(auth);

  const [activeTab, setActiveTab] = useState("manage");
  const [user, setUser] = useState(null);
  const [portfolios, setPortfolios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  async function loadDashboard() {
    if (!apiUsername || !token) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setMessage("");
      setAuthToken(token);

      const [userResponse, portfoliosResponse] = await Promise.all([
        getUser(apiUsername),
        getUserPortfolios(apiUsername),
      ]);

      const basePortfolios = portfoliosResponse.data || [];

      const enrichedPortfolios = await Promise.all(
        basePortfolios.map(async (portfolio) => {
          try {
            const [portfolioResponse, transactionsResponse] = await Promise.all([
              getPortfolio(portfolio.id),
              getPortfolioTransactions(portfolio.id),
            ]);

            return {
              ...portfolio,
              ...portfolioResponse.data,
              transactions: transactionsResponse.data || [],
            };
          } catch {
            return {
              ...portfolio,
              transactions: [],
            };
          }
        })
      );

      setUser(userResponse.data);
      setPortfolios(enrichedPortfolios);
    } catch (error) {
      setMessage(getApiErrorMessage(error));
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      setAuthToken(token);
    }
  }, [token]);

  useEffect(() => {
    loadDashboard();
  }, [apiUsername, token]);

  async function handleCreatePortfolio(formData) {
    try {
      setIsSubmitting(true);
      setMessage("");
      setAuthToken(token);

      await createPortfolio({
        username: apiUsername,
        name: formData.name,
        description: formData.description,
      });

      setMessage("Portfolio created successfully.");
      setMessageType("success");
      setActiveTab("manage");
      await loadDashboard();
    } catch (error) {
      setMessage(getApiErrorMessage(error));
      setMessageType("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeletePortfolio(portfolioId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this portfolio?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsDeleting(true);
      setMessage("");
      setAuthToken(token);

      await deletePortfolio(portfolioId);

      setMessage("Portfolio deleted successfully.");
      setMessageType("success");
      await loadDashboard();
    } catch (error) {
      setMessage(getApiErrorMessage(error));
      setMessageType("error");
    } finally {
      setIsDeleting(false);
    }
  }

  function handleLogout() {
    navigate("/logout");
  }

  return (
    <main className="app-shell">
      <section className="app-container">
        <header className="topbar">
          <div>
            <p className="eyebrow">Investment Portfolio Manager</p>
            <h1>Portfolio Dashboard</h1>
            <p className="subtle-text">Signed in as {displayUsername || "Authenticated user"}</p>
          </div>

          <button type="button" className="secondary-button" onClick={handleLogout}>
            Logout
          </button>
        </header>

        <section className="summary-card">
          <p>Available Balance</p>
          <h2>{formatCurrency(user?.balance)}</h2>
        </section>

        <div className="dashboard-tabs">
          <button
            type="button"
            className={activeTab === "create" ? "tab-button active-tab" : "tab-button"}
            onClick={() => setActiveTab("create")}
          >
            Create Portfolio
          </button>

          <button
            type="button"
            className={activeTab === "manage" ? "tab-button active-tab" : "tab-button"}
            onClick={() => setActiveTab("manage")}
          >
            Manage Holdings
          </button>
        </div>

        <AlertMessage type={messageType} message={message} />

        <section className="content-card">
          {activeTab === "create" && (
            <CreatePortfolioForm
              onCreate={handleCreatePortfolio}
              isSubmitting={isSubmitting}
            />
          )}

          {activeTab === "manage" &&
            (isLoading ? (
              <p>Loading portfolios and holdings...</p>
            ) : (
              <PortfolioList
                portfolios={portfolios}
                onDelete={handleDeletePortfolio}
                isDeleting={isDeleting}
              />
            ))}
        </section>
      </section>
    </main>
  );
}
