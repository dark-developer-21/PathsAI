import { useState } from 'react';
import { Mic, Send, Volume2 } from 'lucide-react';
import { motion } from 'framer-motion';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold text-white">Voice Assistant</h1>
        <p className="text-gray-400 text-sm">Interactive AI voice control interface</p>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Visualizer Area */}
        <div className="lg:col-span-2 glass-card flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
          
          {/* Audio Visualizer Circle */}
          <div className="relative z-10">
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsListening(!isListening)}
              className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 ${
                isListening 
                  ? 'bg-red-500 shadow-[0_0_50px_rgba(239,68,68,0.4)]' 
                  : 'bg-blue-600 shadow-[0_0_30px_rgba(37,99,235,0.3)]'
              }`}
            >
              <Mic size={40} className="text-white" />
            </motion.button>
            
            {/* Ripple Effects */}
            {isListening && (
              <>
                <div className="absolute inset-0 rounded-full border border-red-500/30 animate-ping opacity-75"></div>
                <div className="absolute -inset-4 rounded-full border border-red-500/20 animate-pulse"></div>
              </>
            )}
          </div>

          <div className="mt-8 text-center">
            <h2 className="text-2xl font-light text-white mb-2">
              {isListening ? "Listening..." : "Tap to Speak"}
            </h2>
            <p className="text-gray-400 max-w-md mx-auto">
              Try saying "Find the nearest exit" or "Where am I?"
            </p>
          </div>
        </div>

        {/* Chat History */}
        <div className="glass-card flex flex-col">
          <div className="p-4 border-b border-white/5 flex items-center justify-between">
            <h3 className="font-semibold">Conversation</h3>
            <Volume2 size={18} className="text-gray-400" />
          </div>
          
          <div className="flex-1 p-4 space-y-4 overflow-y-auto">
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white px-4 py-2 rounded-2xl rounded-tr-sm text-sm max-w-[80%]">
                Where is the robotics lab?
              </div>
            </div>
            <div className="flex justify-start">
              <div className="bg-white/10 text-gray-200 px-4 py-2 rounded-2xl rounded-tl-sm text-sm max-w-[80%] border border-white/5">
                The robotics lab is located on the second floor, room 204. Would you like navigation instructions?
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-white/5">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Type a message..." 
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500"
              />
              <button className="absolute right-2 top-2 p-1 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors">
                <Send size={16} className="text-white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistant;
