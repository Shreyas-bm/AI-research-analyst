import React, { useState } from 'react';
import { 
  Download, 
  ShieldAlert, 
  Database, 
  FileText, 
  Globe, 
  Calculator, 
  Flame
} from 'lucide-react';
import type { DecisionReport, ClaimItem } from '../types/decision';

interface DecisionReportViewProps {
  report: DecisionReport;
  onBackToIntake?: () => void;
  onViewTrace: () => void;
}

export const DecisionReportView: React.FC<DecisionReportViewProps> = ({
  report,
  onViewTrace
}) => {
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [activeClaimId, setActiveClaimId] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<string>('all');

  const { verdict, evidence, challenge, trace } = report;

  // Filter sources
  const filteredSources = trace.sources.filter(s => {
    if (sourceFilter === 'all') return true;
    return s.source_type === sourceFilter;
  });

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'sql_result': return Database;
      case 'document': return FileText;
      case 'web': return Globe;
      case 'calculation': return Calculator;
      default: return FileText;
    }
  };

  const handleClaimClick = (claim: ClaimItem) => {
    setActiveClaimId(claim.id);
    if (claim.supporting_source_ids && claim.supporting_source_ids.length > 0) {
      setSelectedSourceId(claim.supporting_source_ids[0]);
    } else {
      setSelectedSourceId(null);
    }
  };

  const handleExportMarkdown = () => {
    const mdContent = `# DecisionLens Verified Decision Report
**Question:** ${verdict.decision_question}
**Date:** ${new Date(report.generated_at).toUTCString()}
**Confidence:** ${Math.round(verdict.confidence.score * 100)}% (${verdict.confidence.level}) - ${verdict.confidence.reasoning}

---

## 1. Recommendation Headline
${verdict.recommendation_headline}

## 2. Alternatives Evaluated
${verdict.alternatives.map(a => `- **${a.name}** (Score: ${a.score || 'N/A'}/10)\n  - Strengths: ${a.strengths.join(', ')}\n  - Weaknesses: ${a.weaknesses.join(', ')}`).join('\n')}

## 3. Quantitative Comparison Table
${evidence.quantitative_analysis.summary}

## 4. Key Trade-offs Accepted
${evidence.key_trade_offs.map(t => `- ${t}`).join('\n')}

## 5. Adversarial Critic & Stress-Testing
- **Identified Risks:** ${challenge.critic_review.identified_risks.join('; ')}
- **Counterarguments:** ${challenge.critic_review.counterarguments.join('; ')}
- **What Would Change This Recommendation:**
${challenge.critic_review.what_would_change_recommendation.map(w => `  - ${w}`).join('\n')}

## 6. Audit Trace
- Run ID: \`${trace.run_id}\`
- Tokens: ${trace.total_tokens} | Latency: ${trace.total_latency_ms}ms | Cost: $${trace.estimated_cost_usd}
`;

    const blob = new Blob([mdContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `decision-report-${trace.run_id}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-full bg-[#E9ECEC] text-[#1A1D22] p-6 lg:p-10 pb-20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Main 14-Part Report Column (8 cols) */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Top Actions Bar */}
          <div className="flex items-center justify-between border-b border-[#D1D7D7] pb-4">
            <div className="flex items-center space-x-2">
              <span className="font-mono text-[11px] text-[#2F8F8B] font-bold uppercase tracking-wider px-2.5 py-0.5 bg-[#2F8F8B]/10 rounded border border-[#2F8F8B]/20">
                Verified Decision Report
              </span>
              <span className="font-mono text-xs text-[#5D646F]">
                // {trace.run_id}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={onViewTrace}
                className="px-3 py-1.5 rounded bg-[#F5F6F5] hover:bg-white border border-[#D1D7D7] font-mono text-xs font-semibold text-[#1A1D22] transition-colors"
              >
                Inspect Graph Trace
              </button>
              <button
                onClick={handleExportMarkdown}
                className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-[#10131C] hover:bg-[#181D2B] text-white font-mono text-xs font-semibold transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Report</span>
              </button>
            </div>
          </div>

          {/* ================= BAND 1: VERDICT BAND ================= */}
          <section className="bg-white rounded-xl p-8 border border-[#D1D7D7] shadow-sm space-y-6">
            <div className="text-xs font-mono font-bold text-[#5D646F] uppercase tracking-wider">
              01 // The Decision Verdict
            </div>

            <div>
              <div className="text-xs font-mono text-[#8E96A5] uppercase tracking-wide">
                Target Question
              </div>
              <h2 className="font-serif text-xl font-semibold text-[#1A1D22] mt-1 leading-snug">
                {verdict.decision_question}
              </h2>
            </div>

            {/* Recommendation Headline */}
            <div className="p-6 rounded-xl bg-gradient-to-br from-[#F5F6F5] to-[#E9ECEC]/60 border-l-4 border-[#2F8F8B] border border-[#D1D7D7]">
              <div className="font-mono text-[11px] font-bold text-[#2F8F8B] uppercase tracking-wider mb-2">
                Synthesized Recommendation
              </div>
              <h1 className="font-serif text-2xl lg:text-3xl font-bold text-[#1A1D22] tracking-tight leading-tight">
                {verdict.recommendation_headline}
              </h1>

              {/* Confidence Indicator */}
              <div className="mt-4 pt-4 border-t border-[#D1D7D7]/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-3">
                  <div className="px-3 py-1 bg-[#2F8F8B]/15 text-[#2F8F8B] rounded-md font-mono text-xs font-bold">
                    Confidence: {Math.round(verdict.confidence.score * 100)}% ({verdict.confidence.level})
                  </div>
                </div>
                <div className="text-xs font-sans text-[#5D646F] italic">
                  {verdict.confidence.reasoning}
                </div>
              </div>
            </div>

            {/* Alternatives Considered */}
            <div className="space-y-3">
              <div className="font-mono text-xs font-bold text-[#5D646F] uppercase">
                Candidates Evaluated
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {verdict.alternatives.map((alt, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-lg bg-[#F5F6F5] border border-[#D1D7D7] space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-[#1A1D22]">
                        {alt.name}
                      </span>
                      {alt.score && (
                        <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-white border border-[#D1D7D7] font-bold text-[#2F8F8B]">
                          Score: {alt.score}/10
                        </span>
                      )}
                    </div>
                    <div className="space-y-1 text-[11px] text-[#5D646F]">
                      <div><strong className="text-[#4C8B5B]">Strengths:</strong> {alt.strengths.join(', ')}</div>
                      <div><strong className="text-[#C1553B]">Weaknesses:</strong> {alt.weaknesses.join(', ')}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* ================= BAND 2: EVIDENCE BAND ================= */}
          <section className="bg-white rounded-xl p-8 border border-[#D1D7D7] shadow-sm space-y-6">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono font-bold text-[#5D646F] uppercase tracking-wider">
                02 // Empirical Evidence & Quantitative Matrix
              </div>
              <span className="font-mono text-[10px] text-[#2F8F8B] font-bold">
                Tap claims below to link source cards
              </span>
            </div>

            {/* Grounded Factual Claims with Evidence Thread */}
            <div className="p-5 rounded-lg bg-[#F5F6F5] border border-[#D1D7D7] space-y-3">
              <div className="font-mono text-xs font-bold text-[#1A1D22] uppercase tracking-wide">
                Key Grounded Claims (Evidence Thread Active)
              </div>
              <div className="space-y-2.5">
                {evidence.claims.map((claim) => {
                  const isUnsupported = claim.verification_status === 'UNSUPPORTED';
                  const isSelected = activeClaimId === claim.id;

                  return (
                    <div
                      key={claim.id}
                      onClick={() => handleClaimClick(claim)}
                      className={`p-3 rounded-md transition-all cursor-pointer border ${
                        isSelected
                          ? 'bg-white border-[#2F8F8B] ring-1 ring-[#2F8F8B] shadow-xs'
                          : isUnsupported
                          ? 'bg-[#C1553B]/5 border-[#C1553B]/30 hover:bg-[#C1553B]/10'
                          : 'bg-white/80 border-[#D1D7D7] hover:border-[#2F8F8B]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="font-sans text-xs text-[#1A1D22] leading-relaxed">
                          <span className={isUnsupported ? 'claim-unsupported' : 'claim-target'}>
                            {claim.claim_text}
                          </span>
                        </div>
                        <span
                          className={`shrink-0 font-mono text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            claim.verification_status === 'SUPPORTED'
                              ? 'bg-[#4C8B5B]/15 text-[#4C8B5B]'
                              : claim.verification_status === 'PARTIALLY_SUPPORTED'
                              ? 'bg-[#D9A441]/15 text-[#9E6C15]'
                              : 'bg-[#C1553B]/15 text-[#C1553B]'
                          }`}
                        >
                          {claim.verification_status}
                        </span>
                      </div>
                      {claim.verifier_notes && (
                        <div className="mt-1.5 font-mono text-[10px] text-[#5D646F]">
                          // {claim.verifier_notes}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Quantitative Comparison Table */}
            <div className="space-y-3">
              <div className="font-mono text-xs font-bold text-[#1A1D22] uppercase">
                Quantitative Comparison Matrix
              </div>
              <div className="text-xs text-[#5D646F] font-sans">
                {evidence.quantitative_analysis.summary}
              </div>

              <div className="overflow-x-auto border border-[#D1D7D7] rounded-lg">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#F5F6F5] border-b border-[#D1D7D7] font-mono text-[11px] text-[#5D646F] uppercase">
                      <th className="p-3">Evaluation Criterion</th>
                      <th className="p-3">Candidate Values</th>
                      <th className="p-3">Empirical Winner</th>
                      <th className="p-3">Benchmark Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#D1D7D7]">
                    {evidence.quantitative_analysis.comparison_table.map((row, idx) => (
                      <tr key={idx} className="hover:bg-[#F5F6F5]/60 transition-colors">
                        <td className="p-3 font-semibold text-[#1A1D22] font-mono text-[11px]">
                          {row.criterion}
                        </td>
                        <td className="p-3 font-mono text-[11px] text-[#5D646F]">
                          {Object.entries(row.values).map(([k, v]) => (
                            <div key={k}><strong>{k}:</strong> {v}</div>
                          ))}
                        </td>
                        <td className="p-3">
                          <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-[#2F8F8B]/10 text-[#2F8F8B] font-bold">
                            {row.winner || 'Tie'}
                          </span>
                        </td>
                        <td className="p-3 text-[11px] text-[#5D646F]">
                          {row.notes || 'Empirical measurement'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Calculations Performed Footnotes */}
              {evidence.quantitative_analysis.calculations_performed.length > 0 && (
                <div className="p-3 rounded bg-[#F5F6F5] border border-[#D1D7D7] font-mono text-[11px] text-[#5D646F] space-y-1">
                  <div className="font-bold text-[#1A1D22] uppercase text-[10px]">Calculations Performed:</div>
                  {evidence.quantitative_analysis.calculations_performed.map((calc, idx) => (
                    <div key={idx} className="text-[#2F8F8B]">{calc}</div>
                  ))}
                </div>
              )}
            </div>

            {/* Key Trade-offs Accepted */}
            <div className="space-y-2">
              <div className="font-mono text-xs font-bold text-[#1A1D22] uppercase">
                Accepted Architectural Trade-offs
              </div>
              <ul className="space-y-1.5 list-disc list-inside text-xs text-[#5D646F] font-sans">
                {evidence.key_trade_offs.map((t, idx) => (
                  <li key={idx} className="leading-relaxed">
                    <span className="text-[#1A1D22] font-medium">{t}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* ================= BAND 3: CHALLENGE BAND ================= */}
          <section className="bg-white rounded-xl p-8 border border-[#D1D7D7] shadow-sm space-y-6">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-[#C1553B]" />
              <div className="text-xs font-mono font-bold text-[#C1553B] uppercase tracking-wider">
                03 // Adversarial Critic Review & Failure Modes
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-[#C1553B]/5 border border-[#C1553B]/30 space-y-2">
                <div className="font-mono text-xs font-bold text-[#C1553B] uppercase">
                  Identified Operational Risks
                </div>
                <ul className="space-y-1 text-xs text-[#5D646F] font-sans list-disc list-inside">
                  {challenge.critic_review.identified_risks.map((risk, idx) => (
                    <li key={idx}>{risk}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-lg bg-[#D9A441]/10 border border-[#D9A441]/40 space-y-2">
                <div className="font-mono text-xs font-bold text-[#9E6C15] uppercase">
                  Counterarguments Considered
                </div>
                <ul className="space-y-1 text-xs text-[#5D646F] font-sans list-disc list-inside">
                  {challenge.critic_review.counterarguments.map((ca, idx) => (
                    <li key={idx}>{ca}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* WHAT WOULD CHANGE THIS RECOMMENDATION */}
            <div className="p-5 rounded-xl bg-gradient-to-r from-[#D9A441]/10 to-[#C1553B]/10 border border-[#D9A441]/40 space-y-2.5">
              <div className="flex items-center space-x-2 font-mono text-xs font-bold text-[#1A1D22] uppercase tracking-wide">
                <Flame className="w-4 h-4 text-[#C1553B]" />
                <span>What Would Change This Recommendation</span>
              </div>
              <ul className="space-y-1.5 text-xs text-[#1A1D22] font-sans list-disc list-inside">
                {challenge.critic_review.what_would_change_recommendation.map((condition, idx) => (
                  <li key={idx} className="font-medium leading-relaxed">
                    {condition}
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* ================= BAND 4: TRACE & AUDIT BAND ================= */}
          <section className="p-6 rounded-xl bg-[#F5F6F5] border border-[#D1D7D7] space-y-4">
            <div className="flex items-center justify-between">
              <div className="font-mono text-xs font-bold text-[#5D646F] uppercase">
                04 // Execution Audit Trail
              </div>
              <button
                onClick={onViewTrace}
                className="font-mono text-xs text-[#2F8F8B] font-bold hover:underline"
              >
                Open Full Graph Console →
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
              <div className="p-3 bg-white rounded border border-[#D1D7D7]">
                <div className="text-[10px] text-[#8E96A5]">RUN ID</div>
                <div className="font-bold text-[#1A1D22] truncate">{trace.run_id}</div>
              </div>
              <div className="p-3 bg-white rounded border border-[#D1D7D7]">
                <div className="text-[10px] text-[#8E96A5]">TOKENS</div>
                <div className="font-bold text-[#1A1D22]">{trace.total_tokens.toLocaleString()}</div>
              </div>
              <div className="p-3 bg-white rounded border border-[#D1D7D7]">
                <div className="text-[10px] text-[#8E96A5]">LATENCY</div>
                <div className="font-bold text-[#2F8F8B]">{trace.total_latency_ms} ms</div>
              </div>
              <div className="p-3 bg-white rounded border border-[#D1D7D7]">
                <div className="text-[10px] text-[#8E96A5]">EST. COST</div>
                <div className="font-bold text-[#4C8B5B]">${trace.estimated_cost_usd.toFixed(4)}</div>
              </div>
            </div>
          </section>

        </div>

        {/* Right Side: Interactive Evidence Drawer (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl p-5 border border-[#D1D7D7] shadow-sm sticky top-6 space-y-4">
            
            <div className="flex items-center justify-between border-b border-[#D1D7D7] pb-3">
              <div>
                <div className="font-mono text-xs font-bold text-[#1A1D22] uppercase tracking-wide">
                  Retrieved Evidence ({trace.sources.length})
                </div>
                <div className="font-mono text-[10px] text-[#5D646F]">
                  Click to inspect raw source metadata
                </div>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex flex-wrap gap-1.5 font-mono text-[10px]">
              {['all', 'sql_result', 'document', 'web', 'calculation'].map((type) => (
                <button
                  key={type}
                  onClick={() => setSourceFilter(type)}
                  className={`px-2.5 py-1 rounded transition-colors uppercase font-bold ${
                    sourceFilter === type
                      ? 'bg-[#10131C] text-white'
                      : 'bg-[#F5F6F5] text-[#5D646F] hover:bg-[#E9ECEC]'
                  }`}
                >
                  {type.replace('_', ' ')}
                </button>
              ))}
            </div>

            {/* Source Cards List */}
            <div className="space-y-3 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
              {filteredSources.map((src) => {
                const Icon = getSourceIcon(src.source_type);
                const isSelected = selectedSourceId === src.id;

                return (
                  <div
                    key={src.id}
                    onClick={() => setSelectedSourceId(src.id)}
                    className={`p-3.5 rounded-lg border transition-all cursor-pointer space-y-2 ${
                      isSelected
                        ? 'bg-[#2F8F8B]/10 border-[#2F8F8B] shadow-xs'
                        : 'bg-[#F5F6F5] border-[#D1D7D7] hover:border-[#2F8F8B]/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center space-x-2">
                        <Icon className="w-3.5 h-3.5 text-[#2F8F8B] shrink-0" />
                        <span className="font-mono text-xs font-bold text-[#1A1D22] line-clamp-1">
                          {src.title}
                        </span>
                      </div>
                      <span className="font-mono text-[9px] px-1.5 py-0.5 rounded bg-white border border-[#D1D7D7] font-bold text-[#5D646F] uppercase shrink-0">
                        {src.source_type.replace('_', ' ')}
                      </span>
                    </div>

                    <p className="text-[11px] text-[#5D646F] font-sans leading-relaxed">
                      "{src.excerpt}"
                    </p>

                    <div className="flex items-center justify-between font-mono text-[9px] text-[#8E96A5] pt-1 border-t border-[#D1D7D7]/60">
                      <span>Credibility: {Math.round(src.credibility_score * 100)}%</span>
                      {src.url && (
                        <span className="text-[#2F8F8B] truncate max-w-[140px]">{src.url}</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};
