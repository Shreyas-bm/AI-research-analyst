import type {
  DecisionReport,
  DecisionHistoryItem,
  DocumentItem,
  BenchmarkResultSummary,
  BenchmarkCase
} from '../types/decision';
import type {
  User,
  AuthResponse,
  RegisterPayload,
  LoginPayload
} from '../types/auth';

const API_BASE = 'http://localhost:8000/api';

const TOKEN_STORAGE_KEY = 'decisionlens_auth_token';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function removeStoredToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function getAuthHeaders(headers: Record<string, string> = {}): Record<string, string> {
  const token = getStoredToken();
  const res: Record<string, string> = { ...headers };
  if (token) {
    res['Authorization'] = `Bearer ${token}`;
  }
  return res;
}

// -------------------------------------------------------------
// Authentication Endpoints
// -------------------------------------------------------------

export async function registerUser(payload: RegisterPayload): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail || `Registration failed (${res.status})`);
  }

  const data: AuthResponse = await res.json();
  setStoredToken(data.access_token);
  return data;
}

export async function loginUser(payload: LoginPayload): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(err.detail || `Login failed (${res.status})`);
  }

  const data: AuthResponse = await res.json();
  setStoredToken(data.access_token);
  return data;
}

export async function fetchCurrentUser(): Promise<User> {
  const token = getStoredToken();
  if (!token) throw new Error('Not authenticated');

  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders({ 'Content-Type': 'application/json' })
  });

  if (!res.ok) {
    removeStoredToken();
    throw new Error('Session expired');
  }

  return res.json();
}

// -------------------------------------------------------------
// Decision Analysis Endpoints
// -------------------------------------------------------------

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
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(err.detail || `Analysis failed (${res.status})`);
  }

  return res.json();
}

export async function getDecisionRun(runId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/decision/${runId}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error(`Run ${runId} not found`);
  return res.json();
}

export async function listDecisionHistory(): Promise<DecisionHistoryItem[]> {
  const res = await fetch(`${API_BASE}/decision/history`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function uploadDocument(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }

  return res.json();
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function runEvaluation(
  configurationName: string = 'Full Agentic (DecisionLens)',
  caseIds?: string[]
): Promise<BenchmarkResultSummary> {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ configuration_name: configurationName, case_ids: caseIds })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Evaluation run failed' }));
    throw new Error(err.detail || 'Evaluation run failed');
  }

  return res.json();
}

export async function listEvaluationRuns(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/eval/runs`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch evaluation runs');
  return res.json();
}

export async function getBenchmarkDataset(): Promise<BenchmarkCase[]> {
  const res = await fetch(`${API_BASE}/eval/dataset`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch dataset');
  return res.json();
}
