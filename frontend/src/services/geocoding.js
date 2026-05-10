import axios from 'axios';

export const getCoordinatesFromCEP = async (cep) => {
  try {
    const cleanCep = cep.replace(/\D/g, '');
    if (cleanCep.length !== 8) {
      throw new Error('CEP deve conter 8 dígitos.');
    }

    // 1. Busca no ViaCEP
    const viaCepResponse = await axios.get(`https://viacep.com.br/ws/${cleanCep}/json/`);
    
    if (viaCepResponse.data.erro) {
      throw new Error('CEP não encontrado.');
    }

    const { logradouro, bairro, localidade, uf } = viaCepResponse.data;
    
    // Monta duas strings de busca: uma completa e uma genérica (só cidade)
    const fullAddressQuery = `${logradouro}, ${bairro}, ${localidade}, ${uf}, Brasil`;
    const cityAddressQuery = `${localidade}, ${uf}, Brasil`;

    // 2. Tenta buscar o endereço completo no Nominatim
    let nominatimResponse = await axios.get('https://nominatim.openstreetmap.org/search', {
      params: { q: fullAddressQuery, format: 'json', limit: 1 },
      headers: { 'Accept-Language': 'pt-BR' }
    });

    // 3. Fallback: Se não achar a rua exata, busca pelo centro da cidade
    if (nominatimResponse.data.length === 0) {
      console.log("Rua não encontrada no mapa, buscando pelo centro da cidade...");
      nominatimResponse = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: cityAddressQuery, format: 'json', limit: 1 },
        headers: { 'Accept-Language': 'pt-BR' }
      });
    }

    // Se ainda assim falhar
    if (nominatimResponse.data.length === 0) {
      throw new Error('Não foi possível encontrar coordenadas para esta região.');
    }

    return {
      latitude: parseFloat(nominatimResponse.data[0].lat),
      longitude: parseFloat(nominatimResponse.data[0].lon)
    };

  } catch (error) {
    console.error('Erro no geocoding:', error);
    throw new Error(error.response?.data?.message || error.message || 'Erro ao processar o CEP.');
  }
};