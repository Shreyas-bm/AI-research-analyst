import React from 'react';
import { 
  Compass, 
  Terminal, 
  FileText, 
  Database, 
  BarChart3
} from 'lucide-react';

export type ActiveTab = 'ask' | 'runs' | 'report' | 'documents' | 'evaluation';

interface NavigationRailProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  activeRunId: string | null;
  hasCompletedReport: boolean;
  historyCount?: number;
}

export const NavigationRail: React.FC<NavigationRailProps> = ({
  activeTab,
  onSelectTab,
  activeRunId,
  hasCompletedReport
}) => {
  const navItems = [
    {
      id: 'ask' as ActiveTab,
      label: 'New Decision',
      sublabel: 'Intake & Context',
      icon: Compass,
      disabled: false,
    },
    {
      id: 'runs' as ActiveTab,
      label: 'Live Trace',
      sublabel: activeRunId ? 'Active Agent Graph' : 'Workflow Console',
      icon: Terminal,
      disabled: !activeRunId,
      badge: activeRunId ? 'RUNNING' : undefined
    },
    {
      id: 'report' as ActiveTab,
      label: 'Decision Report',
      sublabel: '14-Part Verified Band',
      icon: FileText,
      disabled: !hasCompletedReport,
      badge: hasCompletedReport ? 'READY' : undefined
    },
    {
      id: 'documents' as ActiveTab,
      label: 'Knowledge Base',
      sublabel: 'ChromaDB Local RAG',
      icon: Database,
      disabled: false,
    },
    {
      id: 'evaluation' as ActiveTab,
      label: 'Evaluation Matrix',
      sublabel: 'Benchmark Progression',
      icon: BarChart3,
      disabled: false,
    },
  ];

  return (
    <aside className="w-64 bg-[#10131C] border-r border-[#262D3D] flex flex-col justify-between shrink-0 h-screen select-none">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-[#262D3D] flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-[#2F8F8B] to-[#181D2B] border border-[#2F8F8B]/40 flex items-center justify-center text-white font-mono font-bold text-sm shadow-sm">
            DL
          </div>
          <div>
            <div className="font-serif font-bold text-base text-[#E8E9ED] tracking-tight">
              DecisionLens
            </div>
            <div className="font-mono text-[10px] text-[#2F8F8B] tracking-wider uppercase font-semibold">
              Evidence Engine v1.0
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => !item.disabled && onSelectTab(item.id)}
                disabled={item.disabled}
                className={`w-full text-left px-3.5 py-3 rounded-md transition-all flex items-start space-x-3 group relative ${
                  isActive
                    ? 'bg-[#181D2B] text-[#E8E9ED] border-l-2 border-[#2F8F8B] shadow-sm'
                    : item.disabled
                    ? 'opacity-35 cursor-not-allowed text-[#8E96A5]'
                    : 'text-[#8E96A5] hover:text-[#E8E9ED] hover:bg-[#181D2B]/60'
                }`}
              >
                <Icon
                  className={`w-4 h-4 mt-0.5 shrink-0 transition-colors ${
                    isActive ? 'text-[#2F8F8B]' : 'text-[#8E96A5] group-hover:text-[#E8E9ED]'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold tracking-wide">
                      {item.label}
                    </span>
                    {item.badge && (
                      <span className={`font-mono text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                        item.badge === 'RUNNING' 
                          ? 'bg-[#2F8F8B]/20 text-[#2F8F8B] animate-pulse' 
                          : 'bg-[#4C8B5B]/20 text-[#4C8B5B]'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <div className="font-mono text-[10px] text-[#8E96A5] truncate mt-0.5">
                    {item.sublabel}
                  </div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-[#262D3D] bg-[#141824]/60">
        <div className="flex items-center justify-between mb-2">
          <span className="font-mono text-[10px] text-[#8E96A5] uppercase tracking-wider flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#4C8B5B] inline-block animate-ping"></span>
            <span>Local Node Healthy</span>
          </span>
          <span className="font-mono text-[10px] text-[#2F8F8B] font-semibold">
            SQLite / Chroma
          </span>
        </div>
        <div className="font-mono text-[10px] text-[#8E96A5]/80 leading-tight">
          Strict Zero-Hallucination Claim Grounding Active
        </div>
      </div>
    </aside>
  );
};
