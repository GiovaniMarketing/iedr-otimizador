import { useState } from "react";

export default function BasketForm({ onSubmit }) {
  const [items, setItems] = useState([
    { product_name: "", quantity: 1 }
  ]);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  const add = () => {
    setItems([...items, { product_name: "", quantity: 1 }]);
  };

  const remove = (i) => {
    const copy = [...items];
    copy.splice(i, 1);
    setItems(copy);
  };

  const update = (i, field, value) => {
    const copy = [...items];
    copy[i][field] = value;
    setItems(copy);
  };

  const submit = async () => {
    setLoading(true);
    const payload = {
      lat: -23.62,
      lng: -45.41,
      raio_km: 15,
      itens: items.filter(i => i.product_name.trim())
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/optimizer/basket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      setResultado(data);
      if (onSubmit) onSubmit(data); // Mantém a funcionalidade original
    } catch (error) {
      alert("Erro ao otimizar: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20, border: "1px solid #ddd", maxWidth: "400px" }}>
      <h2>🧺 Cesta Inteligente</h2>

      {items.map((item, i) => (
        <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10 }}>
          <input
            placeholder="Produto"
            value={item.product_name}
            onChange={(e) => update(i, "product_name", e.target.value)}
          />
          <input
            type="number"
            min="1"
            value={item.quantity}
            onChange={(e) => update(i, "quantity", Number(e.target.value))}
          />
          <button onClick={() => remove(i)}>❌</button>
        </div>
      ))}

      <button onClick={add}>➕ Adicionar</button>
      <button onClick={submit} style={{ marginLeft: 10, backgroundColor: "#007bff", color: "white" }}>
        {loading ? "Calculando..." : "🚀 Otimizar"}
      </button>

      {/* Exibição do Vencedor */}
      {resultado && (
        <div style={{ marginTop: 20, padding: 15, backgroundColor: "#e8f5e9", borderRadius: "8px" }}>
          <h3 style={{ color: "#2e7d32", margin: 0 }}>🏆 Melhor Opção: {resultado.best_market}</h3>
          <p style={{ fontSize: "1.2em", fontWeight: "bold" }}>Total: R$ {resultado.lowest_total_price.toFixed(2)}</p>
          <small>Mercados consultados: {resultado.markets_used}</small>
        </div>
      )}
    </div>
  );
}