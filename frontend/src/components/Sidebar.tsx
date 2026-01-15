import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Mic, Map, Settings, User, Bell } from 'lucide-react';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: Mic, label: 'Voice Assistant', path: '/voice' },
    { icon: Map, label: 'Navigation', path: '/map' },
  ];

  return (
    <div className="w-64 h-screen glass border-r border-white/10 flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center">
          <span className="font-bold text-white">I</span>
        </div>
        <span className="font-bold text-lg tracking-tight">ICT Innovation</span>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        <div className="text-xs font-semibold text-gray-500 uppercase px-4 mb-2">Menu</div>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
            >
              <item.icon size={20} className={isActive ? 'text-blue-400' : ''} />
              <span>{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute left-0 w-1 h-8 bg-blue-500 rounded-r-full"
                />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5 space-y-2">
        <div className="text-xs font-semibold text-gray-500 uppercase px-4 mb-2">System</div>
        <button className="sidebar-link w-full text-left">
          <Settings size={20} />
          <span>Settings</span>
        </button>
        <button className="sidebar-link w-full text-left">
          <User size={20} />
          <span>Profile</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
