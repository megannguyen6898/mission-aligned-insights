import api from './api';

export interface GenerateDashboardPayload {
  title: string;
  topics: string[];
}

export const dashboardService = {
  async generateDashboard(payload: GenerateDashboardPayload) {
    const response = await api.post('/dashboards/generate', payload);
    return response.data;
  },
  async listDashboards() {
    const response = await api.get('/dashboards');
    return response.data;
  },
  async getDashboard(id: number) {
    const response = await api.get(`/dashboards/${id}`);
    return response.data;
  }
};
