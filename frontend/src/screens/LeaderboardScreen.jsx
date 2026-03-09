import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils/api';

const LeaderboardScreen = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const data = await apiFetch('/api/leaderboard');
        if (data && data.success) {
          setPlayers(data.players);
        } else {
            // Mock data if fails
            setPlayers([
                { id: 1, name: 'Сенсей', xp: 5000, streak: 30, league: 'Master' },
                { id: 2, name: 'Танака', xp: 2400, streak: 15, league: 'Diamond' },
                { id: 3, name: 'Юми', xp: 1200, streak: 5, league: 'Gold' }
            ]);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  return (
    <div className="screen active" style={{ paddingBottom: '100px' }}>
      <div className="glass-header">
        <h2 style={{ fontWeight: 800, fontSize: '26px' }}>🏆 Лига</h2>
        <p style={{ color: 'var(--text-hint)', fontSize: '14px' }}>Топ лучших учеников</p>
      </div>
      
      <div className="section">
        {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>Загрузка...</div>
        ) : (
            players.map((p, index) => (
                <div key={p.id} style={{ 
                    display: 'flex', alignItems: 'center', 
                    padding: '15px', 
                    background: 'rgba(30, 30, 46, 0.7)', 
                    borderRadius: '16px', 
                    marginBottom: '10px',
                    border: index < 3 ? '1px solid var(--gold)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                    <div style={{ width: '30px', fontWeight: 'bold', color: index < 3 ? 'var(--gold)' : 'var(--text-hint)' }}>
                        #{index + 1}
                    </div>
                    <div style={{ width: '40px', height: '40px', background: 'var(--bg)', borderRadius: '50%', marginRight: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {p.name.charAt(0)}
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold' }}>{p.name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-hint)' }}>Лига {p.league}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{p.xp} XP</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-hint)' }}>🔥 {p.streak}</div>
                    </div>
                </div>
            ))
        )}
      </div>
    </div>
  );
};

export default LeaderboardScreen;
