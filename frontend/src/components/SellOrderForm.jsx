import { useState } from "react";

export default function SellOrderForm({ onSell, isSubmitting }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    await onSell({
      ticker: ticker.trim().toUpperCase(),
      quantity: Number(quantity),
    });

    setTicker("");
    setQuantity("");
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Sell Security</h2>

      <label>
        Ticker Symbol
        <input
          type="text"
          value={ticker}
          required
          onChange={(event) => setTicker(event.target.value)}
          placeholder="IBM"
        />
      </label>

      <label>
        Quantity
        <input
          type="number"
          min="1"
          step="1"
          value={quantity}
          required
          onChange={(event) => setQuantity(event.target.value)}
          placeholder="1"
        />
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Selling..." : "Place Sell Order"}
      </button>
    </form>
  );
}