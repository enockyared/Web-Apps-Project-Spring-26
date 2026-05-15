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

export default function HoldingsTable({
  holdings,
  selectedTicker,
  onSelectHolding,
  transactions = [],
}) {
  if (!holdings || holdings.length === 0) {
    return <p className="empty-state">No holdings found for this portfolio.</p>;
  }

  return (
    <section>
      <h2>Holdings</h2>

      <table className="data-table">
        <thead>
          <tr>
            <th>Holding</th>
            <th>Shares Held</th>
            <th>Position Value</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {holdings.map((holding, index) => {
            const ticker = getTicker(holding);
            const sharesHeld = getQuantity(holding);
            const averageBuyPrice = getAverageBuyPrice(ticker, transactions);
            const positionValue =
              averageBuyPrice === null ? null : sharesHeld * averageBuyPrice;
            const isSelected = selectedTicker === ticker;

            return (
              <tr
                key={holding.id || `${ticker}-${index}`}
                className={isSelected ? "selected-row" : ""}
              >
                <td>
                  <button
                    type="button"
                    className="holding-link"
                    onClick={() => onSelectHolding(holding)}
                  >
                    {ticker}
                  </button>
                </td>

                <td>{sharesHeld}</td>
                <td>{formatCurrency(positionValue)}</td>

                <td>
                  <button
                    type="button"
                    className={isSelected ? "secondary-button" : ""}
                    onClick={() => onSelectHolding(holding)}
                  >
                    {isSelected ? "Selected" : "Buy / Sell"}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
