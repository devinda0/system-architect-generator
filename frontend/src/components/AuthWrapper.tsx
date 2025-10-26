import React, { useState } from 'react';
import { LoginPage } from './LoginPage';
import { RegisterPage } from './RegisterPage';

type AuthMode = 'login' | 'register';

interface AuthWrapperProps {
  onAuthSuccess: () => void;
}

export const AuthWrapper: React.FC<AuthWrapperProps> = ({ onAuthSuccess }) => {
  const [mode, setMode] = useState<AuthMode>('login');

  const handleLoginSuccess = async (user: any) => {
    console.log('User logged in:', user);
    // The auth context has already been updated by the login call
    // Just trigger the callback to notify parent
    onAuthSuccess();
  };

  const handleRegisterSuccess = async (user: any) => {
    console.log('User registered:', user);
    // The auth context has already been updated by the register call
    // Just trigger the callback to notify parent
    onAuthSuccess();
  };

  const switchToRegister = () => setMode('register');
  const switchToLogin = () => setMode('login');

  if (mode === 'register') {
    return (
      <RegisterPage
        onRegisterSuccess={handleRegisterSuccess}
        onSwitchToLogin={switchToLogin}
      />
    );
  }

  return (
    <LoginPage
      onLoginSuccess={handleLoginSuccess}
      onSwitchToRegister={switchToRegister}
    />
  );
};