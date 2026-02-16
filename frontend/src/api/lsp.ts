import client from './client';

export const predictLSP = async (frames: any[]) => {
  const response = await client.post('/lsp/predict', { frames });
  return response.data;
};

export const getVocabulary = async () => {
  const response = await client.get('/lsp/vocabulary');
  return response.data;
};
