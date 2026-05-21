import React, { useState } from 'react';

// CORREÇÃO 1: Adicionado 'transporte' para ser recebido via props desestruturadas
export const BasketBuilder = ({ location, transporte, onOptimizationComplete }) => {
  const [items, setItems] = useState([]);
  const [productName, setProductName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [radiusKm, setRadiusKm] = useState(10);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState(null);

  const handleAddItem = (e) => {
    e.preventDefault();
    if (!productName.trim()) return;
    setItems([...items, { product_name: productName.trim(), quantity: Number(quantity) }]);
    setProductName('');
    setQuantity(1);
  };

  const handleRemoveItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setError(null);

    // CORREÇÃO 2: Incluída a propriedade 'transporte' no payload enviado ao Python
    const payload = {
      lat: location.latitude,
      lng: location.longitude,
      raio_km: Number(radiusKm),
      transporte: transporte, // <-- Envia o estado atual dinâmico ('carro' ou 'a_pe')
      itens: items.map(i => ({
        nome: i.product_name,
        quantidade: i.quantity
      }))
    };

    // LOG: O que estamos tentando enviar?
    console.log("DEBUG: Payload sendo enviado:", JSON.stringify(payload, null, 2));

    try {
      const response = await fetch("http://127.0.0.1:8000/optimizer/basket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      // LOG: O servidor respondeu?
      console.log("DEBUG: Status da resposta:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        // LOG: Detalhe do erro
        console.error("DEBUG: Erro detalhado do Backend:", errorText);
        throw new Error(`Erro ${response.status}: ${errorText}`);
      }
      
      const result = await response.json();
      // LOG: O JSON chegou limpo?
      console.log("DEBUG: Resultado do cálculo recebido:", result);
      
      onOptimizationComplete(result);
    } catch (err) {
      console.error("DEBUG: Falha na requisição:", err.message);
      setError(err.message);
    } finally {
      // LOG: Confirmação de encerramento
      console.log("DEBUG: Processo de otimização finalizado.");
      setIsOptimizing(false);
    }
  };

  return (
    <div style={{ padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h3>Monte sua Cesta</h3>
      <div style={{ marginBottom: '10px' }}>
        <label>Raio de busca (km): </label>
        <input 
          type="number" 
          value={radiusKm} 
          onChange={(e) => setRadiusKm(Number(e.target.value))} 
          style={{ width: '60px' }} 
        />
      </div>
      
      <form onSubmit={handleAddItem} style={{ marginBottom: '15px' }}>
        <label htmlFor="productName" style={{ display: 'none' }}>Nome do Produto</label>
        <input 
          id="productName"
          name="productName"
          value={productName} 
          onChange={(e) => setProductName(e.target.value)} 
          placeholder="Ex: Arroz 5kg" 
          style={{ marginRight: '5px' }} 
          required
        />

        <label htmlFor="quantity" style={{ display: 'none' }}>Quantidade</label>
        <input 
          id="quantity"
          name="quantity"
          type="number" 
          min="1"
          value={quantity} 
          onChange={(e) => setQuantity(Number(e.target.value))} 
          style={{ width: '60px', marginRight: '5px' }} 
          required
        />

        <button type="submit">Adicionar</button>
      </form>

      <ul>
        {items.map((i, idx) => (
          <li key={idx}>
            {i.quantity} x {i.product_name}
            <button onClick={() => handleRemoveItem(idx)} style={{ marginLeft: '10px', color: 'red' }}>X</button>
          </li>
        ))}
      </ul>

      <button
        onClick={handleOptimize}
        disabled={isOptimizing || items.length === 0}
        style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
      >
        {isOptimizing ? 'Calculando...' : 'Otimizar Compras'}
      </button>

      {/* Exibição de Erros */}
      {error && <p style={{ color: 'red', marginTop: '10px', fontWeight: 'bold' }}>{error}</p>}
    </div>
  );
};

export default BasketBuilder;