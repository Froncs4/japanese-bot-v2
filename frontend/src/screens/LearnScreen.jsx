import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const LearnScreen = () => {
  const navigate = useNavigate();

  const COURSES = [
    { 
      title: 'Кандзи N5', 
      subtitle: '103 базовых иероглифа', 
      path: '/kanji-n5', 
      progress: 40,
      icon: 'ココ', // Placeholder for the kanji icon
      iconBg: '#759aff',
      barColor: '#ff0055'
    },
    { 
      title: 'Кандзи N4', 
      subtitle: '181 иероглиф', 
      path: '/kanji-n4', 
      progress: 10,
      icon: 'ココ', 
      iconBg: '#759aff',
      barColor: '#ff0055'
    },
    { 
      title: 'Кандзи N3', 
      subtitle: 'Новый уровень N3', 
      path: '/kanji-n3', 
      progress: 5,
      icon: 'ココ', 
      iconBg: '#759aff',
      barColor: '#ff0055'
    },
    { 
      title: 'Слова N5', 
      subtitle: 'Базовая лексика', 
      path: '/words-n5', 
      progress: 25,
      icon: '📝', 
      iconBg: '#ffaa00', // Yellow/Orange
      barColor: '#ff0055'
    },
  ];

  return (
    <div className="screen active" style={{ 
      paddingBottom: '100px',
      background: 'linear-gradient(to bottom, #1a0b2e, #0f0518)',
      minHeight: '100vh',
      color: 'white',
      padding: '20px'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '30px', marginTop: '10px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
          <span style={{ fontSize: '28px' }}>📚</span> Изучение
        </h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {COURSES.map((course, index) => (
          <motion.div
            key={index}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate(course.path)} // В реальности пути могут быть другими
            style={{
              background: '#1e1233',
              borderRadius: '20px',
              padding: '15px',
              display: 'flex',
              alignItems: 'center',
              gap: '15px',
              border: '1px solid rgba(255,255,255,0.05)',
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {/* Icon */}
            <div style={{ 
              width: '50px', height: '50px', 
              background: course.iconBg, 
              borderRadius: '12px', 
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '20px', fontWeight: 'bold', color: 'white',
              boxShadow: '0 4px 10px rgba(0,0,0,0.3)'
            }}>
              {course.icon}
            </div>

            {/* Info */}
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '4px' }}>{course.title}</div>
              <div style={{ fontSize: '13px', color: '#888' }}>{course.subtitle}</div>
              
              {/* Progress Bar */}
              <div style={{ 
                marginTop: '10px', 
                height: '6px', 
                background: '#111', 
                borderRadius: '3px', 
                width: '100%',
                position: 'relative'
              }}>
                <div style={{ 
                  width: `${course.progress}%`, 
                  height: '100%', 
                  background: course.barColor, 
                  borderRadius: '3px',
                  boxShadow: `0 0 10px ${course.barColor}`
                }} />
              </div>
            </div>

            {/* Chevron */}
            <div style={{ color: '#666', fontWeight: 'bold' }}>›</div>

          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default LearnScreen;
