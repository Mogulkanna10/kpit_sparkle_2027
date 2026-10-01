import { Shield, ChevronDown, User, Settings, HelpCircle } from "lucide-react";

interface CommandBarProps {
  analysisData: any;
  isLoading: boolean;
}

export default function CommandBar({ analysisData, isLoading }: CommandBarProps) {
  return (
    <div className="h-12 bg-[#0b3d54] text-white flex items-center px-4 justify-between select-none shrink-0 z-50 shadow-md">
      {/* Left: Logo */}
      <div className="flex items-center space-x-8">
        <div className="flex items-center space-x-2.5">
          <Shield className="w-6 h-6 text-teal-400" />
          <div className="flex flex-col leading-none">
            <span className="text-sm font-bold tracking-wide">AURA-Impact</span>
            <span className="text-[9px] text-gray-400 tracking-wider">Automotive Impact Analysis</span>
          </div>
        </div>

        {/* Project / Repo selectors */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="text-gray-400">Project:</span>
            <div className="flex items-center bg-white/10 hover:bg-white/20 border border-white/20 text-white px-2.5 py-1 rounded cursor-pointer transition">
              <span className="mr-1.5">ADAS Demonstrator</span>
              <ChevronDown className="w-3 h-3 text-gray-300" />
            </div>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="text-gray-400">Repository:</span>
            <div className="flex items-center bg-white/10 hover:bg-white/20 border border-white/20 text-white px-2.5 py-1 rounded cursor-pointer transition">
              <span className="mr-1.5">Demo Dataset</span>
              <ChevronDown className="w-3 h-3 text-gray-300" />
            </div>
          </div>
        </div>
      </div>

      {/* Right: Status + User */}
      <div className="flex items-center space-x-5 text-xs">
        {/* Analysis status */}
        <div className="flex flex-col items-end leading-tight">
          <div className="flex items-center space-x-1.5">
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-400 animate-pulse' : analysisData ? 'bg-green-400' : 'bg-gray-400'}`}></div>
            <span className="font-medium">{isLoading ? 'Running Analysis...' : analysisData ? 'Analysis Completed' : 'Ready'}</span>
          </div>
          {analysisData && <span className="text-[10px] text-gray-400">Oct 1, 2025 18:44</span>}
        </div>

        <div className="flex items-center space-x-1 cursor-pointer hover:bg-white/10 px-2 py-1 rounded transition">
          <div className="w-6 h-6 rounded-full bg-teal-600 flex items-center justify-center">
            <User className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-medium ml-1">Engineer</span>
          <ChevronDown className="w-3 h-3 text-gray-400" />
        </div>

        <button className="p-1.5 hover:bg-white/10 rounded transition text-gray-300 hover:text-white">
          <Settings className="w-4 h-4" />
        </button>
        <button className="p-1.5 hover:bg-white/10 rounded transition text-gray-300 hover:text-white">
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
