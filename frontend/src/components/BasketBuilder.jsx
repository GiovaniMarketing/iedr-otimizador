import React, { useState } from 'react';
import { StorageService } from '../services/storageService';

export const BasketBuilder = ({ location, onOptimizationComplete }) => {
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

  const handleRemoveItem = (indexToRemove) => {
    setItems(items.filter((_, index) => index !== indexToRemove));
  };

  // FUNÇÃO DE OTIMIZAÇÃO CONSOLIDADA (Ação Nacional + Capitalização)
  const handleOptimize = async () => {
    setIsOptimizing(true);
    setError(null);

    // 1. Captura localização precisa para o raio de busca
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const coords = { 
        latitude: pos.coords.latitude, 
        longitude: pos.coords.longitude 
      };

      // 2. Monta o contrato exato para o Backend
      const payload = {
        ...coords,
        radius_km: Number(radiusKm),
        items: items
      };

      try {
        // 3. Chama o serviço de API
        const { optimizeBasketRequest } = await import('../services/api');
        const result = await optimizeBasketRequest(payload);
        
        // 4. GRAVA NO AMBIENTE DO CLIENTE (Histórico Local)
        if (result) {
          await StorageService.saveHistory(result);
          onOptimizationComplete(result); // Atualiza a tela com o resultado
        }
      } catch (err) {
        setError("Erro ao conectar com o serviço de otimização.");
        console.error(err);
      } finally {
        setIsOptimizing(false);
      }
    }, (geoErr) => {
      setError("Por favor, ative o GPS para encontrar mercados próximos.");
      setIsOptimizing(false);
    });
  };

  return (
    <div className="basket-builder">
      <h3>Monte sua Cesta</h3>
      
      <div className="radius-config">
        <label>Raio de busca (km): </label>
        <input 
          type="number" 
          value={radiusKm} 
          onChange={(e) => setRadiusKm(e.target.value)} 
          min="1" max="200"
        />
      </div>

      <form onSubmit={handleAddItem} className="add-item-form">
        <input
          type="text"
          placeholder="Ex: Arroz 5kg"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
        />
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          style={{ width: '60px', marginLeft: '10px' }}
        />
        <button type="submit" style={{ marginLeft: '10px' }}>Adicionar</button>
      </form>

      <ul className="item-list">
        {items.map((item, index) => (
          <li key={index}>
            {item.quantity}x {item.product_name}
            <button onClick={() => handleRemoveItem(index)} style={{ marginLeft: '10px', color: 'red' }}>X</button>
          </li>
        ))}
      </ul>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <button 
        onClick={handleOptimize} 
        disabled={isOptimizing || items.length === 0}
        style={{ marginTop: '20px', padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
      >
        {isOptimizing ? 'Calculando a melhor rota...' : 'Otimizar Compras'}
      </button>
    </div>
  );
};