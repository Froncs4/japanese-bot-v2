import React from 'react';

const ShopScreen = () => {
  return (
    <div className="screen active" style={{ paddingBottom: '100px' }}>
      <div className="glass-header">
        <h2 style={{ fontWeight: 800, fontSize: '26px' }}>🛍️ Магазин</h2>
        <p style={{ color: 'var(--text-hint)', fontSize: '14px' }}>Обменяй монеты на бонусы</p>
      </div>
      
      <div className="section" style={{ textAlign: 'center', marginTop: '50px' }}>
        <div style={{ fontSize: '60px' }}>💎</div>
        <h3>Скоро открытие!</h3>
        <p style={{ color: 'var(--text-hint)' }}>Мы завозим новые товары.</p>
      </div>
    </div>
  );
};

export default ShopScreen;
