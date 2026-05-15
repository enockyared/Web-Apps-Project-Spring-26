import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import AlertMessage from "../components/AlertMessage";
import BuyOrderForm from "../components/BuyOrderForm";
import HoldingsTable from "../components/HoldingsTable";
import TransactionsTable from "../components/TransactionsTable";
import { getApiErrorMessage, setAuthToken } from "../api/client";
import { getUser } from "../api/users";
import {
  getPortfolio,
  getPortfolioTransactions,
} from "../api/portfolios";
import { buySecurity, sellSecurity } from "../api/trades";

function getApiUsername(auth) {
  return (
    auth.user?.profile?.["cognito:username"] ||
    auth.user?.profile?.username ||
    auth.user?.profile?.sub ||
    ""
  );
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

function getFriendlyTradeError(error, fallbackMessage) {
  const detail =
    error.response?.data?.detail ||
    error.response?.data?.error ||
    error.message ||
    "";

  if (
    detail.includes("Alpha Vantage") ||
    detail.includes("Unable to retrieve current market price") ||
    detail.includes("Invalid ticker") ||
    detail.includes("Error Message") ||
    detail.includes("Time Series") ||
    detail.includes("Global Quote")
  ) {
    return "Please enter a valid ticker symbol.";
  }

  return detail || fallbackMessage;
}

function getHoldingTicker(holding) {
  return (
    holding?.ticker ||
    holding?.security_ticker ||
    holding?.symbol ||
    holding?.security?.ticker ||
    ""
  );
}


function getAverageBuyPrice(ticker, transactions = []) {
  const buys = transactions.filter((transaction) => {
    const transactionTicker =
      transaction.ticker ||
      transaction.security_ticker ||
      transaction.symbol ||
      transaction.security?.ticker;

    const type =
      transaction.transaction_type ||
      transaction.type ||
      transaction.transactionType;

    return (
      transactionTicker === ticker &&
      String(type || "").toUpperCase() === "BUY"
    );
  });

  const totalQuantity = buys.reduce(
    (sum, transaction) => sum + Number(transaction.quantity || 0),
    0
  );

  const totalCost = buys.reduce((sum, transaction) => {
    const price = Number(transaction.price || transaction.transaction_price || 0);
    const quantity = Number(transaction.quantity || 0);

    return sum + price * quantity;
  }, 0);

  if (!totalQuantity) {
    return null;
  }

  return totalCost / totalQuantity;
}

function getHoldingQuantity(holding) {
  return Number(holding?.quantity ?? 0);
}

export default function PortfolioDetailPage() {
  const { portfolioId } = useParams();
  const location = useLocation();
  const auth = useAuth();
  const apiUsername = getApiUsername(auth);
  const token = getToken(auth);

  const [user, setUser] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [selectedSellQuantity, setSelectedSellQuantity] = useState("");
  const [selectedBuyQuantity, setSelectedBuyQuantity] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isBuying, setIsBuying] = useState(false);
  const [isSelling, setIsSelling] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  async function loadPortfolioDetails() {
    if (!portfolioId || !token || !apiUsername) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setMessage("");
      setAuthToken(token);

      const [userResponse, portfolioResponse, transactionsResponse] =
        await Promise.all([
          getUser(apiUsername),
          getPortfolio(portfolioId),
          getPortfolioTransactions(portfolioId),
        ]);

      const fullPortfolio = portfolioResponse.data;
      const holdings = fullPortfolio.investments || fullPortfolio.holdings || [];

      setUser(userResponse.data);
      setPortfolio(fullPortfolio);
      setTransactions(transactionsResponse.data || []);

      const holdingFromQuery = new URLSearchParams(location.search).get("holding");

      if (holdingFromQuery) {
        const matchedHolding = holdings.find(
          (holding) => getHoldingTicker(holding) === holdingFromQuery
        );

        if (matchedHolding) {
          setSelectedHolding(matchedHolding);
        }
      }
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
    loadPortfolioDetails();
  }, [portfolioId, token, apiUsername, location.search]);

  async function handleBuyOrder(formData) {
    try {
      setIsBuying(true);
      setMessage("");
      setAuthToken(token);

      await buySecurity({
        portfolio_id: Number(portfolioId),
        ticker: formData.ticker,
        quantity: formData.quantity,
      });

      setMessage("Buy order placed successfully.");
      setMessageType("success");
      await loadPortfolioDetails();
    } catch (error) {
      setMessage(
        getFriendlyTradeError(
          error,
          "Unable to place buy order. Please try again."
        )
      );
      setMessageType("error");
    } finally {
      setIsBuying(false);
    }
  }

  async function handleSelectedHoldingBuy() {
    const ticker = getHoldingTicker(selectedHolding);
    const quantity = Number(selectedBuyQuantity);

    if (!ticker || !quantity || quantity <= 0) {
      setMessage("Please enter a valid buy quantity.");
      setMessageType("error");
      return;
    }

    await handleBuyOrder({
      ticker,
      quantity,
    });

    setSelectedBuyQuantity("");
  }

  async function handleSelectedHoldingSell(quantityToSell) {
    const ticker = getHoldingTicker(selectedHolding);
    const quantity = Number(quantityToSell);

    if (!ticker || !quantity || quantity <= 0) {
      setMessage("Please enter a valid sell quantity.");
      setMessageType("error");
      return;
    }

    try {
      setIsSelling(true);
      setMessage("");
      setAuthToken(token);

      await sellSecurity({
        portfolio_id: Number(portfolioId),
        ticker,
        quantity,
      });

      setMessage("Sell order placed successfully.");
      setMessageType("success");
      setSelectedSellQuantity("");
      await loadPortfolioDetails();
    } catch (error) {
      setMessage(
        getFriendlyTradeError(
          error,
          "Unable to place sell order. Please try again."
        )
      );
      setMessageType("error");
    } finally {
      setIsSelling(false);
    }
  }

  function handleSelectHolding(holding) {
    setSelectedHolding(holding);
    setSelectedSellQuantity("");
    setSelectedBuyQuantity("");
    setMessage("");
  }

  const holdings = portfolio?.investments || portfolio?.holdings || [];
  const selectedTicker = getHoldingTicker(selectedHolding);
  const selectedQuantity = getHoldingQuantity(selectedHolding);
  const selectedAverageBuyPrice = getAverageBuyPrice(selectedTicker, transactions);
  const selectedPositionValue =
    selectedAverageBuyPrice === null
      ? null
      : selectedQuantity * selectedAverageBuyPrice;

  return (
    <main className="app-shell">
      <section className="app-container">
        <header className="topbar">
          <div>
            <p className="eyebrow">Portfolio Detail</p>
            <h1>{portfolio?.name || "Portfolio Detail"}</h1>
            <p className="subtle-text">{portfolio?.description || `Portfolio ID: ${portfolioId}`}</p>
          </div>

          <Link className="primary-link-button" to="/">
            Back to Dashboard
          </Link>
        </header>

        <section className="summary-card">
          <p>Available Balance</p>
          <h2>{formatCurrency(user?.balance)}</h2>
        </section>

        <AlertMessage type={messageType} message={message} />

        <section className="content-card">
          {isLoading ? (
            <p>Loading portfolio details...</p>
          ) : (
            <>
              <HoldingsTable
                holdings={holdings}
                selectedTicker={selectedTicker}
                onSelectHolding={handleSelectHolding}
                transactions={transactions}
              />

              {selectedHolding && (
                <section className="selected-holding-card">
                  <div>
                    <h2>{selectedTicker} Buy / Sell</h2>
                    <p>
                      Shares Held: <strong>{selectedQuantity}</strong>
                    </p>
                    <p>
                      Position Value: <strong>{formatCurrency(selectedPositionValue)}</strong>
                    </p>
                    <p>
                      Available Balance:{" "}
                      <strong>{formatCurrency(user?.balance)}</strong>
                    </p>
                  </div>

                  <div className="trade-panel-grid">
                    <div className="mini-trade-panel">
                      <h3>Buy More {selectedTicker}</h3>
                      <label>
                        Quantity to Buy
                        <input
                          type="number"
                          min="1"
                          step="1"
                          value={selectedBuyQuantity}
                          onChange={(event) =>
                            setSelectedBuyQuantity(event.target.value)
                          }
                          placeholder="Qty"
                        />
                      </label>

                      <button
                        type="button"
                        disabled={isBuying}
                        onClick={handleSelectedHoldingBuy}
                      >
                        {isBuying ? "Buying..." : `Buy ${selectedTicker}`}
                      </button>
                    </div>

                    <div className="mini-trade-panel">
                      <h3>Sell {selectedTicker}</h3>
                      <label>
                        Quantity to Sell
                        <input
                          type="number"
                          min="1"
                          max={selectedQuantity}
                          step="1"
                          value={selectedSellQuantity}
                          onChange={(event) =>
                            setSelectedSellQuantity(event.target.value)
                          }
                          placeholder="Qty"
                        />
                      </label>

                      <div className="table-actions">
                        <button
                          type="button"
                          disabled={isSelling}
                          onClick={() =>
                            handleSelectedHoldingSell(selectedSellQuantity)
                          }
                        >
                          {isSelling ? "Selling..." : "Sell Quantity"}
                        </button>

                        <button
                          type="button"
                          className="danger-button"
                          disabled={isSelling}
                          onClick={() => handleSelectedHoldingSell(selectedQuantity)}
                        >
                          Liquidate All
                        </button>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              <div className="form-grid single-form">
                <BuyOrderForm onBuy={handleBuyOrder} isSubmitting={isBuying} />
              </div>

              <TransactionsTable transactions={transactions} />
            </>
          )}
        </section>
      </section>
    </main>
  );
}
