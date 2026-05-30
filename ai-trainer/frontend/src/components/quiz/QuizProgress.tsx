interface QuizProgressProps {
  current: number;
  total: number;
  answeredCount: number;
}

export const QuizProgress = ({ current, total, answeredCount }: QuizProgressProps) => {
  const progress = (current / total) * 100;
  const answeredProgress = (answeredCount / total) * 100;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">Progress</span>
        <span className="text-sm font-bold text-gray-800">
          {current} / {total}
        </span>
      </div>
      
      {/* Progress Bar */}
      <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        {/* Answered progress (lighter) */}
        <div
          className="absolute h-full bg-green-200 rounded-full transition-all duration-300"
          style={{ width: `${answeredProgress}%` }}
        />
        {/* Current position (darker) */}
        <div
          className="absolute h-full bg-primary rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Question Dots */}
      <div className="flex items-center justify-center gap-2 mt-4">
        {Array.from({ length: total }).map((_, index) => (
          <button
            key={index}
            className={`w-3 h-3 rounded-full transition-all ${
              index + 1 === current
                ? 'bg-primary scale-125'
                : index + 1 <= answeredCount
                ? 'bg-green-500'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Stats */}
      <div className="flex items-center justify-center gap-6 mt-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          Answered: {answeredCount}
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-gray-300"></span>
          Remaining: {total - answeredCount}
        </span>
      </div>
    </div>
  );
};
