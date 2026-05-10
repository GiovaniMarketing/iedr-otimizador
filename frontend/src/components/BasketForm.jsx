import { useState } from "react";

export default function BasketForm({ onSubmit }) {

  const [items, setItems] = useState([
    { product_name: "", quantity: 1 }
  ]);

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

  const submit = () => {
    onSubmit({
      latitude: -23.62,
      longitude: -45.41,
      radius_km: 15,
      items: items.filter(i => i.product_name.trim())
    });
  };

  return (
    <div style={{ padding: 20, border: "1px solid #ddd" }}>

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

      <button onClick={submit} style={{ marginLeft: 10 }}>
        🚀 Otimizar
      </button>

    </div>
  );
}