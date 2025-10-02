import { useState } from 'react';
import Tabs from '../Common/Tabs';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthSection = ({ onAuthSuccess }) => {
  const [activeTab, setActiveTab] = useState('login');

  const tabs = [
    { id: 'login', label: 'Вход' },
    { id: 'register', label: 'Регистрация' }
  ];

  return (
    <div className="auth-section">
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {activeTab === 'login' && (
        <LoginForm onSuccess={onAuthSuccess} />
      )}

      {activeTab === 'register' && (
        <RegisterForm onSuccess={onAuthSuccess} />
      )}
    </div>
  );
};

export default AuthSection;