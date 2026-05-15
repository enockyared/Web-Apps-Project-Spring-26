import { Link } from "react-router-dom";

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "N/A";
  }

  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

function getTicker(holding) {
  return (
    holding.ticker ||
    holding.security_ticker ||
    holding.symbol ||
    holding.security?.ticker ||
    "N/A"
  );
}

function getQuantity(holding) {
  return Number(holding.quantity ?? 0);
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

function HoldingSummaryTable({ portfolio }) {
  const holdings = portfolio.investments || portfolio.holdings || [];
  const transactions = portfolio.transactions || [];

  if (!holdings.length) {
    return <p className="empty-state">No holdings currently in this portfolio.</p>;
  }

  return (
    <table className="data-table compact-table">
      <thead>
        <tr>
          <th>Holding</th>
          <th>Shares Held</th>
          <th>Position Value</th>
          <th>Manage</th>
        </tr>
      </thead>

      <tbody>
        {holdings.map((holding, index) => {
          const ticker = getTicker(holding);
          const sharesHeld = getQuantity(holding);
          const averageBuyPrice = getAverageBuyPrice(ticker, transactions);
          const positionValue =
            averageBuyPrice === null ? null : sharesHeld * averageBuyPrice;

          return (
            <tr key={holding.id || `${ticker}-${index}`}>
              <td>
                <Link
                  className="holding-link"
                  to={`/portfolios/${portfolio.id}?holding=${ticker}`}
                >
                  {ticker}
                </Link>
              </td>
              <td>{sharesHeld}</td>
              <td>{formatCurrency(positionValue)}</td>
              <td>
                <Link
                  className="small-action-link"
                  to={`/portfolios/${portfolio.id}?holding=${ticker}`}
                >
                  Buy / Sell
                </Link>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default function PortfolioList({ portfolios, onDelete, isDeleting }) {
  if (!portfolios.length) {
    return <p className="empty-state">No portfolios found. Create one to get started.</p>;
  }

  return (
    <section>
      <h2>Manage Holdings</h2>

      <div className="portfolio-grid">
        {portfolios.map((portfolio) => {
          const holdings = portfolio.investments || portfolio.holdings || [];
          const transactions = portfolio.transactions || [];

          const totalSharesHeld = holdings.reduce(
            (sum, holding) => sum + getQuantity(holding),
            0
          );

          const totalPositionValue = holdings.reduce((sum, holding) => {
            const ticker = getTicker(holding);
            const sharesHeld = getQuantity(holding);
            const averageBuyPrice = getAverageBuyPrice(ticker, transactions);

            if (averageBuyPrice === null) {
              return sum;
            }

            return sum + sharesHeld * averageBuyPrice;
          }, 0);

          return (
            <article className="portfolio-card" key={portfolio.id}>
              <div className="portfolio-card-header">
                <div>
                  <h3>{portfolio.name}</h3>
                  <p>{portfolio.description}</p>

                  <div className="metric-row">
                    <p className="metric-pill">
                      Shares Held: <strong>{totalSharesHeld}</strong>
                    </p>

                    <p className="metric-pill">
                      Position Value: <strong>{formatCurrency(totalPositionValue)}</strong>
                    </p>
                  </div>
                </div>

                <Link className="primary-link-button" to={`/portfolios/${portfolio.id}`}>
                  Manage Holdings
                </Link>
              </div>

              <HoldingSummaryTable portfolio={portfolio} />

              <div className="portfolio-actions">
                <button
                  type="button"
                  className="danger-button"
                  disabled={isDeleting}
                  onClick={() => onDelete(portfolio.id)}
                >
                  Delete Portfolio
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
