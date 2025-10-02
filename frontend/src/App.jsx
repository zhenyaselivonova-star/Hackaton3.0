import { useState, useEffect } from 'react';
import AuthSection from './components/Auth/AuthSection';
import ProfileSection from './components/Profile/ProfileSection';
import MainSection from './components/Common/MainSection';
import './styles/App.css';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Проверяем авторизацию при загрузке приложения
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');

    if (token && user) {
      try {
        const userData = JSON.parse(user);
        setCurrentUser(userData);
        setIsAuthenticated(true);
        document.body.style.background = 'linear-gradient(135deg, #2575fc 0%, #6a11cb 100%)';
      } catch (error) {
        console.error('Ошибка загрузки пользователя:', error);
        handleLogout();
      }
    }
  }, []);

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
    document.body.style.background = 'linear-gradient(135deg, #2575fc 0%, #6a11cb 100%)';
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setIsAuthenticated(false);
    document.body.style.background = 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)';
  };

  return (
    <div className="container">
      {!isAuthenticated ? (
        <AuthSection onAuthSuccess={handleAuthSuccess} />
      ) : (
        <ProfileSection user={currentUser} onLogout={handleLogout} />
      )}

      <MainSection />
    </div>
  );
}

export default App;