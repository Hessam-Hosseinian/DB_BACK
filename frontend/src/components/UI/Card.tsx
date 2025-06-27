import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`
      bg-gray-800/50 backdrop-blur-sm border border-gray-600/30 rounded-xl shadow-xl
      transition-all duration-300 hover:shadow-2xl hover:border-gray-500/50
      ${className}
    `}>
      {children}
    </div>
  );
};

export default Card;