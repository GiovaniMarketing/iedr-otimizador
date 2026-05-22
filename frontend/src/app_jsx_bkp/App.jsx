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
      /* CONTAINER IMERSIVO */
      maxWidth: '500px', margin: '0 auto', minHeight: '100vh', padding: '25px', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#0a0414', color: '#f8fafc', display: 'flex', flexDirection: 'column',
      position: 'relative', overflow: 'hidden', boxSizing: 'border-box',
    }}>
      
      {/* 1. LINHAS SIMÉTRICAS EM CURVAS */}
      <div style={{ position: 'absolute', top: '-15%', right: '-20%', width: '400px', height: '400px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.06)', zIndex: 0, pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', top: '-5%', right: '-10%', width: '500px', height: '500px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.04)', zIndex: 0, pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', top: '5%', right: '0%', width: '600px', height: '600px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.02)', zIndex: 0, pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', bottom: '0%', left: '-30%', width: '500px', height: '500px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.05)', zIndex: 0, pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', bottom: '10%', left: '-20%', width: '600px', height: '600px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.03)', zIndex: 0, pointerEvents: 'none' }}></div>

      {/* 2. LUZES NEON DE ALTA LUMINOSIDADE */}
      <div style={{ position: 'absolute', top: '-10%', right: '-20%', width: '350px', height: '350px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(217, 70, 239, 0.45) 0%, rgba(0,0,0,0) 70%)', filter: 'blur(40px)', mixBlendMode: 'screen', zIndex: 0, pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', bottom: '-10%', left: '-20%', width: '450px', height: '450px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, rgba(0,0,0,0) 70%)', filter: 'blur(50px)', mixBlendMode: 'screen', zIndex: 0, pointerEvents: 'none' }}></div>

      {/* CABEÇALHO */}
      <header style={{ textAlign: 'center', marginBottom: '35px', zIndex: 1, position: 'relative' }}>
        <h1 style={{ 
          fontSize: '22px', fontWeight: '900', margin: '15px 0 6px 0', textTransform: 'uppercase', letterSpacing: '2px',
          background: 'linear-gradient(135deg, #fff 0%, #d946ef 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          OTIMIZADOR SUPREMO
        </h1>
        <div style={{ width: '30px', height: '3px', background: 'linear-gradient(90deg, #8b5cf6, #d946ef)', margin: '0 auto', borderRadius: '2px', boxShadow: '0 0 10px rgba(217, 70, 239, 0.5)' }}></div>
      </header>

      {/* ETAPA 1: LOCALIZAÇÃO */}
      <section style={{ 
        background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)',
        padding: '24px', borderRadius: '28px', border: '1px solid rgba(255, 255, 255, 0.08)',
        borderTop: '1px solid rgba(255, 255, 255, 0.15)', boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
        marginBottom: '20px', zIndex: 1, position: 'relative'
      }}>
        <h2 style={{ fontSize: '14px', fontWeight: '800', color: '#e9d5ff', margin: '0 0 18px 0', textTransform: 'uppercase', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d946ef" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          Localização Atual
        </h2>
        
        {/* CAIXA DE LOCALIZAÇÃO RESTAURADA COMO O ORIGINAL */}
        {location && (
          <div style={{ background: 'rgba(0, 0, 0, 0.4)', padding: '18px', borderRadius: '20px', marginBottom: '24px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            
            {/* Texto "Endereço Fixado por CEP" restaurado */}
            <span style={{ fontSize: '11px', color: '#d946ef', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', marginBottom: '6px' }}>
              {isManualMode ? 'Endereço fixado por CEP:' : 'Endereço identificado:'}
            </span>
            
            <p style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: '700', color: '#fff', lineHeight: '1.4' }}>
              {readableAddress}
            </p>
            
            {/* Divisão clara entre Endereço e GPS */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
              <div>
                <span style={{ fontSize: '11px', color: '#cbd5e1', display: 'block', marginBottom: '2px' }}>Coordenadas GPS:</span>
                <span style={{ fontSize: '14px', color: '#a855f7', fontFamily: 'monospace', fontWeight: 'bold' }}>
                  {location.latitude?.toFixed(5)}, {location.longitude?.toFixed(5)}
                </span>
              </div>
              
              {isManualMode && (
                <button onClick={handleResetLocation} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', padding: '10px 14px', borderRadius: '12px', background: 'rgba(217, 70, 239, 0.15)', color: '#fdf4ff', fontWeight: '800', border: '1px solid rgba(217, 70, 239, 0.4)', cursor: 'pointer' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                  USAR GPS
                </button>
              )}
            </div>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button 
            onClick={() => setTransporte('carro')}
            style={{ 
              flex: 1, padding: '14px 10px', cursor: 'pointer', borderRadius: '16px', fontWeight: '700', fontSize: '12px', border: 'none',
              background: transporte === 'carro' ? 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)' : 'rgba(255,255,255,0.04)',
              color: transporte === 'carro' ? '#fff' : '#94a3b8', 
              boxShadow: transporte === 'carro' ? '0 10px 20px rgba(217, 70, 239, 0.4)' : 'none',
              borderTop: transporte === 'carro' ? '1px solid rgba(255,255,255,0.3)' : '1px solid rgba(255,255,255,0.05)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px'
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 14v4c0 .5.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>
            Carro / Moto
          </button>
          <button 
            onClick={() => setTransporte('a_pe')}
            style={{ 
              flex: 1, padding: '14px 10px', cursor: 'pointer', borderRadius: '16px', fontWeight: '700', fontSize: '12px', border: 'none',
              background: transporte === 'a_pe' ? 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)' : 'rgba(255,255,255,0.04)',
              color: transporte === 'a_pe' ? '#fff' : '#94a3b8', 
              boxShadow: transporte === 'a_pe' ? '0 10px 20px rgba(217, 70, 239, 0.4)' : 'none',
              borderTop: transporte === 'a_pe' ? '1px solid rgba(255,255,255,0.3)' : '1px solid rgba(255,255,255,0.05)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px'
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 11.5V14l-3-3 4-3 2 3h2"/></svg>
            A Pé / Bike
          </button>
        </div>

        <form onSubmit={handleCepSubmit} style={{ display: 'flex', gap: '10px' }}>
          <input 
            type="text" placeholder="Alterar CEP..." value={cep} onChange={(e) => setCep(e.target.value)}
            style={{ flex: 1, padding: '16px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.4)', color: '#fff', fontSize: '14px' }}
          />
          <button type="submit" style={{ padding: '16px 24px', background: '#fff', color: '#000', border: 'none', borderRadius: '16px', fontWeight: '900', boxShadow: '0 4px 15px rgba(255,255,255,0.2)' }}>OK</button>
        </form>
      </section>

      {/* ETAPA 2: LISTA DE PRODUTOS */}
      {location && !optimizationResult && (
        <section style={{ 
          background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)',
          padding: '24px', borderRadius: '28px', border: '1px solid rgba(255, 255, 255, 0.08)', borderTop: '1px solid rgba(255, 255, 255, 0.15)',
          marginBottom: '20px', zIndex: 1, position: 'relative'
        }}>
          <h2 style={{ fontSize: '14px', fontWeight: '800', color: '#e9d5ff', margin: '0 0 16px 0', textTransform: 'uppercase', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d946ef" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
            Sua Lista
          </h2>
          <BasketBuilder location={location} transporte={transporte} onOptimizationComplete={(data) => setOptimizationResult(data)} />
        </section>
      )}

      {/* ETAPA 3: RESULTADOS */}
      {optimizationResult && (
        <section style={{ zIndex: 1, position: 'relative' }}>
          
          <div style={{ 
            background: 'linear-gradient(135deg, rgba(88, 28, 135, 0.6) 0%, rgba(30, 27, 75, 0.8) 100%)', backdropFilter: 'blur(20px)',
            padding: '28px', borderRadius: '32px', border: '1px solid rgba(217, 70, 239, 0.4)',
            boxShadow: '0 20px 50px rgba(0,0,0,0.5), inset 0 2px 0 rgba(255,255,255,0.1)', marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: '900', color: '#fdf4ff', background: 'linear-gradient(90deg, #8b5cf6, #d946ef)', padding: '4px 10px', borderRadius: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>
                Campeão
              </span>
            </div>

            <h2 style={{ fontSize: '26px', color: '#fff', margin: '0 0 24px 0', fontWeight: '900', lineHeight: '1.2' }}>
              {optimizationResult?.best_market}
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontSize: '10px', color: '#a855f7', display: 'block', marginBottom: '6px', fontWeight: '700', textTransform: 'uppercase' }}>PRODUTOS</span>
                <strong style={{ fontSize: '18px', color: '#fff', fontWeight: '800' }}>R$ {totalProdutosCesta.toFixed(2)}</strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontSize: '10px', color: '#a855f7', display: 'block', marginBottom: '6px', fontWeight: '700', textTransform: 'uppercase' }}>DESLOCAMENTO</span>
                <strong style={{ fontSize: '18px', color: custoDeslocamento > 0 ? '#fff' : '#4ade80', fontWeight: '800' }}>{custoDeslocamento > 0 ? `R$ ${custoDeslocamento.toFixed(2)}` : 'GRÁTIS'}</strong>
              </div>
            </div>

            <div style={{ textAlign: 'center', padding: '24px', background: 'linear-gradient(135deg, rgba(217, 70, 239, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)', borderRadius: '20px', border: '1px solid rgba(217, 70, 239, 0.3)' }}>
              <span style={{ fontSize: '12px', color: '#e9d5ff', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>VALOR TOTAL FINAL</span>
              <strong style={{ fontSize: '46px', display: 'block', color: '#fff', fontWeight: '900', letterSpacing: '-1px', margin: '8px 0' }}>
                R$ {custoTotalFinal.toFixed(2)}
              </strong>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {comparativo.map((mercado, index) => (
              <div key={index} style={{ 
                background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(10px)',
                padding: '18px 22px', borderRadius: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                border: index === 0 ? '1px solid #d946ef' : '1px solid rgba(255,255,255,0.05)'
              }}>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: '800', color: '#fff' }}>{mercado?.market_name}</div>
                  <div style={{ color: '#94a3b8', fontSize: '12px' }}>{(mercado?.distancia || 0).toFixed(2)} km</div>
                </div>
                <strong style={{ fontSize: '18px', color: index === 0 ? '#d946ef' : '#fff', fontWeight: '900' }}>
                  R$ {((mercado?.custo_total_final) || 0).toFixed(2)}
                </strong>
              </div>
            ))}
          </div>
          
          <button onClick={() => setOptimizationResult(null)} style={{ marginTop: '30px', padding: '20px', width: '100%', background: 'linear-gradient(135deg, #fff 0%, #e9d5ff 100%)', color: '#1e0a3c', border: 'none', borderRadius: '20px', fontWeight: '900', textTransform: 'uppercase', cursor: 'pointer', letterSpacing: '1px', boxShadow: '0 10px 25px rgba(255,255,255,0.15)' }}>
            Nova Consulta
          </button>
        </section>
      )}
    </div>
  );
}

export default App;