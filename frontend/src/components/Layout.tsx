import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Bell, Search } from 'lucide-react';

const Layout = () => {
  return (
    <div className="min-h-screen bg-darker text-gray-100 font-sans selection:bg-blue-500/30">
      <Sidebar />
      
      <div className="pl-64">
        {/* Header */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-darker/80 backdrop-blur-sm sticky top-0 z-40">
          <div className="flex items-center gap-4 text-gray-400">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search..." 
              className="bg-transparent border-none focus:outline-none text-sm w-64 text-white placeholder-gray-500"
            />
          </div>
          
          <div className="flex items-center gap-4">
            <button className="relative p-2 hover:bg-white/5 rounded-full transition-colors">
              <Bell size={20} className="text-gray-400" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-emerald-400 border border-white/20"></div>
          </div>
        </header>

        {/* Main Content */}
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
