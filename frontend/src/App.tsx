import { useState, useEffect } from 'react';
import { NavigationRail } from './components/NavigationRail';
import type { ActiveTab } from './components/NavigationRail';
import { DecisionIntake } from './components/DecisionIntake';
import { ResearchTrace } from './components/ResearchTrace';
import { DecisionReportView } from './components/DecisionReportView';
import { DocumentsView } from './components/DocumentsView';
import { EvaluationDashboard } from './components/EvaluationDashboard';
import { AuthModal } from './components/AuthModal';
import { AuthScreen } from './components/AuthScreen';
import { useAuth } from './context/AuthContext';
import type { DecisionReport, DecisionHistoryItem } from './types/decision';
import { analyzeDecision, listDecisionHistory } from './services/api';

export function App() {
  const { isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<ActiveTab>('ask');
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [currentReport, setCurrentReport] = useState<DecisionReport | null>(null);
  const [history, setHistory] = useState<DecisionHistoryItem[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const fetchHistory = async () => {
    try {
      const data = await listDecisionHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchHistory();
    }
  }, [isAuthenticated]);

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

  // 1. Session check loading state
  if (isLoading) {
    return (
      <div className="min-h-screen w-screen bg-[#0D1017] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-2 border-[#2F8F8B]/20 border-t-[#2F8F8B] rounded-full animate-spin"></div>
        <div className="font-mono text-xs text-[#8E96A5] tracking-wider uppercase">
          Verifying Session State...
        </div>
      </div>
    );
  }

  // 2. Strict Authentication Wall: block unauthenticated users from using the app
  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  // 3. Authenticated App Experience
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#10131C] text-[#E8E9ED]">
      {/* Navigation Rail */}
      <NavigationRail
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        activeRunId={activeRunId}
        hasCompletedReport={!!currentReport}
        historyCount={history.length}
        onOpenAuth={() => setIsAuthModalOpen(true)}
      />

      {/* Main Surface Canvas */}
      <main className="flex-1 h-full overflow-y-auto relative">
        {errorMessage && (
          <div className="absolute top-4 right-4 z-50 p-4 bg-[#C1553B] text-white rounded-lg shadow-lg font-mono text-xs max-w-md flex items-center justify-between">
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage(null)} className="ml-3 font-bold cursor-pointer">✕</button>
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

      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </div>
  );
}

export default App;
