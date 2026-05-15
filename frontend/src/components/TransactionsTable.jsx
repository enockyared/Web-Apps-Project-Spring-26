function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "N/A";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
}

function formatCurrency(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "N/A";
  }

  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

export default function TransactionsTable({ transactions }) {
  if (!transactions || transactions.length === 0) {
    return <p className="empty-state">No transactions found for this portfolio.</p>;
  }

  function getTicker(transaction) {
    return (
      transaction.ticker ||
      transaction.security_ticker ||
      transaction.symbol ||
      transaction.security?.ticker ||
      "N/A"
    );
  }

  function getType(transaction) {
    return (
      transaction.transaction_type ||
      transaction.type ||
      transaction.transactionType ||
      "N/A"
    );
  }

  function getPrice(transaction) {
    return transaction.price ?? transaction.transaction_price;
  }

  function getTimestamp(transaction) {
    return (
      transaction.timestamp ||
      transaction.created_at ||
      transaction.transaction_date ||
      transaction.date
    );
  }

  return (
    <section>
      <h2>Transaction History</h2>

      <table className="data-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Type</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction, index) => (
            <tr key={transaction.id || `${getTicker(transaction)}-${index}`}>
              <td>{getTicker(transaction)}</td>
              <td>
                <span className={`status-pill ${String(getType(transaction)).toLowerCase()}`}>
                  {getType(transaction)}
                </span>
              </td>
              <td>{transaction.quantity ?? "N/A"}</td>
              <td>{formatCurrency(getPrice(transaction))}</td>
              <td>{formatTimestamp(getTimestamp(transaction))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
