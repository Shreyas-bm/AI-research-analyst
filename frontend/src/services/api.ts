import type {
  DecisionReport,
  DecisionHistoryItem,
  DocumentItem,
  BenchmarkResultSummary,
  BenchmarkCase
} from '../types/decision';

const API_BASE = 'http://localhost:8000/api';

export interface DecisionAnalyzePayload {
  question: string;
  context?: Record<string, any>;
  constraints?: string[];
  preferred_alternatives?: string[];
  document_ids?: string[];
}

export async function analyzeDecision(payload: DecisionAnalyzePayload): Promise<DecisionReport> {
  const res = await fetch(`${API_BASE}/decision/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(err.detail || `Analysis failed (${res.status})`);
  }

  return res.json();
}

export async function getDecisionRun(runId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/decision/${runId}`);
  if (!res.ok) throw new Error(`Run ${runId} not found`);
  return res.json();
}

export async function listDecisionHistory(): Promise<DecisionHistoryItem[]> {
  const res = await fetch(`${API_BASE}/decision/history`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function uploadDocument(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }

  return res.json();
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function runEvaluation(
  configurationName: string = 'Full Agentic (DecisionLens)',
  caseIds?: string[]
): Promise<BenchmarkResultSummary> {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ configuration_name: configurationName, case_ids: caseIds })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Evaluation run failed' }));
    throw new Error(err.detail || 'Evaluation run failed');
  }

  return res.json();
}

export async function listEvaluationRuns(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/eval/runs`);
  if (!res.ok) throw new Error('Failed to fetch evaluation runs');
  return res.json();
}

export async function getBenchmarkDataset(): Promise<BenchmarkCase[]> {
  const res = await fetch(`${API_BASE}/eval/dataset`);
  if (!res.ok) throw new Error('Failed to fetch dataset');
  return res.json();
}
