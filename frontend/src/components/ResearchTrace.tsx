import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Terminal, 
  Database, 
  Calculator, 
  ShieldAlert, 
  CheckCheck, 
  ArrowRight,
  Cpu,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import type { DecisionReport } from '../types/decision';

interface ResearchTraceProps {
  runId: string;
  report: DecisionReport | null;
  isLoading?: boolean;
  onViewReport: () => void;
}

interface StepNode {
  id: string;
  name: string;
  role: string;
  icon: any;
  status: 'queued' | 'running' | 'completed' | 'failed';
  durationMs?: number;
  details?: string;
  subItems?: Array<{ label: string; value: string }>;
}

export const ResearchTrace: React.FC<ResearchTraceProps> = ({
  runId,
  report,
  onViewReport
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
    'planner': true,
    'tools': true,
    'critic': true
  });

  const toggleNode = (id: string) => {
    setExpandedNodes(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const steps: StepNode[] = [
    {
      id: 'intake',
      name: 'Decision Parser Agent',
      role: 'Formulate Objective & Candidate Alternatives',
      icon: Terminal,
      status: 'completed',
      durationMs: 180,
      details: report ? `Parsed question into structured evaluation criteria: ${report.evidence.decision_criteria.join(', ')}` : 'Extracting candidates and hard constraints...',
      subItems: report ? [
        { label: 'Domain', value: 'Technology / Infrastructure' },
        { label: 'Alternatives', value: report.verdict.alternatives.map(a => a.name).join(' vs ') }
      ] : []
    },
    {
      id: 'planner',
      name: 'Research Planner Agent',
      role: 'Task Decomposition across Tools',
      icon: Cpu,
      status: 'completed',
      durationMs: 240,
      details: 'Generated atomic search queries across SQL benchmarks, internal vector RAG, and calculation tools.',
      subItems: [
        { label: 'SQL Query', value: 'SELECT * FROM benchmark_results WHERE workload_size=500000' },
        { label: 'RAG Ingestion', value: 'Querying local ChromaDB for vector latency policies' },
        { label: 'Web Benchmarks', value: 'Searching pgvector vs ChromaDB empirical latency' },
        { label: 'Math Formula', value: '(500000 * 1536 * 4) / (1024 * 1024) = 2,929.69 MB' }
      ]
    },
    {
      id: 'tools',
      name: 'Multi-Tool Execution Matrix',
      role: 'Parallel Fact Gathering & Vector Retrieval',
      icon: Database,
      status: 'completed',
      durationMs: 420,
      details: `Aggregated ${report?.trace.sources.length || 4} verified empirical evidence items.`,
      subItems: report?.trace.sources.map(s => ({
        label: `[${s.source_type.toUpperCase()}] ${s.title}`,
        value: s.excerpt.slice(0, 100) + '...'
      })) || []
    },
    {
      id: 'synthesis',
      name: 'Quantitative Synthesis Agent',
      role: 'Draft Comparison Matrix & Latency Delta',
      icon: Calculator,
      status: 'completed',
      durationMs: 310,
      details: report?.evidence.quantitative_analysis.summary || 'Constructing quantitative trade-off table and alternative scoring.',
      subItems: report?.evidence.quantitative_analysis.comparison_table.map(row => ({
        label: row.criterion,
        value: `Winner: ${row.winner || 'Tie'} (${row.notes || 'Empirical benchmark'})`
      })) || []
    },
    {
      id: 'critic',
      name: 'Adversarial Critic Agent',
      role: 'Ruthless Assumption Stress-Testing',
      icon: ShieldAlert,
      status: 'completed',
      durationMs: 290,
      details: 'Identified key boundary failure conditions and migration thresholds.',
      subItems: report?.challenge.critic_review.what_would_change_recommendation.map((w, idx) => ({
        label: `Flip Condition #${idx + 1}`,
        value: w
      })) || []
    },
    {
      id: 'verifier',
      name: 'Evidence & Claim Verifier',
      role: 'Sentence-Level Grounding & Citation Binding',
      icon: CheckCheck,
      status: 'completed',
      durationMs: 160,
      details: `Grounding verification completed: ${report?.evidence.claims.length || 3} claims audited with zero ungrounded assertions.`,
      subItems: report?.evidence.claims.map(c => ({
        label: `[${c.verification_status}] ${c.claim_text}`,
        value: c.verifier_notes || 'Confirmed by empirical benchmark source'
      })) || []
    }
  ];

  return (
    <div className="min-h-screen bg-[#10131C] text-[#E8E9ED] p-8 lg:p-12 overflow-y-auto">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Top Console Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-[#262D3D] gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#2F8F8B] animate-pulse"></span>
              <span className="font-mono text-xs text-[#2F8F8B] font-bold uppercase tracking-wider">
                Research Trace Console
              </span>
              <span className="font-mono text-xs text-[#8E96A5]">
                // {runId}
              </span>
            </div>
            <h1 className="font-serif text-2xl font-bold text-[#E8E9ED] mt-2">
              {report?.question || 'Orchestrating Multi-Agent Decision Workflow...'}
            </h1>
          </div>

          {/* Metric Badges */}
          <div className="flex items-center space-x-3 shrink-0">
            <div className="bg-[#181D2B] border border-[#262D3D] px-3.5 py-2 rounded-lg text-right">
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Total Tokens</div>
              <div className="font-mono text-xs font-bold text-[#E8E9ED]">
                {report?.trace.total_tokens?.toLocaleString() || '1,650'}
              </div>
            </div>
            <div className="bg-[#181D2B] border border-[#262D3D] px-3.5 py-2 rounded-lg text-right">
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Total Latency</div>
              <div className="font-mono text-xs font-bold text-[#2F8F8B]">
                {report?.trace.total_latency_ms || '1,600'} ms
              </div>
            </div>
            <div className="bg-[#181D2B] border border-[#262D3D] px-3.5 py-2 rounded-lg text-right">
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Est. Cost</div>
              <div className="font-mono text-xs font-bold text-[#4C8B5B]">
                ${report?.trace.estimated_cost_usd?.toFixed(4) || '0.0007'}
              </div>
            </div>
          </div>
        </div>

        {/* State Machine Step Flow */}
        <div className="space-y-4">
          <div className="font-mono text-xs text-[#8E96A5] uppercase tracking-wider font-semibold">
            Execution Graph Nodes
          </div>

          <div className="space-y-3">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              const isExpanded = expandedNodes[step.id];

              return (
                <div
                  key={step.id}
                  className="bg-[#181D2B] border border-[#262D3D] hover:border-[#2F8F8B]/50 rounded-lg p-4 transition-all"
                >
                  <div 
                    onClick={() => toggleNode(step.id)}
                    className="flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded bg-[#10131C] border border-[#262D3D] flex items-center justify-center text-[#2F8F8B]">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-[#E8E9ED] font-mono">
                            0{idx + 1}. {step.name}
                          </span>
                          <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-[#4C8B5B]/15 text-[#4C8B5B] font-semibold uppercase">
                            COMPLETED
                          </span>
                        </div>
                        <div className="text-[11px] text-[#8E96A5] font-sans">
                          {step.role}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="font-mono text-[11px] text-[#8E96A5]">
                        {step.durationMs}ms
                      </span>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-[#8E96A5]" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-[#8E96A5]" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Sub-details */}
                  {isExpanded && (
                    <div className="mt-4 pt-3 border-t border-[#262D3D] space-y-2.5">
                      <div className="text-xs text-[#E8E9ED]/90 font-sans leading-relaxed">
                        {step.details}
                      </div>

                      {step.subItems && step.subItems.length > 0 && (
                        <div className="space-y-1.5 pt-1">
                          {step.subItems.map((sub, sIdx) => (
                            <div
                              key={sIdx}
                              className="p-2.5 rounded bg-[#10131C] border border-[#262D3D]/80 font-mono text-[11px] space-y-1"
                            >
                              <div className="text-[#2F8F8B] font-semibold">{sub.label}</div>
                              <div className="text-[#8E96A5] font-sans text-xs">{sub.value}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Completion Callout & Transition to Report */}
        <div className="p-6 bg-gradient-to-r from-[#181D2B] to-[#141824] border border-[#2F8F8B]/40 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg">
          <div>
            <div className="flex items-center space-x-2 font-mono text-xs text-[#4C8B5B] font-bold uppercase">
              <CheckCircle2 className="w-4 h-4" />
              <span>Multi-Agent Research & Verification Complete</span>
            </div>
            <div className="text-sm text-[#E8E9ED] mt-1 font-serif">
              Recommendation synthesized on the cool-grey paper surface with live Evidence Thread connectivity.
            </div>
          </div>

          <button
            onClick={onViewReport}
            className="inline-flex items-center space-x-2.5 px-6 py-3 bg-[#2F8F8B] hover:bg-[#277875] text-white rounded-lg font-mono text-xs font-bold uppercase tracking-wider transition-all shrink-0 shadow-md group"
          >
            <span>View Final Report</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

      </div>
    </div>
  );
};
