import { useState, useEffect } from 'react';
import { userAPI } from '../../services/api';
import ProfileHeader from './ProfileHeader';
import UploadSection from './UploadSection';

const ProfileSection = ({ user: initialUser, onLogout }) => {
  const [user, setUser] = useState(initialUser);

  useEffect(() => {
    // Загружаем актуальные данные пользователя
    const loadUserProfile = async () => {
      try {
        const userData = await userAPI.getProfile();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
      }
    };

    loadUserProfile();
  }, []);

  const handleAnalysisComplete = (result) => {
    alert(`Анализ завершен! Найдено объектов: ${result.objects_count}`);
    // Обновляем данные пользователя
    if (result.analysis_count !== undefined) {
      const updatedUser = { ...user, analysis_count: result.analysis_count };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="profile-section active">
      <ProfileHeader user={user} />

      <div className="profile-info">
        <h2>Добро пожаловать в ваш профиль!</h2>
        <p>Теперь вы можете использовать все возможности нашего сервиса.</p>

        <div className="profile-details">
          <div className="detail-item">
            <label>Дата регистрации:</label>
            <span id="registration-date">
              {formatDate(user.created_at || new Date().toISOString())}
            </span>
          </div>
          <div className="detail-item">
            <label>Статус аккаунта:</label>
            <span id="account-status">Активный</span>
          </div>
          <div className="detail-item">
            <label>Количество анализов:</label>
            <span id="analysis-count">{user.analysis_count || 0}</span>
          </div>
        </div>

        <UploadSection onAnalysisComplete={handleAnalysisComplete} />

        <div className="profile-actions" style={{ marginTop: '20px' }}>
          <button className="btn btn-secondary" onClick={onLogout}>
            Выйти из профиля
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileSection;