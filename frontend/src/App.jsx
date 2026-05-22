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

  // =================================================================
  // 💥 DISPARO E RASTREAMENTO INDEPENDENTE 💥
  // =================================================================
  
  useEffect(() => {
    if (typeof requestLocation === 'function') {
      requestLocation();
    }
  }, [requestLocation]);

  useEffect(() => {
    if (geoLocation && !isManualMode) {
      setLocation(geoLocation);
      fetchAddressFromCoords(geoLocation.latitude, geoLocation.longitude);
    }
  }, [geoLocation, isManualMode]);

  // =================================================================

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
          setReadableAddress(`${city} - ${state}`);
          setIsWrongCity(true);
        }
      } else {
        setReadableAddress(`Localização via Satélite (Lat: ${lat.toFixed(3)}, Lng: ${lng.toFixed(3)})`);
        setIsWrongCity(true);
      }
    } catch (err) {
      setReadableAddress(`Localização baseada em Rede (Lat: ${lat.toFixed(3)})`);
      setIsWrongCity(false);
    }
  }, []);

  const handleCepSubmit = async (e) => {
    e.preventDefault();
    const cleanCep = cep.replace(/\D/g, '');
    
    if (cleanCep.length !== 8) {
      setCepError('Digite um CEP válido com 8 dígitos.');
      return;
    }

    setIsManualMode(true);
    setIsSearchingCep(true);
    setCepError(null);
    setReadableAddress('Buscando endereço do CEP...');

    try {
      const viaCepRes = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const viaCepData = await viaCepRes.json();

      if (viaCepRes.status !== 200 || viaCepData.erro) {
        throw new Error('CEP não encontrado na base dos Correios.');
      }

      const ruaLougradouro = viaCepData.logradouro ? viaCepData.logradouro : '';
      const bairroRegiao = viaCepData.bairro ? viaCepData.bairro : '';

      const parteRua = ruaLougradouro && bairroRegiao
        ? `${ruaLougradouro}, ${bairroRegiao}`
        : (ruaLougradouro || bairroRegiao || 'Centro');

      const enderecoDefinitivo = `${parteRua}, ${viaCepData.localidade} - ${viaCepData.uf}`;
      
      setReadableAddress(enderecoDefinitivo);
      setIsWrongCity(false);

      setIsSearchingCep(false);

      const buscarCoordenadasMapa = async () => {
        const query = `${viaCepData.logradouro || ''} ${viaCepData.bairro || ''} ${viaCepData.localidade} Brazil`;

        try {
          const osmRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
          const osmData = await osmRes.json();

          if (osmData && osmData.length > 0 && osmData[0].lat) {
            setLocation({
              latitude: parseFloat(osmData[0].lat),
              longitude: parseFloat(osmData[0].lon)
            });
          } else {
            const queryFallback = `${viaCepData.bairro || ''} ${viaCepData.localidade} Brazil`;

            const osmResFallback = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryFallback)}&limit=1`);
            const osmDataFallback = await osmResFallback.json();
            
            if (osmDataFallback && osmDataFallback.length > 0 && osmDataFallback[0].lat) {
              setLocation({
                latitude: parseFloat(osmDataFallback[0].lat),
                longitude: parseFloat(osmDataFallback[0].lon)
              });
            } else {
              setLocation({
                latitude: -23.5489,
                longitude: -46.6388
              });
            }
          }
        } catch (osmErr) {
          setLocation({
            latitude: -23.5489,
            longitude: -46.6388
          });
        }
      };

      buscarCoordenadasMapa();

    } catch (err) {
      setIsManualMode(false);
      setCepError(err.message || 'Erro ao processar a busca do CEP.');
      setReadableAddress('Erro ao fixar endereço.');
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

  const custoDeslocamento =
    transporte === 'a_pe'
      ? 0.0
      : (melhorMercado?.distancia || 0) * 0.50;

  const custoTotalFinal =
    melhorMercado?.custo_total_final || 0;

  // =========================================================
  // LOADING GPS
  // =========================================================

  if (!location && !isManualMode) {
    return (
      <div className="app-shell">

        <header className="app-header">
          <h1 className="app-title">
            Detectando sua posição
          </h1>

          <p className="app-subtitle">
            Buscando sua localização GPS para calcular os mercados mais próximos.
          </p>
        </header>

        <section className="glass-card">

          <h2 className="section-title">
            📍 Informe seu CEP
          </h2>

          <form
            onSubmit={handleCepSubmit}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '14px'
            }}
          >

            <input
              type="text"
              placeholder="00000-000"
              value={cep}
              onChange={(e) => setCep(e.target.value)}
            />

            <button
              type="submit"
              className="primary-button"
            >
              Buscar CEP
            </button>

            {cepError && (
              <p
                style={{
                  color: '#fda4af',
                  fontSize: '13px',
                  fontWeight: '700'
                }}
              >
                ❌ {cepError}
              </p>
            )}

          </form>

        </section>

      </div>
    );
  }

  // =========================================================
  // APP PRINCIPAL
  // =========================================================

  return (
    <div className="app-shell">

      {/* HEADER */}
      <header className="app-header">

        <h1 className="app-title">
          🔥 OTIMIZADOR DE COMPRAS SUPREMO
        </h1>

        <p className="app-subtitle">
          Quem pesquisa, economiza. Encontre a combinação mais barata da região.
        </p>

      </header>

      {/* LOCALIZAÇÃO */}
      <section className="glass-card">

        <h2 className="section-title">
          📍 Onde você está?
        </h2>

        {location && (
          <div className="location-box">

            <p className="location-label">
              {isManualMode
                ? 'ENDEREÇO FIXADO POR CEP'
                : 'ENDEREÇO IDENTIFICADO VIA GPS'}
            </p>

            <p className="location-text">
              {readableAddress}
            </p>

            <div
              style={{
                marginTop: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '12px',
                flexWrap: 'wrap'
              }}
            >

              <span
                style={{
                  fontSize: '11px',
                  opacity: 0.7,
                  fontFamily: 'monospace'
                }}
              >
                GPS: {location.latitude?.toFixed(5)}, {location.longitude?.toFixed(5)}
              </span>

              {isManualMode && (
                <button
                  onClick={handleResetLocation}
                  style={{
                    background: 'rgba(255,255,255,0.08)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: '#fff',
                    borderRadius: '14px',
                    padding: '10px 14px',
                    fontWeight: '700'
                  }}
                >
                  🔄 GPS Automático
                </button>
              )}

            </div>

          </div>
        )}

        {/* TRANSPORTE */}
        <div
          style={{
            marginBottom: '20px'
          }}
        >

          <label
            style={{
              display: 'block',
              marginBottom: '12px',
              fontWeight: '700',
              opacity: 0.85
            }}
          >
            🚶 Escolha o meio de deslocamento
          </label>

          <div className="transport-grid">

            <button
              type="button"
              onClick={() => setTransporte('carro')}
              className={`transport-button ${transporte === 'carro' ? 'active' : ''}`}
            >
              <div style={{
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '6px'
}}>
  <span style={{
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: '#8b5cf6',
    boxShadow: '0 0 12px rgba(139,92,246,0.8)'
  }} />
  <span>Carro / Moto</span>
</div>
              <br />
              <span
                style={{
                  fontSize: '11px',
                  opacity: 0.75
                }}
              >
                + combustível
              </span>
            </button>

            <button
              type="button"
              onClick={() => setTransporte('a_pe')}
              className={`transport-button ${transporte === 'a_pe' ? 'active' : ''}`}
            >
              <div style={{
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '6px'
}}>
  <span style={{
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: '#38bdf8',
    boxShadow: '0 0 12px rgba(56,189,248,0.8)'
  }} />
  <span>A Pé / Bike</span>
</div>
              <br />
              <span
                style={{
                  fontSize: '11px',
                  opacity: 0.75
                }}
              >
                gratuito
              </span>
            </button>

          </div>

        </div>

        {/* CEP */}
        <form
          onSubmit={handleCepSubmit}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '14px'
          }}
        >

          <input
            type="text"
            placeholder="Digite outro CEP"
            value={cep}
            onChange={(e) => setCep(e.target.value)}
            disabled={isSearchingCep}
          />

          <button
            type="submit"
            className="primary-button"
            disabled={isSearchingCep}
          >
            {isSearchingCep ? 'Buscando...' : 'Buscar CEP'}
          </button>

          {cepError && (
            <p
              style={{
                color: '#fda4af',
                fontSize: '13px',
                fontWeight: '700'
              }}
            >
              ❌ {cepError}
            </p>
          )}

        </form>

      </section>

      {/* LISTA */}
      {location && !optimizationResult && (
        <section className="glass-card">

          <h2 className="section-title">
            🛒 Monte sua Lista de Produtos
          </h2>

          <BasketBuilder
            location={location}
            transporte={transporte}
            onOptimizationComplete={(data) => setOptimizationResult(data)}
          />

        </section>
      )}

      {/* RESULTADO */}
      {optimizationResult && (
        <section>

          {/* CAMPEÃO */}
          <div className="winner-card">

            <h2 className="winner-title">
              💥 Campeão de Economia Encontrado
            </h2>

            <div
              style={{
                display: 'grid',
                gap: '14px',
                marginBottom: '22px'
              }}
            >

              <div
                style={{
                  background: 'rgba(255,255,255,0.12)',
                  borderRadius: '18px',
                  padding: '16px'
                }}
              >
                <span
                  style={{
                    fontSize: '12px',
                    opacity: 0.7,
                    display: 'block',
                    marginBottom: '8px'
                  }}
                >
                  MERCADO RECOMENDADO
                </span>

                <strong
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: '900'
                  }}
                >
                  {optimizationResult?.best_market}
                </strong>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px'
                }}
              >

                <div
                  style={{
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '18px',
                    padding: '14px'
                  }}
                >
                  <span
                    style={{
                      fontSize: '11px',
                      opacity: 0.7,
                      display: 'block',
                      marginBottom: '8px'
                    }}
                  >
                    PRODUTOS
                  </span>

                  <strong
                    style={{
                      fontSize: '1.2rem'
                    }}
                  >
                    R$ {totalProdutosCesta.toFixed(2)}
                  </strong>
                </div>

                <div
                  style={{
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '18px',
                    padding: '14px'
                  }}
                >
                  <span
                    style={{
                      fontSize: '11px',
                      opacity: 0.7,
                      display: 'block',
                      marginBottom: '8px'
                    }}
                  >
                    DESLOCAMENTO
                  </span>

                  <strong
                    style={{
                      fontSize: '1.2rem'
                    }}
                  >
                    {custoDeslocamento > 0
                      ? `R$ ${custoDeslocamento.toFixed(2)}`
                      : 'GRÁTIS'}
                  </strong>
                </div>

              </div>

            </div>

            <div
              style={{
                background: 'rgba(255,255,255,0.14)',
                borderRadius: '22px',
                padding: '20px',
                textAlign: 'center'
              }}
            >

              <span
                style={{
                  display: 'block',
                  fontSize: '13px',
                  opacity: 0.75,
                  marginBottom: '8px',
                  letterSpacing: '1px'
                }}
              >
                TOTAL FINAL
              </span>

              <strong className="total-price">
                R$ {custoTotalFinal.toFixed(2)}
              </strong>

            </div>

          </div>

          {/* RANKING */}
          <div
            style={{
              marginTop: '26px'
            }}
          >

            <h3
              style={{
                marginBottom: '18px',
                fontSize: '1rem',
                fontWeight: '800',
                opacity: 0.9
              }}
            >
              📊 Ranking Regional
            </h3>

            {comparativo.map((mercado, index) => {

              const isBest = index === 0;

              return (
                <div
                  key={index}
                  className={`market-item ${isBest ? 'best' : ''}`}
                >

                  <div>

                    <div
                      style={{
                        fontWeight: '800',
                        marginBottom: '6px'
                      }}
                    >
                      📍 {mercado?.market_name}
                    </div>

                    <div
                      style={{
                        fontSize: '13px',
                        opacity: 0.7
                      }}
                    >
                      {(mercado?.distancia || 0).toFixed(2)} km
                    </div>

                  </div>

                  <div
                    style={{
                      textAlign: 'right'
                    }}
                  >

                    <span
                      style={{
                        fontSize: '11px',
                        opacity: 0.7,
                        display: 'block',
                        marginBottom: '6px'
                      }}
                    >
                      TOTAL
                    </span>

                    <strong
                      style={{
                        fontSize: '1.1rem',
                        fontWeight: '900'
                      }}
                    >
                      R$ {((mercado?.custo_total_final) || 0).toFixed(2)}
                    </strong>

                  </div>

                </div>
              );
            })}

          </div>

          {/* RESET */}
          <button
            onClick={() => setOptimizationResult(null)}
            className="primary-button"
            style={{
              marginTop: '22px'
            }}
          >
            🛒 Nova Lista de Compras
          </button>

        </section>
      )}

    </div>
  );
}

export default App;