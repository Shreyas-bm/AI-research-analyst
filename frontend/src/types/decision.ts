export type SourceType = 'web' | 'document' | 'sql_result' | 'calculation';
export type VerificationStatus = 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'CONTRADICTED';

export interface SourceMetadata {
  author?: string;
  publish_date?: string;
  page_number?: number;
  section?: string;
  query_used?: string;
  document_id?: string;
  table_name?: string;
  custom?: Record<string, any>;
}

export interface EvidenceItem {
  id: string;
  source_type: SourceType;
  title: string;
  url?: string;
  excerpt: string;
  metadata?: SourceMetadata;
  retrieved_at?: string;
  credibility_score: number;
}

export interface ClaimItem {
  id: string;
  claim_text: string;
  verification_status: VerificationStatus;
  supporting_source_ids: string[];
  contradicting_source_ids?: string[];
  verifier_notes?: string;
  confidence: number;
}

export interface AlternativeScore {
  name: string;
  strengths: string[];
  weaknesses: string[];
  score?: number;
}

export interface ComparisonRow {
  criterion: string;
  values: Record<string, string>;
  winner?: string;
  notes?: string;
}

export interface QuantitativeAnalysis {
  summary: string;
  comparison_table: ComparisonRow[];
  calculations_performed: string[];
}

export interface CriticReview {
  identified_risks: string[];
  counterarguments: string[];
  assumptions_stress_tested: string[];
  what_would_change_recommendation: string[];
}

export interface ConfidenceIndicator {
  score: number;
  level: string;
  reasoning: string;
}

export interface VerdictBand {
  decision_question: string;
  recommendation_headline: string;
  confidence: ConfidenceIndicator;
  alternatives: AlternativeScore[];
}

export interface EvidenceBand {
  context_summary: string;
  decision_criteria: string[];
  quantitative_analysis: QuantitativeAnalysis;
  key_trade_offs: string[];
  claims: ClaimItem[];
}

export interface ChallengeBand {
  critic_review: CriticReview;
  material_assumptions: string[];
}

export interface TraceBand {
  run_id: string;
  total_tokens: number;
  estimated_cost_usd: number;
  total_latency_ms: number;
  tool_invocations_count: number;
  sources: EvidenceItem[];
}

export interface DecisionReport {
  id: string;
  question: string;
  generated_at: string;
  verdict: VerdictBand;
  evidence: EvidenceBand;
  challenge: ChallengeBand;
  trace: TraceBand;
}

export interface DecisionHistoryItem {
  id: string;
  question: string;
  status: string;
  recommendation_headline?: string;
  confidence_score?: number;
  created_at?: string;
  total_tokens: number;
  total_latency_ms: number;
}

export interface BenchmarkCase {
  case_id: string;
  category: string;
  question: string;
  context: Record<string, any>;
  constraints: string[];
  candidate_alternatives: string[];
  ground_truth_criteria: string[];
  gold_recommendation: string;
  expected_trade_offs: string[];
}

export interface BenchmarkResultSummary {
  eval_id: string;
  configuration_name: string;
  dataset_name: string;
  total_cases: number;
  citation_coverage: number;
  faithfulness_score: number;
  answer_relevance: number;
  recall_at_5: number;
  precision_at_5: number;
  avg_latency_ms: number;
  avg_token_cost_usd: number;
  case_results: Array<{
    case_id: string;
    question: string;
    citation_coverage: number;
    faithfulness: number;
    answer_relevance: number;
    recommendation_alignment: number;
    latency_ms: number;
    cost_usd: number;
    recommendation: string;
  }>;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  chunk_count: number;
  created_at: string;
  preview?: string;
}
