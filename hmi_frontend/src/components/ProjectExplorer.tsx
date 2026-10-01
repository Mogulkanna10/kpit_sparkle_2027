import {
  Home, FolderTree, FileText, Shield, Cpu, Puzzle, PlugZap, Play,
  Code2, Link, Search, FilePlus, History, Network, Grid,
  FlaskConical, CheckSquare, ShieldAlert, AlertTriangle, Lock,
  ListOrdered, FileCheck, Braces, ChevronRight, ChevronDown, ChevronUp
} from "lucide-react";
import { useState } from "react";

type TreeItemProps = {
  name: string;
  icon: React.ElementType;
  children?: React.ReactNode;
  defaultOpen?: boolean;
  isActive?: boolean;
  depth?: number;
  onClick?: () => void;
};

function TreeItem({ name, icon: Icon, children, defaultOpen = false, isActive = false, depth = 0, onClick }: TreeItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const hasChildren = !!children;
  const indent = depth * 10;

  return (
    <div>
      <div
        className={`flex items-center py-1 pr-2 cursor-pointer text-[12px] transition-colors select-none ${
          isActive
            ? 'bg-[#135471] text-white border-l-2 border-teal-400'
            : 'text-[#b0cad8] hover:bg-[#165a78] hover:text-white border-l-2 border-transparent'
        }`}
        style={{ paddingLeft: `${8 + indent}px` }}
        onClick={() => {
          if (hasChildren) setIsOpen(!isOpen);
          if (onClick) onClick();
        }}
      >
        <div className="w-4 h-4 flex items-center justify-center mr-1 shrink-0">
          {hasChildren ? (
            isOpen ? <ChevronDown className="w-3 h-3 opacity-60" /> : <ChevronRight className="w-3 h-3 opacity-60" />
          ) : null}
        </div>
        <Icon className={`w-3.5 h-3.5 mr-1.5 shrink-0 ${isActive ? 'text-teal-300' : 'text-[#7aabb8]'}`} />
        <span className="truncate">{name}</span>
      </div>
      {hasChildren && isOpen && (
        <div>{children}</div>
      )}
    </div>
  );
}


export default function ProjectExplorer({
  activeMenu,
  onMenuSelect,
}: {
  activeMenu: string;
  onMenuSelect: (m: string) => void;
}) {
  const [projectOpen, setProjectOpen] = useState(false);
  const [repoOpen, setRepoOpen] = useState(false);

  const item = (name: string, icon: React.ElementType, depth = 1) => (
    <TreeItem
      key={name}
      name={name}
      icon={icon}
      depth={depth}
      isActive={activeMenu === name}
      onClick={() => onMenuSelect(name)}
    />
  );

  return (
    <div className="h-full flex flex-col bg-[#0f4a66] overflow-hidden">
      {/* AURA-Impact branding in sidebar */}
      <div className="px-3 py-2 border-b border-[#1a5f7a]">
        <div className="text-xs font-bold text-white">AURA-Impact</div>
        <div className="text-[9px] text-[#7aabb8] mt-0.5">Automotive Impact Analysis</div>
      </div>

      {/* Project dropdown */}
      <div className="px-3 pt-2 pb-1">
        <div className="text-[9px] font-semibold text-[#5a8a9f] uppercase tracking-wider mb-1">Project</div>
        <button
          onClick={() => setProjectOpen(!projectOpen)}
          className="w-full flex items-center justify-between bg-white/10 hover:bg-white/15 border border-white/10 rounded px-2 py-1 text-xs text-white transition"
        >
          <span>ADAS Demonstrator</span>
          {projectOpen ? <ChevronUp className="w-3 h-3 text-gray-400" /> : <ChevronDown className="w-3 h-3 text-gray-400" />}
        </button>
      </div>

      {/* Repository dropdown */}
      <div className="px-3 pb-2">
        <div className="text-[9px] font-semibold text-[#5a8a9f] uppercase tracking-wider mb-1">Repository</div>
        <button
          onClick={() => setRepoOpen(!repoOpen)}
          className="w-full flex items-center justify-between bg-white/10 hover:bg-white/15 border border-white/10 rounded px-2 py-1 text-xs text-white transition"
        >
          <span>Demo Dataset</span>
          {repoOpen ? <ChevronUp className="w-3 h-3 text-gray-400" /> : <ChevronDown className="w-3 h-3 text-gray-400" />}
        </button>
      </div>

      {/* Search */}
      <div className="px-3 pb-2 border-b border-[#1a5f7a]">
        <div className="flex items-center bg-white/10 border border-white/10 rounded px-2 py-1">
          <Search className="w-3 h-3 text-[#7aabb8] mr-1.5 shrink-0" />
          <input
            type="text"
            placeholder="Search this repository..."
            className="flex-1 bg-transparent text-white placeholder-[#7aabb8] text-[11px] outline-none"
          />
        </div>
        <p className="text-[9px] text-[#5a8a9f] mt-1">Press Enter to search in this repository</p>
      </div>

      {/* Tree */}
      <div className="flex-1 overflow-y-auto py-1" style={{ scrollbarWidth: 'thin', scrollbarColor: '#1a5f7a transparent' }}>
        {item('Home', Home, 0)}

        <TreeItem name="Requirements" icon={FolderTree} defaultOpen depth={0}>
          {item('System Requirements', FileText)}
          {item('Software Requirements', FileText)}
          {item('Safety Requirements', Shield)}
        </TreeItem>

        <TreeItem name="Architecture" icon={FolderTree} defaultOpen depth={0}>
          {item('ECUs', Cpu)}
          {item('Software Components', Puzzle)}
          {item('Ports', PlugZap)}
          {item('Runnables', Play)}
        </TreeItem>

        <TreeItem name="Source Code" icon={FolderTree} defaultOpen depth={0}>
          {item('C Functions', Code2)}
          {item('C++ Functions', Code2)}
          {item('RTE Interfaces', Link)}
        </TreeItem>

        <TreeItem name="Change Analysis" icon={FolderTree} defaultOpen depth={0}>
          {item('Current Analysis', Search)}
          {item('Change Seeds', FilePlus)}
          {item('Analysis History', History)}
        </TreeItem>

        <TreeItem name="Traceability" icon={FolderTree} defaultOpen depth={0}>
          {item('Impact Tree', Network)}
          {item('Traceability Matrix', Grid)}
        </TreeItem>

        <TreeItem name="Testing" icon={FolderTree} defaultOpen depth={0}>
          {item('Test Cases', FlaskConical)}
          {item('Regression Selection', CheckSquare)}
          {item('Safety Tests', ShieldAlert)}
        </TreeItem>

        <TreeItem name="Safety" icon={FolderTree} defaultOpen depth={0}>
          {item('ASIL Analysis', AlertTriangle)}
          {item('Safety Gate', Lock)}
        </TreeItem>

        <TreeItem name="Evidence" icon={FolderTree} defaultOpen depth={0}>
          {item('Decision Trail', ListOrdered)}
          {item('Audit Evidence', FileCheck)}
          {item('Raw JSON', Braces)}
        </TreeItem>
      </div>
    </div>
  );
}
