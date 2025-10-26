import React, { useState } from 'react';
import { userService } from '../services/userService';

interface AuthTestProps {}

const AuthTest: React.FC<AuthTestProps> = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState(userService.getCurrentUser());

  const handleRegister = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await userService.register({
        username,
        email,
        password,
      });
      setMessage(`Registration successful: ${response.username}`);
      console.log('Registration response:', response);
    } catch (error: any) {
      setMessage(`Registration failed: ${error.message}`);
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await userService.login({
        username,
        password,
      });
      setMessage(`Login successful: ${response.user.username}`);
      setCurrentUser(response.user);
      console.log('Login response:', response);
    } catch (error: any) {
      setMessage(`Login failed: ${error.message}`);
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      await userService.logout();
      setMessage('Logout successful');
      setCurrentUser(null);
    } catch (error: any) {
      setMessage(`Logout failed: ${error.message}`);
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Authentication Test</h2>
      
      {currentUser ? (
        <div className="mb-4 p-4 bg-green-100 rounded">
          <h3 className="font-semibold">Logged in as:</h3>
          <p>Username: {currentUser.username}</p>
          <p>Email: {currentUser.email}</p>
          <button
            onClick={handleLogout}
            disabled={isLoading}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
          >
            {isLoading ? 'Logging out...' : 'Logout'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Username:
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email:
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleRegister}
              disabled={isLoading || !username || !email || !password}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isLoading ? 'Registering...' : 'Register'}
            </button>
            
            <button
              onClick={handleLogin}
              disabled={isLoading || !username || !password}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </div>
      )}
      
      {message && (
        <div className={`mt-4 p-3 rounded ${
          message.includes('successful') 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        }`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default AuthTest;