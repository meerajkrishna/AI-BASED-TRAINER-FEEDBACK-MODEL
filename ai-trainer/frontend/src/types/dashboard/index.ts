export interface DashboardModule {
  id: string;
  title: string;
  description: string;
  path: string;
  status: 'Ready' | 'Locked' | 'Available';
  progress: number;
}

export interface UserStats {
  resumeStatus: string;
  testsCompleted: number;
  overallScore: number;
  interviewsDone: number;
}
