import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, BookOpen, Library, Trophy, User } from 'lucide-react';

export const BottomNav = () => {
  return (
    <div className="bottom-nav">
      <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <Home className="icon" size={24} />
        <span>Главная</span>
      </NavLink>
      
      <NavLink to="/stories" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <BookOpen className="icon" size={24} />
        <span>Истории</span>
      </NavLink>
      
      <NavLink to="/learn" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <Library className="icon" size={24} />
        <span>Учить</span>
      </NavLink>
      
      <NavLink to="/leaderboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <Trophy className="icon" size={24} />
        <span>Лиги</span>
      </NavLink>

      <NavLink to="/profile" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <User className="icon" size={24} />
        <span>Профиль</span>
      </NavLink>
    </div>
  );
};
