import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const Confetti = () => {
  const [particles, setParticles] = useState<{ id: number; x: number; color: string; size: number; delay: number }[]>([]);

  useEffect(() => {
    const colors = ['#FF5722', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0', '#F44336'];
    const newParticles = [];

    for (let i = 0; i < 100; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * 100, // random horizontal position
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 0.8 + 0.2, // random size between 0.2 and 1
        delay: Math.random() * 0.5 // random delay for animation start
      });
    }

    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute top-0 rounded"
          style={{
            left: `${particle.x}%`,
            width: `${particle.size * 10}px`,
            height: `${particle.size * 20}px`,
            backgroundColor: particle.color,
            zIndex: 50,
          }}
          initial={{ y: -20, opacity: 1, rotate: 0 }}
          animate={{
            y: window.innerHeight,
            opacity: [1, 1, 0],
            rotate: Math.random() > 0.5 ? 360 : -360,
          }}
          transition={{
            duration: 3 + Math.random() * 3,
            delay: particle.delay,
            ease: "linear",
            repeat: 2,
            repeatType: "loop"
          }}
        />
      ))}
    </div>
  );
};

export default Confetti;