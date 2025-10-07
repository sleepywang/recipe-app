import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  getRecipes() {
    return apiClient.get('/recipes');
  },
  getRecipe(id) {
    return apiClient.get(`/recipes/${id}`);
  },
  createRecipe(data) {
    return apiClient.post('/recipes', data);
  },
  updateRecipe(id, data) {
    return apiClient.put(`/recipes/${id}`, data);
  },
  deleteRecipe(id) {
    return apiClient.delete(`/recipes/${id}`);
  },
  getTags() {
    return apiClient.get('/tags');
  },
  uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    // Use a separate axios post for multipart/form-data
    return axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};