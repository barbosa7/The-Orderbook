import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true
});

// Add an interceptor to include the token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const placeOrder = async (orderData: {
  competition_id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
}) => {
  return api.post('/order', orderData);
};

export const joinCompetition = async (competitionId: string) => {
  return api.post('/competition/join', null, {
    params: { competition_id: competitionId }
  });
};

export const getParticipants = async (competitionId: string) => {
  return api.get(`/competition/${competitionId}/users`);
};

export const getPnL = async (competitionId: string) => {
  return api.get(`/competition/${competitionId}/pnl`);
};

export const getUserOrders = async (competitionId: string, userId: string) => {
  return api.get(`/competition/${competitionId}/orders/${userId}`);
};

export const cancelOrder = async (competitionId: string, orderId: string) => {
  return api.delete(`/competition/${competitionId}/order/${orderId}`);
}; 