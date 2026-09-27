import { useState, useEffect } from 'react';
import { NavigationRail } from './components/NavigationRail';
import type { ActiveTab } from './components/NavigationRail';
import { DecisionIntake } from './components/DecisionIntake';
import { ResearchTrace } from './components/ResearchTrace';
import { DecisionReportView } from './components/DecisionReportView';
import { DocumentsView } from './components/DocumentsView';
import { EvaluationDashboard } from './components/EvaluationDashboard';
import type { DecisionReport, DecisionHistoryItem } from './types/decision';
import { analyzeDecision, listDecisionHistory } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('ask');
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [currentReport, setCurrentReport] = useState<DecisionReport | null>(null);
  const [history, setHistory] = useState<DecisionHistoryItem[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      const data = await listDecisionHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleStartResearch = async (data: {
    question: string;
    context: Record<string, any>;
    constraints: string[];
    preferred_alternatives: string[];
    document_ids: string[];
  }) => {
    try {
      setIsAnalyzing(true);
      setErrorMessage(null);
      
      // Instantly generate a temporary run ID for the live trace console
      const tempRunId = `run-${Date.now().toString(36)}`;
      setActiveRunId(tempRunId);
      setActiveTab('runs');

      const report = await analyzeDecision(data);
      setCurrentReport(report);
      setActiveRunId(report.id);
      await fetchHistory();
    } catch (err: any) {
      setErrorMessage(err.message || 'Decision research workflow failed.');
      setActiveTab('ask');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#10131C] text-[#E8E9ED]">
      {/* Navigation Rail */}
      <NavigationRail
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        activeRunId={activeRunId}
        hasCompletedReport={!!currentReport}
        historyCount={history.length}
      />

      {/* Main Surface Canvas */}
      <main className="flex-1 h-screen overflow-hidden relative">
        {errorMessage && (
          <div className="absolute top-4 right-4 z-50 p-4 bg-[#C1553B] text-white rounded-lg shadow-lg font-mono text-xs max-w-md flex items-center justify-between">
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage(null)} className="ml-3 font-bold">✕</button>
          </div>
        )}

        {activeTab === 'ask' && (
          <DecisionIntake
            onStartResearch={handleStartResearch}
            isSubmitting={isAnalyzing}
          />
        )}

        {activeTab === 'runs' && (
          <ResearchTrace
            runId={activeRunId || 'run-live'}
            report={currentReport}
            isLoading={isAnalyzing}
            onViewReport={() => setActiveTab('report')}
          />
        )}

        {activeTab === 'report' && currentReport && (
          <DecisionReportView
            report={currentReport}
            onBackToIntake={() => setActiveTab('ask')}
            onViewTrace={() => setActiveTab('runs')}
          />
        )}

        {activeTab === 'documents' && (
          <DocumentsView />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
