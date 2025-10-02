// Конфигурация API
const API_BASE_URL = 'http://localhost:8000';

// Общая функция для API запросов
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  // Для FormData убираем Content-Type
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Auth API - исправлено под ваши endpoints
export const authAPI = {
  // Регистрация
  register: async (username, password) => {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: username,
        password: password
      }),
    });
  },

  // Логин (OAuth2 token)
  login: async (username, password) => {
    // Для OAuth2 используем FormData
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password');

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Ошибка авторизации');
    }

    return await response.json();
  },
};

// User API
export const userAPI = {
  getProfile: async () => {
    return apiRequest('/users/me');
  },
};

// Upload API
export const uploadAPI = {
  analyzeImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest('/upload/', {
      method: 'POST',
      body: formData,
    });
  },
};

// Экспорт по умолчанию
export default {
  authAPI,
  userAPI,
  uploadAPI
};