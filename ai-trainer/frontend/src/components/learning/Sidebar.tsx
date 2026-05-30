import { useState } from 'react';
import type { Topic } from '../../types/learning';
import { getProgress } from '../../data/aptitudeData';

interface SidebarProps {
  topics: Topic[];
  activeTopicId: number | null;
  onSelectTopic: (topicId: number) => void;
}

export const Sidebar = ({ topics, activeTopicId, onSelectTopic }: SidebarProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);

  const filteredTopics = topics.filter(topic =>
    topic.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group topics by level
  const groupedTopics = {
    Beginner: filteredTopics.filter(t => t.level === 'Beginner'),
    Intermediate: filteredTopics.filter(t => t.level === 'Intermediate'),
    Hard: filteredTopics.filter(t => t.level === 'Hard')
  };

  const levelColors = {
    Beginner: 'bg-green-100 text-green-700',
    Intermediate: 'bg-yellow-100 text-yellow-700',
    Hard: 'bg-red-100 text-red-700'
  };

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="lg:hidden fixed top-20 left-4 z-50 p-2 bg-white rounded-lg shadow-lg border border-gray-200"
      >
        <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Mobile Overlay */}
      {!isCollapsed && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsCollapsed(true)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-16 left-0 h-[calc(100vh-4rem)] w-72 bg-white border-r border-gray-200 z-40 transition-transform duration-300 overflow-hidden ${
          isCollapsed ? '-translate-x-full lg:translate-x-0' : 'translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800 mb-3">📚 Aptitude Topics</h2>
            
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 pl-10 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <svg
                className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Topics List */}
          <div className="flex-1 overflow-y-auto p-4">
            {Object.entries(groupedTopics).map(([level, levelTopics]) => (
              levelTopics.length > 0 && (
                <div key={level} className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`px-2 py-1 text-xs font-bold rounded-full ${levelColors[level as keyof typeof levelColors]}`}>
                      {level}
                    </span>
                    <span className="text-xs text-gray-400">({levelTopics.length})</span>
                  </div>

                  <div className="space-y-2">
                    {levelTopics.map((topic) => {
                      const progress = getProgress(topic.id);
                      const isActive = activeTopicId === topic.id;

                      return (
                        <button
                          key={topic.id}
                          onClick={() => {
                            onSelectTopic(topic.id);
                            setIsCollapsed(true);
                          }}
                          className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all text-left ${
                            isActive
                              ? 'bg-primary-light border-l-4 border-primary'
                              : 'hover:bg-gray-50 border-l-4 border-transparent'
                          }`}
                        >
                          <span className="text-2xl">{topic.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium truncate ${isActive ? 'text-primary' : 'text-gray-800'}`}>
                              {topic.name}
                            </p>
                            {progress && (
                              <div className="flex items-center gap-2 mt-1">
                                {progress.completed && (
                                  <span className="text-xs text-green-600">✓</span>
                                )}
                                <span className="text-xs text-gray-400">
                                  Best: {progress.bestScore}%
                                </span>
                              </div>
                            )}
                          </div>
                          {isActive && (
                            <div className="w-1.5 h-6 bg-primary rounded-full"></div>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )
            ))}

            {filteredTopics.length === 0 && (
              <div className="text-center py-8">
                <span className="text-4xl mb-2 block">🔍</span>
                <p className="text-sm text-gray-500">No topics found</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="bg-gradient-to-r from-primary-light to-white rounded-lg p-4">
              <p className="text-xs font-bold text-gray-800 mb-1">💡 Pro Tip</p>
              <p className="text-xs text-gray-600">
                Complete quizzes to track your progress and identify weak areas.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
