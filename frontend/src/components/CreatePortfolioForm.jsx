import { useState } from "react";

export default function CreatePortfolioForm({ onCreate, isSubmitting }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    await onCreate({
      name: name.trim(),
      description: description.trim(),
    });

    setName("");
    setDescription("");
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Create Portfolio</h2>

      <label>
        Portfolio Name
        <input
          type="text"
          value={name}
          required
          onChange={(event) => setName(event.target.value)}
          placeholder="Growth Portfolio"
        />
      </label>

      <label>
        Description
        <textarea
          value={description}
          required
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Long-term growth investments"
        />
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create Portfolio"}
      </button>
    </form>
  );
}
