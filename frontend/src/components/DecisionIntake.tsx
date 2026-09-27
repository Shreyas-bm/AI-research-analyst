import React, { useState, useRef } from 'react';
import { 
  Compass, 
  UploadCloud, 
  X, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  ArrowRight,
  ShieldCheck,
  Layers
} from 'lucide-react';
import { uploadDocument } from '../services/api';

interface DecisionIntakeProps {
  onStartResearch: (data: {
    question: string;
    context: Record<string, any>;
    constraints: string[];
    preferred_alternatives: string[];
    document_ids: string[];
  }) => void;
  isSubmitting: boolean;
}

const PRESET_QUESTIONS = [
  {
    title: "Vector Store Architecture",
    question: "Should we choose PostgreSQL + pgvector or PostgreSQL + ChromaDB for semantic search?",
    constraints: ["Low operational complexity", "ACID compliance", "Zero dual-write drift"],
    alts: ["PostgreSQL + pgvector", "PostgreSQL + ChromaDB"]
  },
  {
    title: "Workflow Orchestrator",
    question: "Should we choose Temporal.io or Celery with Redis for long-running agent workflows?",
    constraints: ["Durable execution state", "Crash-resilient recovery", "Low maintenance"],
    alts: ["Temporal.io", "Celery + Redis"]
  },
  {
    title: "Frontend Application Architecture",
    question: "Should our internal analytical console be built in Vite + Vanilla CSS or Next.js App Router?",
    constraints: ["Instant HMR velocity", "Zero hydration errors", "Lightweight bundle"],
    alts: ["Vite SPA", "Next.js App Router"]
  },
  {
    title: "Embedding Model Deployment",
    question: "Should we route production embeddings to local all-MiniLM-L6-v2 or OpenAI text-embedding-3-small?",
    constraints: ["Complete offline privacy", "Zero marginal API bills", "Sub-20ms p95 latency"],
    alts: ["Local all-MiniLM-L6-v2", "OpenAI text-embedding-3-small"]
  }
];

export const DecisionIntake: React.FC<DecisionIntakeProps> = ({
  onStartResearch,
  isSubmitting
}) => {
  const [question, setQuestion] = useState('');
  const [showContext, setShowContext] = useState(false);
  const [budget, setBudget] = useState('');
  const [workload, setWorkload] = useState('');
  const [teamSize, setTeamSize] = useState('');
  const [constraints, setConstraints] = useState<string[]>([]);
  const [newConstraint, setNewConstraint] = useState('');
  const [alternatives, setAlternatives] = useState<string[]>([]);
  const [newAlt, setNewAlt] = useState('');
  const [uploadedDocs, setUploadedDocs] = useState<Array<{ id: string; name: string; chunks: number }>>([]);
  const [isUploading, setIsUploading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleApplyPreset = (p: typeof PRESET_QUESTIONS[0]) => {
    setQuestion(p.question);
    setConstraints(p.constraints);
    setAlternatives(p.alts);
    setShowContext(true);
  };

  const handleAddConstraint = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    if (newConstraint.trim() && !constraints.includes(newConstraint.trim())) {
      setConstraints([...constraints, newConstraint.trim()]);
      setNewConstraint('');
    }
  };

  const handleRemoveConstraint = (item: string) => {
    setConstraints(constraints.filter(c => c !== item));
  };

  const handleAddAlt = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    if (newAlt.trim() && !alternatives.includes(newAlt.trim())) {
      setAlternatives([...alternatives, newAlt.trim()]);
      setNewAlt('');
    }
  };

  const handleRemoveAlt = (item: string) => {
    setAlternatives(alternatives.filter(a => a !== item));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const res = await uploadDocument(file);
      setUploadedDocs(prev => [...prev, { id: res.document_id, name: res.filename, chunks: res.chunk_count }]);
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    onStartResearch({
      question: question.trim(),
      context: {
        budget_usd: budget ? Number(budget) : undefined,
        workload_estimate: workload || undefined,
        team_size: teamSize ? Number(teamSize) : undefined
      },
      constraints,
      preferred_alternatives: alternatives,
      document_ids: uploadedDocs.map(d => d.id)
    });
  };

  return (
    <div className="min-h-screen bg-[#E9ECEC] text-[#1A1D22] p-8 lg:p-12 overflow-y-auto">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header Title */}
        <div>
          <div className="inline-flex items-center space-x-2 font-mono text-[11px] uppercase tracking-wider text-[#2F8F8B] font-bold px-2.5 py-1 bg-[#2F8F8B]/10 rounded border border-[#2F8F8B]/20 mb-3">
            <Compass className="w-3.5 h-3.5" />
            <span>Decision Intake Protocol</span>
          </div>
          <h1 className="font-serif text-3xl lg:text-4xl font-bold text-[#1A1D22] tracking-tight leading-tight">
            What technical or architectural decision are you trying to resolve?
          </h1>
          <p className="text-[#5D646F] text-sm mt-2 font-sans">
            DecisionLens builds a full research plan, queries empirical SQL benchmark tables, parses internal documents, runs quantitative math, and stress-tests its conclusions with an adversarial critic.
          </p>
        </div>

        {/* Preset Quick Starters */}
        <div className="space-y-2">
          <div className="font-mono text-[11px] font-semibold text-[#5D646F] uppercase tracking-wider">
            Quick Scenario Presets
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {PRESET_QUESTIONS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className="text-left p-3 rounded-lg bg-[#F5F6F5] hover:bg-white border border-[#D1D7D7] hover:border-[#2F8F8B] transition-all shadow-2xs group"
              >
                <div className="flex items-center justify-between text-xs font-bold text-[#1A1D22] group-hover:text-[#2F8F8B]">
                  <span>{preset.title}</span>
                  <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div className="text-[11px] text-[#5D646F] truncate mt-1">
                  {preset.question}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Intake Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="p-6 bg-white rounded-xl border border-[#D1D7D7] shadow-sm space-y-5">
            
            {/* Main Question Textarea */}
            <div>
              <label htmlFor="decision-question-input" className="block font-mono text-xs uppercase font-bold text-[#1A1D22] mb-2 tracking-wide">
                Decision Objective <span className="text-[#C1553B]">*</span>
              </label>
              <textarea
                id="decision-question-input"
                rows={3}
                required
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Should we adopt PostgreSQL + pgvector or PostgreSQL + ChromaDB for local embedding search given a 500k vector corpus?"
                className="w-full font-serif text-lg p-4 rounded-lg bg-[#F5F6F5] border border-[#D1D7D7] focus:bg-white focus:border-[#2F8F8B] focus:ring-1 focus:ring-[#2F8F8B] outline-none transition-all placeholder:text-[#8E96A5]/70"
              />
            </div>

            {/* Candidate Alternatives */}
            <div>
              <label className="block font-mono text-xs uppercase font-bold text-[#1A1D22] mb-1.5">
                Candidate Alternatives to Compare
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {alternatives.map((alt, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center space-x-1.5 px-3 py-1 bg-[#2F8F8B]/10 text-[#2F8F8B] border border-[#2F8F8B]/30 rounded-full font-mono text-xs font-semibold"
                  >
                    <span>{alt}</span>
                    <button type="button" onClick={() => handleRemoveAlt(alt)} className="hover:text-[#C1553B]">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newAlt}
                  onChange={(e) => setNewAlt(e.target.value)}
                  onKeyDown={handleAddAlt}
                  placeholder="Type an alternative (e.g. PostgreSQL + pgvector) and press Enter"
                  className="flex-1 text-xs px-3.5 py-2.5 bg-[#F5F6F5] border border-[#D1D7D7] rounded-md focus:bg-white focus:border-[#2F8F8B] outline-none"
                />
                <button
                  type="button"
                  onClick={handleAddAlt}
                  className="px-3.5 py-2 bg-[#F5F6F5] hover:bg-[#E9ECEC] border border-[#D1D7D7] rounded-md text-xs font-bold font-mono text-[#1A1D22]"
                >
                  Add
                </button>
              </div>
            </div>

            {/* Collapsible Context & Constraints Section */}
            <div className="border-t border-[#E9ECEC] pt-4">
              <button
                type="button"
                onClick={() => setShowContext(!showContext)}
                className="flex items-center justify-between w-full text-left font-mono text-xs font-bold text-[#5D646F] hover:text-[#1A1D22] select-none"
              >
                <span className="flex items-center space-x-2">
                  <Layers className="w-3.5 h-3.5 text-[#2F8F8B]" />
                  <span>ADD CONSTRAINTS, BUDGET & WORKLOAD PARAMETERS</span>
                </span>
                {showContext ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showContext && (
                <div className="mt-4 space-y-4 pt-2">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block font-mono text-[11px] text-[#5D646F] mb-1">
                        Monthly Budget (USD)
                      </label>
                      <input
                        type="number"
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        placeholder="e.g. 500"
                        className="w-full text-xs p-2.5 bg-[#F5F6F5] border border-[#D1D7D7] rounded-md focus:bg-white focus:border-[#2F8F8B] outline-none font-mono"
                      />
                    </div>
                    <div>
                      <label className="block font-mono text-[11px] text-[#5D646F] mb-1">
                        Workload Size / Vectors
                      </label>
                      <input
                        type="text"
                        value={workload}
                        onChange={(e) => setWorkload(e.target.value)}
                        placeholder="e.g. 500,000 vectors"
                        className="w-full text-xs p-2.5 bg-[#F5F6F5] border border-[#D1D7D7] rounded-md focus:bg-white focus:border-[#2F8F8B] outline-none font-mono"
                      />
                    </div>
                    <div>
                      <label className="block font-mono text-[11px] text-[#5D646F] mb-1">
                        Engineering Team Size
                      </label>
                      <input
                        type="number"
                        value={teamSize}
                        onChange={(e) => setTeamSize(e.target.value)}
                        placeholder="e.g. 3"
                        className="w-full text-xs p-2.5 bg-[#F5F6F5] border border-[#D1D7D7] rounded-md focus:bg-white focus:border-[#2F8F8B] outline-none font-mono"
                      />
                    </div>
                  </div>

                  {/* Explicit Constraints Tagging */}
                  <div>
                    <label className="block font-mono text-[11px] font-bold text-[#5D646F] mb-1.5 uppercase">
                      Hard Constraints & Policies
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {constraints.map((c, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center space-x-1.5 px-3 py-1 bg-[#D9A441]/15 text-[#9E6C15] border border-[#D9A441]/40 rounded-full font-mono text-xs font-semibold"
                        >
                          <span>{c}</span>
                          <button type="button" onClick={() => handleRemoveConstraint(c)} className="hover:text-[#C1553B]">
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={newConstraint}
                        onChange={(e) => setNewConstraint(e.target.value)}
                        onKeyDown={handleAddConstraint}
                        placeholder="Type constraint (e.g. ACID compliance, sub-15ms p95) and press Enter"
                        className="flex-1 text-xs px-3.5 py-2.5 bg-[#F5F6F5] border border-[#D1D7D7] rounded-md focus:bg-white focus:border-[#2F8F8B] outline-none"
                      />
                      <button
                        type="button"
                        onClick={handleAddConstraint}
                        className="px-3.5 py-2 bg-[#F5F6F5] hover:bg-[#E9ECEC] border border-[#D1D7D7] rounded-md text-xs font-bold font-mono text-[#1A1D22]"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Optional Document Upload Zone */}
            <div className="border-t border-[#E9ECEC] pt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs uppercase font-bold text-[#1A1D22] flex items-center space-x-1.5">
                  <UploadCloud className="w-4 h-4 text-[#2F8F8B]" />
                  <span>Attach Internal Documents (PDF / Markdown / TXT)</span>
                </span>
                <span className="font-mono text-[10px] text-[#5D646F]">
                  Indexed locally in ChromaDB
                </span>
              </div>

              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-[#D1D7D7] hover:border-[#2F8F8B] rounded-lg p-4 text-center cursor-pointer transition-colors bg-[#F5F6F5] hover:bg-white group"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.md,.markdown,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="font-sans text-xs text-[#5D646F] group-hover:text-[#1A1D22]">
                  {isUploading ? (
                    <span className="font-mono text-[#2F8F8B] font-bold animate-pulse">Chunking and embedding document...</span>
                  ) : (
                    <span>Click or drag and drop architectural docs, RFCs, or benchmark sheets here</span>
                  )}
                </div>
              </div>

              {uploadedDocs.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  {uploadedDocs.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-2 rounded bg-[#F5F6F5] border border-[#D1D7D7] text-xs font-mono"
                    >
                      <span className="flex items-center space-x-2 text-[#1A1D22]">
                        <FileText className="w-3.5 h-3.5 text-[#2F8F8B]" />
                        <span>{doc.name}</span>
                      </span>
                      <span className="text-[10px] text-[#4C8B5B] font-bold">
                        {doc.chunks} chunks indexed
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Primary Submit Action */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center space-x-2 text-xs font-mono text-[#5D646F]">
              <ShieldCheck className="w-4 h-4 text-[#4C8B5B]" />
              <span>Full Audit Trace & Adversarial Stress-Testing Guaranteed</span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !question.trim()}
              className="inline-flex items-center space-x-3 px-8 py-3.5 bg-[#10131C] hover:bg-[#181D2B] text-white rounded-lg font-mono text-xs font-bold uppercase tracking-wider transition-all shadow-md hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed group"
            >
              <span>{isSubmitting ? 'Initializing Workflow...' : 'Start Research'}</span>
              <ArrowRight className="w-4 h-4 text-[#2F8F8B] group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
