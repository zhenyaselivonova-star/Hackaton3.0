import { useState } from 'react';
import { authAPI } from '../../services/api';

const RegisterForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert('Пароли не совпадают');
      return;
    }

    if (!formData.agreeTerms) {
      alert('Необходимо согласие с условиями использования');
      return;
    }

    setLoading(true);

    try {
      // Регистрируем пользователя
      await authAPI.register(formData.username, formData.password);

      // Автоматически логиним после регистрации
      const loginResponse = await authAPI.login(formData.username, formData.password);

      // Сохраняем токен
      localStorage.setItem('token', loginResponse.access_token);

      // Создаем user object
      const user = {
        name: formData.username,
        email: `${formData.username}@example.com`,
        username: formData.username,
        created_at: new Date().toISOString(),
        analysis_count: 0
      };

      localStorage.setItem('user', JSON.stringify(user));
      onSuccess(user);
    } catch (error) {
      alert(error.message || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="tab-content">
      <h2>Начните свой путь сейчас</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="register-username">Имя пользователя</label>
          <input
            type="text"
            id="register-username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Введите имя пользователя"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="register-password">Пароль</label>
          <input
            type="password"
            id="register-password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Придумайте пароль"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="register-confirm-password">Подтвердите пароль</label>
          <input
            type="password"
            id="register-confirm-password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Повторите пароль"
            required
          />
        </div>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="agree-terms"
            name="agreeTerms"
            checked={formData.agreeTerms}
            onChange={handleChange}
            required
          />
          <label htmlFor="agree-terms">Я согласен с условиями использования</label>
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
    </div>
  );
};

export default RegisterForm;