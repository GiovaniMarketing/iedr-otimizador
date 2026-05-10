import { useState, useCallback } from 'react';

export const useUserLocation = () => {
  const [location, setLocation] = useState(null); // { latitude, longitude }
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const requestLocation = useCallback(() => {
    setIsLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocalização não é suportada por este navegador.');
      setIsLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setIsLoading(false);
      },
      (err) => {
        let errorMessage = 'Erro desconhecido ao buscar localização.';
        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMessage = 'Permissão de localização negada. Por favor, insira o CEP ou endereço.';
            break;
          case err.POSITION_UNAVAILABLE:
            errorMessage = 'Informação de localização indisponível no momento.';
            break;
          case err.TIMEOUT:
            errorMessage = 'Tempo limite de requisição excedido.';
            break;
          default:
            break;
        }
        setError(errorMessage);
        setIsLoading(false);
      },
      {
        enableHighAccuracy: true, // Tenta usar o GPS real, importante para mobile
        timeout: 10000,           // 10 segundos de limite
        maximumAge: 0             // Não usa cache de localização antiga
      }
    );
  }, []);

  // Função preparada para o fallback de CEP/Endereço
  const setManualLocation = useCallback((latitude, longitude) => {
    setLocation({ latitude, longitude });
    setError(null); 
  }, []);

  return { 
    location, 
    isLoading, 
    error, 
    requestLocation, 
    setManualLocation 
  };
};