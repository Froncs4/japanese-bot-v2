import React, { createContext, useState, useEffect, useContext } from 'react';
import { apiFetch, checkApiAvailability } from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUser = async () => {
    try {
      setLoading(true);
      // Проверка API перед запросом
      const isApiOk = await checkApiAvailability();
      
      if (!isApiOk) {
        // Если API недоступен, используем мок-данные для разработки
        console.warn('API unavailable, using mock user');
        setUser({
          id: 'mock_user',
          username: 'Student (Offline)',
          league: 'Бронзовая',
          xp: 120,
          nextLeagueXp: 500,
          streak: 5,
          todayXp: 30,
          coins: 100,
          cardsLearned: 15
        });
        setLoading(false);
        return;
      }

      // Запрос пользователя
      const data = await apiFetch('/api/user');
      if (data && data.success) {
        setUser({
          id: data.user.id,
          username: data.user.name || 'Student',
          league: data.user.league || 1,
          xp: data.user.xp || 0,
          nextLeagueXp: 500,
          streak: data.user.streak || 0,
          todayXp: data.user.daily_progress || 0,
          coins: data.user.coins || 0,
          cardsLearned: data.user.cards_learned || 0,
          weeklyXp: data.user.weekly_xp || 0
        });
      } else {
        throw new Error('Failed to fetch user data');
      }
    } catch (err) {
      console.error('Auth fetch error:', err);
      setError(err.message);
      
      // === FALLBACK: ДЕМО-РЕЖИМ ПРИ ОШИБКЕ ===
      // Если API вернул 401 или недоступен, показываем интерфейс, чтобы не пугать пользователя черным экраном
      console.warn('Using fallback user data due to API error');
      setUser({
        id: 'guest',
        username: 'Гость (Demo)',
        league: 1,
        xp: 0,
        nextLeagueXp: 100,
        streak: 0,
        todayXp: 0,
        coins: 0,
        cardsLearned: 0,
        weeklyXp: 0,
        isDemo: true // Флаг, что это демо-режим
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const value = {
    user,
    loading,
    error,
    refreshUser: fetchUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
