import api from './api';

export const dataService = {
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/data/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  async listUploads() {
    const response = await api.get('/data/uploads');
    return response.data;
  }
};
