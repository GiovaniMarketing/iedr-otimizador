import React, { useState, useEffect } from 'react';
import { useUserLocation } from './hooks/useUserLocation';
import { LocationFallback } from './components/LocationFallback';
import { BasketBuilder } from './components/BasketBuilder';

function App() {
  const { location, isLoading: isLocating, error: locationError, requestLocation, setManualLocation } = useUserLocation();
  const [optimizationResult, setOptimizationResult] = useState(null);

  // Tenta pegar o GPS nativo assim que o app abre
  useEffect(() => {
    requestLocation();
  }, [requestLocation]);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>🛒 IEDR - Otimizador de Compras</h1>

      {/* BLOCO 1: GEOLOCALIZAÇÃO */}
      <section style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2>1. Sua Localização</h2>
        
        {isLocating && <p>Buscando sinal de GPS...</p>}
        
        {locationError && !location && (
          <LocationFallback onLocationFound={setManualLocation} />
        )}

        {location && (
          <p style={{ color: 'green' }}>
            ✅ Localização definida! (Lat: {location.latitude.toFixed(4)}, Lng: {location.longitude.toFixed(4)})
          </p>
        )}
      </section>

      {/* BLOCO 2: CESTA E OTIMIZAÇÃO */}
      {location && !optimizationResult && (
        <section style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <BasketBuilder 
            location={location} 
            onOptimizationComplete={(data) => setOptimizationResult(data)} 
          />
        </section>
      )}

      {/* BLOCO 3: RESULTADOS COM CÁLCULO DE VIABILIDADE */}
      {optimizationResult && (
        <section style={{ padding: '20px', border: '2px solid #28a745', borderRadius: '8px', backgroundColor: '#f0fff0', marginTop: '20px' }}>
          <h2>✨ Otimização Concluída!</h2>
          
          {/* CÁLCULO INTELIGENTE DE VIABILIDADE */}
          {(() => {
            const custoPorKm = 0.50; // Estimativa de custo de combustível/desgaste (R$ 0,50 por km)
            const custoDeslocamento = optimizationResult.total_distance * custoPorKm;
            const economiaBruta = optimizationResult.estimated_savings || 0;
            const economiaReal = economiaBruta - custoDeslocamento;
            const valeAPena = economiaReal > 0;

            return (
              <div style={{ 
                marginBottom: '20px', 
                padding: '15px', 
                backgroundColor: valeAPena ? '#d4edda' : '#f8d7da', 
                border: `1px solid ${valeAPena ? '#c3e6cb' : '#f5c6cb'}`,
                borderRadius: '8px' 
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: valeAPena ? '#155724' : '#721c24' }}>
                  {valeAPena ? '✅ Vale a pena o deslocamento!' : '❌ O deslocamento dá prejuízo.'}
                </h3>
                <p style={{ margin: '5px 0', color: '#333' }}>
                  Economia nos Produtos: <strong>+ R$ {economiaBruta.toFixed(2)}</strong>
                </p>
                <p style={{ margin: '5px 0', color: '#333' }}>
                  Custo Est. de Combustível (R$0,50/km): <strong style={{ color: 'red' }}>- R$ {custoDeslocamento.toFixed(2)}</strong>
                </p>
                <hr style={{ borderColor: valeAPena ? '#c3e6cb' : '#f5c6cb', margin: '10px 0' }} />
                <p style={{ margin: '0', fontSize: '18px', fontWeight: 'bold', color: valeAPena ? '#155724' : '#721c24' }}>
                  Saldo Final: R$ {economiaReal.toFixed(2)}
                </p>
              </div>
            );
          })()}

          <p><strong>Total da Cesta:</strong> R$ {optimizationResult.total_price.toFixed(2)}</p>
          <p><strong>Distância Percorrida:</strong> {optimizationResult.total_distance.toFixed(2)} km</p>
          <p><strong>Mercados Visitados:</strong> {optimizationResult.markets_used}</p>
          
          <h3 style={{ marginTop: '25px', borderBottom: '2px solid #ccc', paddingBottom: '5px' }}>🛒 Onde Comprar:</h3>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {optimizationResult.items.map((item, index) => (
              <li key={index} style={{ 
                backgroundColor: '#fff', 
                border: '1px solid #ddd', 
                borderRadius: '5px', 
                padding: '15px', 
                marginBottom: '10px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
              }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>
                  {item.quantity}x {item.matched_product}
                </div>
                <div style={{ color: '#555', marginBottom: '5px' }}>
                  📍 <strong>{item.market_name}</strong> (a {item.distance_km.toFixed(2)} km de você)
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', color: '#0056b3' }}>
                  <span>Unidade: R$ {item.unit_price.toFixed(2)}</span>
                  <strong>Total: R$ {item.total_price.toFixed(2)}</strong>
                </div>
              </li>
            ))}
          </ul>
          
          <button 
            onClick={() => setOptimizationResult(null)}
            style={{ marginTop: '20px', padding: '10px 20px', width: '100%', fontSize: '16px', backgroundColor: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Fazer Nova Busca
          </button>
        </section>
      )}
    </div>
  );
}

// O ERRO ERA A FALTA DESTA LINHA ABAIXO:
export default App;