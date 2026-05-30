import { DashboardHome } from './sections/DashboardHome';
import { ResumeUpload } from './sections/ResumeUpload';

interface DashboardContentProps {
  activeModule: string;
}

export const DashboardContent = ({ activeModule }: DashboardContentProps) => {
  switch (activeModule) {
    case 'home':
      return <DashboardHome />;
    case 'resume':
      return <ResumeUpload />;
    case 'interview':
      return <div className="p-8"><h2 className="text-2xl font-bold">Interview Module (Coming Soon)</h2></div>;
    case 'aptitude':
      return <div className="p-8"><h2 className="text-2xl font-bold">Aptitude Test (Coming Soon)</h2></div>;
    case 'learning':
      return <div className="p-8"><h2 className="text-2xl font-bold">Learning Resources (Coming Soon)</h2></div>;
    case 'results':
      return <div className="p-8"><h2 className="text-2xl font-bold">Results & Feedback (Coming Soon)</h2></div>;
    default:
      return <DashboardHome />;
  }
};
