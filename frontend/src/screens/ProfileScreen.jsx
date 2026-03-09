import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings, Edit2, X } from 'lucide-react';

const ProfileScreen = () => {
  const { user } = useAuth();
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState('dark'); // 'dark', 'light', 'neon'

  if (!user) return null;

  const stats = [
    { value: user.xp || 0, label: 'XP', color: '#ff4d4d' },
    { value: user.streak || 0, label: 'Серия', color: '#ff4d4d' }, // Огонь
    { value: user.cardsLearned || 0, label: 'Карточек', color: '#ff4d4d' },
  ];

  const progressSections = [
    { title: 'Хирагана', current: 44, total: 46, percent: 96, color: '#ff0055' },
    { title: 'Катакана', current: 43, total: 46, percent: 93, color: '#ff0055' },
    { title: 'Кандзи N5', current: 0, total: 103, percent: 0, color: '#ff0055' },
    { title: 'Слова N5', current: 5, total: 40, percent: 13, color: '#ff0055' },
  ];

  return (
    <div className="screen active" style={{ 
      paddingBottom: '100px', 
      background: 'linear-gradient(to bottom, #1a0b2e, #0f0518)',
      minHeight: '100vh',
      color: 'white'
    }}>
      
      {/* Верхняя панель с кнопками */}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '20px', alignItems: 'center' }}>
        <div 
          onClick={() => alert('Смена ника пока не реализована')}
          style={{ cursor: 'pointer', padding: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}
        >
          <Edit2 size={20} color="white" />
        </div>

        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>Профиль</div>

        <div 
          onClick={() => setShowSettings(!showSettings)}
          style={{ cursor: 'pointer', padding: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}
        >
          <Settings size={20} color="white" />
        </div>
      </div>

      {/* Аватар и Инфо */}
      <div style={{ textAlign: 'center', marginTop: '10px' }}>
        <div style={{ 
          width: '100px', height: '100px', 
          borderRadius: '50%', 
          border: '3px solid #ff0055',
          margin: '0 auto 15px', 
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: '#fff',
          overflow: 'hidden'
        }}>
           {/* Placeholder avatar if no photo */}
           <span style={{fontSize: '40px'}}>🐱</span> 
        </div>
        
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px' }}>
          {user.username}
        </h2>
        
        <div style={{ 
          display: 'inline-block', 
          background: '#2a1b3d', 
          padding: '5px 15px', 
          borderRadius: '20px', 
          fontSize: '14px',
          color: '#ff4d4d',
          fontWeight: 'bold'
        }}>
          🥷 Самурай
        </div>
      </div>

      {/* Статистика */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr 1fr', 
        gap: '10px', 
        padding: '20px',
        marginTop: '10px'
      }}>
        {stats.map((stat, idx) => (
          <div key={idx} style={{ 
            background: '#1e1233', 
            padding: '15px 5px', 
            borderRadius: '16px', 
            textAlign: 'center' 
          }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: stat.color }}>{stat.value}</div>
            <div style={{ fontSize: '12px', color: '#888' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Прогресс */}
      <div style={{ padding: '0 20px' }}>
        <h3 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          📊 Прогресс по разделам
        </h3>
        
        {progressSections.map((item, idx) => (
          <div key={idx} style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px' }}>
              <span>{item.title}</span>
              <span>
                {item.current}/{item.total} 
                <span style={{ color: item.percent > 0 ? item.color : '#666', fontWeight: 'bold', marginLeft: '5px' }}>
                  ({item.percent}%)
                </span>
              </span>
            </div>
            <div style={{ height: '8px', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ 
                width: `${item.percent}%`, 
                height: '100%', 
                background: item.percent > 0 ? item.color : 'transparent',
                borderRadius: '4px'
              }} />
            </div>
          </div>
        ))}
      </div>

      {/* Модалка настроек */}
      {showSettings && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{ background: '#1e1233', padding: '20px', borderRadius: '20px', width: '80%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3>Настройки</h3>
              <X onClick={() => setShowSettings(false)} />
            </div>
            <p>Тема интерфейса:</p>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <button style={{ flex: 1, padding: '10px', background: '#ff0055', border: 'none', borderRadius: '8px', color: 'white' }}>Neon</button>
              <button style={{ flex: 1, padding: '10px', background: '#333', border: 'none', borderRadius: '8px', color: 'white' }}>Dark</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ProfileScreen;
