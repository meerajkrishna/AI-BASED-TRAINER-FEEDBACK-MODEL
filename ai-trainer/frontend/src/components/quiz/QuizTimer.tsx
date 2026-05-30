import { useState, useEffect } from 'react';

interface QuizTimerProps {
  totalSeconds: number;
  onTimeUp: () => void;
  isRunning: boolean;
}

export const QuizTimer = ({ totalSeconds, onTimeUp, isRunning }: QuizTimerProps) => {
  const [timeLeft, setTimeLeft] = useState(totalSeconds);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          onTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, onTimeUp]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const progress = (timeLeft / totalSeconds) * 100;

  const isWarning = timeLeft <= 60; // Last minute warning
  const isCritical = timeLeft <= 30; // Last 30 seconds

  return (
    <div className={`bg-white rounded-xl border p-4 shadow-sm transition-colors ${
      isCritical ? 'border-red-500 bg-red-50' : isWarning ? 'border-yellow-500' : 'border-gray-200'
    }`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">⏱️ Time Remaining</span>
        {isCritical && <span className="text-xs text-red-600 font-bold animate-pulse">Hurry up!</span>}
      </div>

      {/* Timer Display */}
      <div className={`text-3xl font-bold text-center mb-3 ${
        isCritical ? 'text-red-600' : isWarning ? 'text-yellow-600' : 'text-gray-800'
      }`}>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-1000 ${
            isCritical ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-primary'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};
