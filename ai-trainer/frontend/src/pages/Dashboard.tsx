import { Navigation } from '../components/dashboard/Navigation';
import { DashboardHome } from '../components/dashboard/sections/DashboardHome';

export const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Navigation */}
      <Navigation />
      
      {/* Main Content Area */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <DashboardHome />
        </div>
      </main>
    </div>
  );
};
