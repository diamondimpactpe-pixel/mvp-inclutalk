import client from './client';

export const startSession = async () => {
  const response = await client.post('/sessions/start');
  return response.data;
};

export const endSession = async (sessionId: number) => {
  const response = await client.post(`/sessions/${sessionId}/end`, {});
  return response.data;
};
