import React, { useState } from 'react';
import { getCoordinatesFromCEP } from '../services/geocoding';

export const LocationFallback = ({ onLocationFound }) => {
  const [cep, setCep] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const coords = await getCoordinatesFromCEP(cep);
      // Passa as coordenadas para o hook principal que criamos anteriormente
      onLocationFound(coords.latitude, coords.longitude);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="location-fallback">
      <h4>Buscar localização por CEP</h4>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Digite seu CEP (ex: 01001-000)"
          value={cep}
          onChange={(e) => setCep(e.target.value)}
          maxLength={9}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || cep.length < 8}>
          {isLoading ? 'Buscando...' : 'Confirmar CEP'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};