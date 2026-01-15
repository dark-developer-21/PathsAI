import { Activity, Eye, Cpu, Wifi } from 'lucide-react';

const StatCard = ({ title, value, subtext, icon: Icon, color }: any) => (
  <div className="glass-card p-6 relative overflow-hidden group">
    <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity ${color}`}>
      <Icon size={80} />
    </div>
    <div className="relative z-10">
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg bg-white/5 ${color} bg-opacity-20`}>
          <Icon size={20} className={color.replace('bg-', 'text-')} />
        </div>
        <h3 className="text-gray-400 font-medium text-sm">{title}</h3>
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-gray-500">{subtext}</div>
    </div>
  </div>
);

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold text-white">System Overview</h1>
        <p className="text-gray-400 text-sm">Real-time AI monitoring and analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Active Cameras" 
          value="4" 
          subtext="All systems operational" 
          icon={Eye} 
          color="text-blue-400" 
        />
        <StatCard 
          title="AI Processing" 
          value="120 FPS" 
          subtext="YOLOv8 + SAM Running" 
          icon={Cpu} 
          color="text-purple-400" 
        />
        <StatCard 
          title="System Load" 
          value="42%" 
          subtext="Optimal performance" 
          icon={Activity} 
          color="text-emerald-400" 
        />
        <StatCard 
          title="Network" 
          value="24ms" 
          subtext="Low latency connection" 
          icon={Wifi} 
          color="text-amber-400" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Feed */}
        <div className="lg:col-span-2 glass-card p-1 min-h-[400px] flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-white/5">
            <h3 className="font-semibold text-lg">Live Feed - Camera 01</h3>
            <span className="px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 border border-red-500/20 animate-pulse">LIVE</span>
          </div>
          <div className="flex-1 bg-black/50 m-1 rounded-xl relative overflow-hidden flex items-center justify-center group">
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-60"></div>
            
            {/* Grid Overlay */}
            <div className="absolute inset-0 opacity-20" 
                 style={{backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '40px 40px'}}>
            </div>

            {/* Simulated Detection Box */}
            <div className="absolute top-1/3 left-1/4 w-32 h-48 border-2 border-emerald-500 rounded flex flex-col items-center justify-center">
               <div className="absolute -top-6 left-0 bg-emerald-500 text-black text-xs px-2 py-0.5 font-bold rounded-t">Person 98%</div>
            </div>

            <p className="text-gray-500 z-10 flex flex-col items-center gap-2">
              <Eye size={40} className="opacity-50" />
              <span>Waiting for video stream...</span>
            </p>
          </div>
        </div>

        {/* Recent Events */}
        <div className="glass-card p-0 flex flex-col">
           <div className="p-4 border-b border-white/5">
            <h3 className="font-semibold text-lg">Recent Detections</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400">
                  <User size={18} />
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-200">Person Detected</div>
                  <div className="text-xs text-gray-500">Camera 01 • {i * 2} min ago</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
