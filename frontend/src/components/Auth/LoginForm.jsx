import { useState } from 'react';
import { authAPI } from '../../services/api';

const LoginForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authAPI.login(formData.username, formData.password);

      // Сохраняем токен
      localStorage.setItem('token', response.access_token);

      // Создаем mock user object (замените на реальный запрос к /users/me если есть)
      const user = {
        name: formData.username,
        email: `${formData.username}@example.com`, // временно
        username: formData.username,
        created_at: new Date().toISOString(),
        analysis_count: 0
      };

      localStorage.setItem('user', JSON.stringify(user));
      onSuccess(user);
    } catch (error) {
      alert(error.message || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="tab-content active">
      <h2>Войдите в кабинет</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="login-username">Имя пользователя</label>
          <input
            type="text"
            id="login-username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Введите ваше имя пользователя"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="login-password">Пароль</label>
          <input
            type="password"
            id="login-password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Введите ваш пароль"
            required
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>

      <div className="separator">
        <span>Или войдите с помощью</span>
      </div>

      <div className="social-login">
        <div className="social-btn">VK</div>
        <div className="social-btn">FB</div>
        <div className="social-btn">G</div>
      </div>
    </div>
  );
};

export default LoginForm;