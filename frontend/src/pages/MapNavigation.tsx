import { MapPin, Navigation } from 'lucide-react';

const MapNavigation = () => {
  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold text-white">Campus Navigation</h1>
          <p className="text-gray-400 text-sm">Interactive map and pathfinding</p>
        </div>
        <div className="flex gap-3">
            <select className="bg-surface border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-300 focus:outline-none">
                <option>Floor 1</option>
                <option>Floor 2</option>
                <option>Floor 3</option>
            </select>
            <button className="btn-primary flex items-center gap-2">
                <Navigation size={16} />
                <span>Start Navigation</span>
            </button>
        </div>
      </div>

      <div className="flex-1 glass-card p-1 relative overflow-hidden rounded-2xl group">
        {/* Placeholder Map Background */}
        <div className="absolute inset-0 bg-[#0f1623] pattern-grid-lg"></div>
        
        {/* Simulated Map Elements */}
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative w-3/4 h-3/4 border border-white/10 rounded-xl bg-surface/30 backdrop-blur-sm">
                
                {/* Rooms */}
                <div className="absolute top-10 left-10 w-32 h-24 border border-blue-500/30 bg-blue-500/5 rounded flex items-center justify-center">
                    <span className="text-blue-400 text-xs font-mono">Lab 101</span>
                </div>
                 <div className="absolute bottom-10 right-10 w-40 h-32 border border-purple-500/30 bg-purple-500/5 rounded flex items-center justify-center">
                    <span className="text-purple-400 text-xs font-mono">Auditorium</span>
                </div>

                {/* Path */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    <path d="M 100 100 L 300 100 L 300 300 L 500 300" stroke="#3B82F6" strokeWidth="3" fill="none" strokeDasharray="10 5" className="animate-pulse" />
                    <circle cx="100" cy="100" r="6" fill="#3B82F6" />
                    <circle cx="500" cy="300" r="6" fill="#EF4444" />
                </svg>

                {/* User Pin */}
                <div className="absolute top-[88px] left-[94px]">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-ping absolute"></div>
                    <div className="w-3 h-3 bg-blue-500 rounded-full relative border-2 border-white"></div>
                </div>

            </div>
        </div>

        {/* Floating Controls */}
        <div className="absolute bottom-6 right-6 flex flex-col gap-2">
            <button className="p-3 bg-surface hover:bg-white/10 rounded-lg shadow-lg border border-white/10 transition-colors">
                <span className="text-xl font-bold">+</span>
            </button>
            <button className="p-3 bg-surface hover:bg-white/10 rounded-lg shadow-lg border border-white/10 transition-colors">
                 <span className="text-xl font-bold">-</span>
            </button>
        </div>
      </div>
    </div>
  );
};

export default MapNavigation;
