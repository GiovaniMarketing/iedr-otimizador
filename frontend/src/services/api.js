import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // URL do backend FastAPI
  headers: {
    'Content-Type': 'application/json',
  },
});

export const optimizeBasketRequest = async (payload) => {
  try {
    // Aqui fazemos o POST exato para a rota que validamos no dossiê
    const response = await api.post('/optimizer/basket', payload);
    return response.data;
  } catch (error) {
    console.error('Erro na otimização:', error);
    throw new Error(
      error.response?.data?.detail || 'Erro ao processar a otimização no servidor.'
    );
  }
};