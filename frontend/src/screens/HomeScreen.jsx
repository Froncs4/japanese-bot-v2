import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const HomeScreen = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [leagueTimeLeft, setLeagueTimeLeft] = useState('');
  
  if (!user) return <div style={{padding: '20px', textAlign: 'center'}}>Загрузка профиля...</div>;

  return (
    <div className="screen active" style={{ 
      paddingBottom: '100px',
      background: 'linear-gradient(to bottom, #1a0b2e, #0f0518)',
      minHeight: '100vh',
      color: 'white'
    }}>
      {/* Header Profile Snippet */}
      <div style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}>
        <div style={{ 
          width: '60px', height: '60px', 
          borderRadius: '50%', background: '#fff', 
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '30px', border: '2px solid #ff0055'
        }}>
          🐱
        </div>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold' }}>Привет, {user.username}! 👋</h2>
          <div style={{ fontSize: '14px', color: '#759aff', fontWeight: 'bold' }}>🏆 {user.league} Лига</div>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', padding: '0 20px' }}>
        <div style={{ background: '#1e1233', padding: '15px', borderRadius: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '5px' }}>🔥 {user.streak}</div>
          <div style={{ fontSize: '12px', color: '#888', fontWeight: 'bold' }}>Дней подряд</div>
        </div>
        <div style={{ background: '#1e1233', padding: '15px', borderRadius: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '5px' }}>⚡ {user.todayXp}</div>
          <div style={{ fontSize: '12px', color: '#888', fontWeight: 'bold' }}>XP сегодня</div>
        </div>
      </div>

      <div className="section" style={{ padding: '20px' }}>
        <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
          🎯 Ежедневные цели
        </h3>
        
        {/* Кнопка для начала обучения (если нет прогресса) */}
        {user.xp < 50 && (
          <div 
            onClick={() => navigate('/alphabet')}
            style={{
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              borderRadius: '20px',
              padding: '20px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '15px',
              cursor: 'pointer',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
            }}
          >
            <div style={{ fontSize: '32px' }}>🚀</div>
            <div>
              <div style={{ fontWeight: 'bold', fontSize: '18px', marginBottom: '4px' }}>Начать обучение</div>
              <div style={{ fontSize: '13px', opacity: 0.9 }}>Выучи первые символы хираганы!</div>
            </div>
          </div>
        )}

        <div className="quest-item" style={{ background: '#1e1233', borderRadius: '16px', padding: '15px', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '15px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div className="quest-icon" style={{ fontSize: '24px' }}>📚</div>
          <div className="quest-info" style={{ flex: 1 }}>
            <div className="quest-title" style={{ fontWeight: 'bold', fontSize: '16px' }}>Изучить 5 слов</div>
            <div style={{ 
              marginTop: '8px', height: '6px', background: '#111', borderRadius: '3px', width: '100%' 
            }}>
              <div style={{ width: '40%', height: '100%', background: '#ff0055', borderRadius: '3px' }} />
            </div>
          </div>
          <div style={{ fontWeight: 'bold', color: '#759aff' }}>+50 XP</div>
        </div>

        <div className="quest-item" style={{ background: '#1e1233', borderRadius: '16px', padding: '15px', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '15px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div className="quest-icon" style={{ fontSize: '24px', color: '#4ade80' }}>✅</div>
          <div className="quest-info" style={{ flex: 1 }}>
            <div className="quest-title" style={{ fontWeight: 'bold', fontSize: '16px' }}>Пройти тест</div>
            <div style={{ 
              marginTop: '8px', height: '6px', background: '#111', borderRadius: '3px', width: '100%' 
            }}>
              <div style={{ width: '100%', height: '100%', background: '#4ade80', borderRadius: '3px' }} />
            </div>
          </div>
          <div style={{ fontWeight: 'bold', color: '#4ade80' }}>✓</div>
        </div>
      </div>

      <div className="section">
        <h3 className="section-title">🏆 Лига</h3>
        <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '16px', padding: '16px', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ fontSize: '30px' }}>🛡️</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '4px' }}>До следующей лиги</div>
            <div style={{ fontSize: '12px', color: 'var(--text-hint)' }}>{user.nextLeagueXp - user.xp} XP осталось</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '12px', color: 'var(--warning)', fontWeight: 'bold' }}>⏳ {leagueTimeLeft}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-hint)' }}>до конца</div>
          </div>
        </div>
      </div>

      <div className="section" style={{ paddingBottom: '100px' }}>
        <h3 className="section-title">Быстрый доступ</h3>
        <div className="menu-grid">
          <motion.div whileTap={{ scale: 0.95 }} className="menu-card wide" onClick={() => navigate('/learn')}>
            <div className="card-icon">🎓</div>
            <div>
              <div className="card-title">Начать урок</div>
              <div className="card-subtitle">Продолжить N5</div>
            </div>
          </motion.div>
          <motion.div whileTap={{ scale: 0.95 }} className="menu-card" onClick={() => navigate('/wheel')}>
            <div className="card-icon">🎡</div>
            <div className="card-title">Рулетка</div>
          </motion.div>
          <motion.div whileTap={{ scale: 0.95 }} className="menu-card" onClick={() => navigate('/shop')}>
            <div className="card-icon">🛍️</div>
            <div className="card-title">Магазин</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;