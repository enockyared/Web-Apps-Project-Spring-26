import { useState } from "react";

export default function BuyOrderForm({ onBuy, isSubmitting }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    await onBuy({
      ticker: ticker.trim().toUpperCase(),
      quantity: Number(quantity),
    });

    setTicker("");
    setQuantity("");
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Buy Security</h2>

      <label>
        Ticker Symbol
        <input
          type="text"
          value={ticker}
          required
          onChange={(event) => setTicker(event.target.value)}
          placeholder="AAPL"
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
          placeholder="5"
        />
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Buying..." : "Place Buy Order"}
      </button>
    </form>
  );
}