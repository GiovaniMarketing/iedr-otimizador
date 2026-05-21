import React, { useState, useEffect, useCallback } from 'react';
import { useUserLocation } from './hooks/useUserLocation';
import { LocationFallback } from './components/LocationFallback';
import { BasketBuilder } from './components/BasketBuilder';

function App() {
  const { location: geoLocation, isLoading: isLocating, error: locationError, requestLocation } = useUserLocation();
  const [optimizationResult, setOptimizationResult] = useState(null);
  
  // Estados para controle de localização e endereço por extenso
  const [location, setLocation] = useState(null);
  const [readableAddress, setReadableAddress] = useState('Buscando endereço...');
  const [isWrongCity, setIsWrongCity] = useState(false);
  
  // Estados para controle do formulário de CEP
  const [cep, setCep] = useState('');
  const [isSearchingCep, setIsSearchingCep] = useState(false);
  const [cepError, setCepError] = useState(null);
  const [isManualMode, setIsManualMode] = useState(false);
  const [transporte, setTransporte] = useState('carro');

  // Função para descobrir o endereço real a partir de coordenadas (Geocoding Reverso)
  const fetchAddressFromCoords = useCallback(async (lat, lng) => {
    try {
      setReadableAddress('Identificando rua e cidade...');
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`);
      const data = await res.json();
      
      if (data && data.address) {
        const addr = data.address;
        const road = addr.road || addr.suburb || addr.neighbourhood || '';
        const city = addr.city || addr.town || addr.municipality || addr.village || 'Desconhecida';
        const state = (addr.state_code || addr.state || 'BR').toUpperCase();
        
        if (road) {
          setReadableAddress(`${road}, ${city} - ${state}`);
          setIsWrongCity(false);
        } else {
          setReadableAddress(`${city} - ${state} (Localização aproximada)`);
          setIsWrongCity(true);
        }
      } else {
        setReadableAddress('Endereço não identificado no mapa.');
        setIsWrongCity(true);
      }
    } catch (err) {
      setReadableAddress('Não foi possível carregar o endereço.');
    }
  }, []);

  // Converte o CEP digitado manualmente em coordenadas reais
  const handleCepSubmit = async (e) => {
    e.preventDefault();
    const cleanCep = cep.replace(/\D/g, '');
    if (cleanCep.length !== 8) {
      setCepError('Digite um CEP válido com 8 dígitos.');
      return;
    }

    setIsSearchingCep(true);
    setCepError(null);
    setReadableAddress('Buscando endereço do CEP...');

    try {
      const viaCepRes = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const viaCepData = await viaCepRes.json();

      if (viaCepData.erro) {
        throw new Error('CEP não encontrado na base dos Correios.');
      }

      const query = `${viaCepData.logradouro}, ${viaCepData.bairro}, ${viaCepData.localidade}, Brazil`;
      const osmRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
      const osmData = await osmRes.json();

      if (osmData && osmData.length > 0) {
        const newLat = parseFloat(osmData[0].lat);
        const newLng = parseFloat(osmData[0].lon);
        
        setIsManualMode(true);
        setLocation({ latitude: newLat, longitude: newLng });
        setReadableAddress(`${viaCepData.logradouro || viaCepData.bairro}, ${viaCepData.localidade} - ${viaCepData.uf}`);
        setIsWrongCity(false); 
      } else {
        const queryFallback = `${viaCepData.bairro}, ${viaCepData.localidade}, Brazil`;
        const osmResFallback = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryFallback)}&limit=1`);
        const osmDataFallback = await osmResFallback.json();
        
        if (osmDataFallback && osmDataFallback.length > 0) {
          const newLatFb = parseFloat(osmDataFallback[0].lat);
          const newLngFb = parseFloat(osmDataFallback[0].lon);
          
          setIsManualMode(true);
          setLocation({ latitude: newLatFb, longitude: newLngFb });
          setReadableAddress(`${viaCepData.bairro}, ${viaCepData.localidade} - ${viaCepData.uf}`);
          setIsWrongCity(false);
        } else {
          throw new Error('Não foi possível obter as coordenadas para este CEP.');
        }
      }
    } catch (err) {
      setCepError(err.message || 'Erro ao processar a busca do CEP.');
      setReadableAddress('Erro ao fixar endereço.');
    } finally {
      setIsSearchingCep(false);
    }
  };

  const handleResetLocation = () => {
    setIsManualMode(false);
    setCep('');
    setReadableAddress('Buscando endereço...');
    if (geoLocation) {
      setLocation(geoLocation);
      fetchAddressFromCoords(geoLocation.latitude, geoLocation.longitude);
    }
  };

  const comparativo = optimizationResult?.comparativo || [];
  const melhorMercado = comparativo[0] || {};
  const totalProdutosCesta = melhorMercado?.total_produtos || 0;
  const custoDeslocamento = transporte === 'a_pe' ? 0.0 : (melhorMercado?.distancia || 0) * 0.50;
  const custoTotalFinal = melhorMercado?.custo_total_final || 0;

  return (
    <div style={{ 
      maxWidth: '1000px', 
      margin: '40px auto', 
      padding: '30px', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      backgroundColor: '#fecdd3', // Fundo Rose/Goiaba chamativo que destaca os elementos brancos
      borderRadius: '20px',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
      border: '4px solid #e11d48' // Borda forte vermelha estilo varejo de ofertas
    }}>
      
      {/* CABEÇALHO */}
      <header style={{ 
        textAlign: 'center', 
        marginBottom: '35px',
        backgroundColor: '#fff',
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 4px 10px rgba(0,0,0,0.05)'
      }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: '900', 
          color: '#be123c', 
          margin: '0 0 5px 0',
          letterSpacing: '-1px',
          textTransform: 'uppercase'
        }}>
          🔥 OTIMIZADOR DE COMPRAS SUPREMO 🔥
        </h1>
        <p style={{ color: '#4c0519', fontSize: '16px', margin: 0, fontWeight: '700' }}>
          Quem pesquisa, economiza! Encontre a combinação mais barata da região
        </p>
      </header>

      {/* PAINEL CONFIGURAÇÃO DE LOCALIZAÇÃO */}
      <section style={{ 
        backgroundColor: '#ffffff', 
        padding: '24px', 
        borderRadius: '12px', 
        boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
        border: '1px solid #fda4af',
        marginBottom: '25px'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#9f1239', margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
          📍 1. Onde você está?
        </h2>
        
        {location && (
          <div style={{ 
            backgroundColor: '#fff1f2', 
            padding: '16px', 
            borderRadius: '8px', 
            marginBottom: '20px', 
            border: '1px solid #ffe4e6' 
          }}>
            <p style={{ color: '#e11d48', fontWeight: '800', margin: '0 0 6px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {isManualMode ? 'Endereço Fixado por CEP:' : 'Endereço Identificado via GPS:'}
            </p>
            <p style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: '700', color: '#0f172a', lineHeight: '1.4' }}>
              {readableAddress}
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
              <span style={{ fontSize: '11px', color: '#9f1239', fontFamily: 'monospace', fontWeight: 'bold' }}>
                GPS: {location.latitude?.toFixed(5)}, {location.longitude?.toFixed(5)}
              </span>
              {isManualMode && (
                <button 
                  onClick={handleResetLocation} 
                  style={{ 
                    fontSize: '12px', 
                    padding: '6px 12px', 
                    cursor: 'pointer',
                    backgroundColor: '#fff',
                    border: '2px solid #f43f5e',
                    color: '#e11d48',
                    borderRadius: '6px',
                    fontWeight: '800',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}
                >
                  🔄 Usar GPS Automático
                </button>
              )}
            </div>
          </div>
        )}

        {/* MEIO DE TRANSPORTE */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '14px', fontWeight: '800', color: '#4c0519' }}>
            🚶‍♂️ Escolha o Meio de Deslocamento:
          </label>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              type="button"
              onClick={() => setTransporte('carro')}
              style={{ 
                flex: 1, 
                padding: '12px 16px', 
                cursor: 'pointer', 
                borderRadius: '8px', 
                fontWeight: '800',
                fontSize: '14px',
                border: transporte === 'carro' ? '3px solid #dc2626' : '1px solid #cbd5e1',
                backgroundColor: transporte === 'carro' ? '#fef2f2' : '#ffffff',
                color: transporte === 'carro' ? '#991b1b' : '#64748b',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: transporte === 'carro' ? '0 4px 10px rgba(220,38,38,0.15)' : 'none'
              }}
            >
              🚗 Carro ou Moto <span style={{fontSize: '11px', fontWeight: 'bold'}}>(+ Combustível)</span>
            </button>
            <button 
              type="button"
              onClick={() => setTransporte('a_pe')}
              style={{ 
                flex: 1, 
                padding: '12px 16px', 
                cursor: 'pointer', 
                borderRadius: '8px', 
                fontWeight: '800',
                fontSize: '14px',
                border: transporte === 'a_pe' ? '3px solid #16a34a' : '1px solid #cbd5e1',
                backgroundColor: transporte === 'a_pe' ? '#f0fdf4' : '#ffffff',
                color: transporte === 'a_pe' ? '#166534' : '#64748b',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: transporte === 'a_pe' ? '0 4px 10px rgba(22,163,74,0.15)' : 'none'
              }}
            >
              🚶‍♂️ Vou a Pé / Bicicleta <span style={{fontSize: '11px', fontWeight: 'bold'}}>(Grátis)</span>
            </button>
          </div>
        </div>

        {/* FORMULÁRIO DE CEP */}
        <form onSubmit={handleCepSubmit} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '15px', paddingTop: '15px', borderTop: '1px dashed #f43f5e', flexWrap: 'wrap' }}>
          <label style={{ fontSize: '14px', fontWeight: '700', color: '#4c0519' }}>
            Quer mudar o CEP? Digite aqui:
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="00000-000" 
              value={cep} 
              onChange={(e) => setCep(e.target.value)}
              style={{ width: '120px', padding: '8px 12px', borderRadius: '6px', border: '2px solid #f43f5e', fontSize: '14px', outline: 'none', fontWeight: 'bold' }}
              disabled={isSearchingCep}
            />
            <button type="submit" style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#e11d48', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: '800', fontSize: '13px', boxShadow: '0 2px 6px rgba(225,29,72,0.2)' }} disabled={isSearchingCep}>
              {isSearchingCep ? 'Buscando...' : 'Buscar CEP'}
            </button>
          </div>
          {cepError && <p style={{ color: '#dc2626', margin: 0, fontSize: '13px', width: '100%', fontWeight: 'bold' }}>❌ {cepError}</p>}
        </form>
      </section>

      {/* PAINEL SELEÇÃO DA CESTA */}
      {location && !optimizationResult && (
        <section style={{ 
          backgroundColor: '#ffffff', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
          border: '1px solid #fda4af'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#9f1239', margin: '0 0 15px 0' }}>
            🛒 2. Monte sua Lista de Produtos
          </h2>
          <BasketBuilder 
            location={location} 
            transporte={transporte} 
            onOptimizationComplete={(data) => setOptimizationResult(data)} 
          />
        </section>
      )}

      {/* PAINEL DE RESULTADOS COMPLETOS */}
      {optimizationResult && (
        <section style={{ marginTop: '10px' }}>
          
          {/* CARTAZ DE PREÇO DO CAMPEÃO (ESTILO PLACA DE SUPERMERCADO) */}
          <div style={{ 
            padding: '24px', 
            border: '4px dashed #facc15', // Borda tracejada amarela de encarte
            borderRadius: '16px', 
            backgroundColor: '#dc2626', // Fundo Vermelho Alerta Máximo
            boxShadow: '0 8px 25px rgba(220,38,38,0.3)',
            marginBottom: '30px',
            color: '#ffffff'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', flexWrap: 'wrap', gap: '10px' }}>
              <h2 style={{ margin: 0, fontSize: '24px', color: '#fff', fontWeight: '900', textTransform: 'uppercase', letterSpacing: '-0.5px' }}>
                💥 CAMPEÃO DE ECONOMIA ENCONTRADO! 💥
              </h2>
              <span style={{ backgroundColor: '#facc15', color: '#000', padding: '6px 14px', borderRadius: '4px', fontSize: '14px', fontWeight: '900', textTransform: 'uppercase', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}>
                O MAIS BARATO!
              </span>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', margin: '20px 0' }}>
              <div style={{ backgroundColor: '#fef08a', padding: '12px 16px', borderRadius: '8px', border: '2px solid #facc15' }}>
                <span style={{ fontSize: '12px', color: '#854d0e', display: 'block', fontWeight: '800' }}>REDE RECOMENDADA</span>
                <strong style={{ fontSize: '24px', color: '#000', fontWeight: '900' }}>{optimizationResult?.best_market}</strong>
              </div>
              <div style={{ backgroundColor: '#fff', padding: '12px 16px', borderRadius: '8px', color: '#000' }}>
                <span style={{ fontSize: '12px', color: '#475569', display: 'block', fontWeight: '800' }}>SOMA DOS PRODUTOS</span>
                <strong style={{ fontSize: '22px', color: '#dc2626', fontWeight: '900' }}>R$ {totalProdutosCesta.toFixed(2)}</strong>
              </div>
              <div style={{ backgroundColor: '#fff', padding: '12px 16px', borderRadius: '8px', color: '#000' }}>
                <span style={{ fontSize: '12px', color: '#475569', display: 'block', fontWeight: '800' }}>TAXA DE DESLOCAMENTO</span>
                <strong style={{ fontSize: '22px', color: custoDeslocamento > 0 ? '#dc2626' : '#16a34a', fontWeight: '900' }}>
                  {custoDeslocamento > 0 ? `R$ ${custoDeslocamento.toFixed(2)}` : 'GRÁTIS!'}
                </strong>
              </div>
            </div>

            {/* PLACA DA PROMOÇÃO PRINCIPAL */}
            <div style={{ 
              backgroundColor: '#facc15', 
              color: '#dc2626', 
              padding: '20px', 
              borderRadius: '10px', 
              textAlign: 'center', 
              border: '3px solid #fff',
              boxShadow: 'inset 0 0 10px rgba(0,0,0,0.1)'
            }}>
              <span style={{ fontSize: '15px', fontWeight: '900', display: 'block', textTransform: 'uppercase', letterSpacing: '1px', color: '#000' }}>
                PREÇO TOTAL DA SUA CESTA LEVANDO TUDO NO {optimizationResult?.best_market}:
              </span>
              <strong style={{ fontSize: '42px', fontWeight: '950', display: 'block', lineHeight: '1', marginTop: '5px' }}>
                R$ {custoTotalFinal.toFixed(2)}
              </strong>
            </div>
          </div>

          {/* LISTA COMPARTIVA - RANKING DE PREÇOS */}
          <h3 style={{ fontSize: '18px', fontWeight: '800', color: '#ffffff', backgroundColor: '#be123c', padding: '10px 15px', borderRadius: '6px', marginBottom: '15px', textTransform: 'uppercase', textAlign: 'center' }}>
            📊 COMPARATIVO DE PREÇOS ENTRE AS REDES DA REGIÃO ({comparativo.length})
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {comparativo.map((mercado, index) => {
              const isBest = index === 0;
              return (
                <div 
                  key={index} 
                  style={{ 
                    backgroundColor: '#ffffff', 
                    border: isBest ? '3px solid #facc15' : '1px solid #cbd5e1', 
                    borderRadius: '10px', 
                    padding: '16px 20px', 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    boxShadow: '0 4px 10px rgba(0,0,0,0.04)',
                    flexWrap: 'wrap',
                    gap: '15px'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ fontSize: '18px', fontWeight: '900', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      📍 {mercado?.market_name}
                      {isBest && <span style={{fontSize: '11px', backgroundColor: '#facc15', color: '#000', padding: '3px 8px', borderRadius: '4px', fontWeight: '900', textTransform: 'uppercase'}}>CAMPEÃO</span>}
                    </div>
                    <div style={{ color: '#475569', fontSize: '14px', fontWeight: '600' }}>
                      Distância: <strong>{(mercado?.distancia || 0).toFixed(2)} km</strong>
                    </div>
                  </div>

                  {/* MINI CARTAZ DE OFERTA INDIVIDUAL */}
                  <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '11px', color: '#64748b', display: 'block', fontWeight: '700' }}>SOMA PROD.</span>
                      <span style={{ fontSize: '15px', color: '#334155', fontWeight: '700' }}>R$ {((mercado?.total_produtos) || 0).toFixed(2)}</span>
                    </div>
                    
                    {/* PLACA DE PREÇO DO CARD */}
                    <div style={{ 
                      backgroundColor: isBest ? '#dc2626' : '#334155', 
                      color: isBest ? '#facc15' : '#ffffff', 
                      padding: '10px 18px', 
                      borderRadius: '8px', 
                      textAlign: 'center',
                      border: '2px solid #fff',
                      boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
                      minWidth: '110px'
                    }}>
                      <span style={{ fontSize: '10px', display: 'block', fontWeight: '900', textTransform: 'uppercase', color: isBest ? '#fff' : '#cbd5e1' }}>TOTAL FINAL</span>
                      <strong style={{ fontSize: '20px', fontWeight: '950' }}>
                        R$ {((mercado?.custo_total_final) || 0).toFixed(2)}
                      </strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          <button 
            onClick={() => setOptimizationResult(null)} 
            style={{ 
              marginTop: '30px', 
              padding: '16px 20px', 
              width: '100%', 
              fontSize: '16px', 
              backgroundColor: '#e11d48', 
              color: '#fff', 
              border: 'none', 
              borderRadius: '8px', 
              cursor: 'pointer', 
              fontWeight: '900',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              boxShadow: '0 4px 15px rgba(225,29,72,0.3)',
              transition: 'background-color 0.2s'
            }}
          >
            🛒 Montar uma Nova Lista de Compras
          </button>
        </section>
      )}
    </div>
  );
}

export default App;