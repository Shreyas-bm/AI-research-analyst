"""Safe Read-Only SQL Query Tool with strict AST / keyword validation"""
import os
import re
import sqlite3
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.schemas.evidence import EvidenceItem, SourceType, SourceMetadata

FORBIDDEN_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
    r"\bALTER\b", r"\bCREATE\b", r"\bTRUNCATE\b", r"\bATTACH\b",
    r"\bDETACH\b", r"\bPRAGMA\b", r"\bREPLACE\b", r"\bGRANT\b",
    r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"\bVACUUM\b"
]

class SQLToolResult(BaseModel):
    query: str
    is_success: bool
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    error_message: Optional[str] = None
    formatted_summary: Optional[str] = None

class SafeSQLTool:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.BENCHMARK_DB_PATH

    def validate_query(self, query: str) -> None:
        """Validate query string to ensure strictly read-only execution."""
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Empty SQL query")

        # Must start with SELECT or WITH
        first_word = clean_query.split()[0].upper()
        if first_word not in ["SELECT", "WITH", "EXPLAIN"]:
            raise PermissionError(f"Query must begin with SELECT, WITH or EXPLAIN. Got: {first_word}")

        # Check for forbidden mutation keywords
        for pattern in FORBIDDEN_KEYWORDS:
            if re.search(pattern, clean_query, re.IGNORECASE):
                matched = re.search(pattern, clean_query, re.IGNORECASE).group(0)
                raise PermissionError(f"Security violation: Query contains disallowed keyword '{matched}'")

        # Disallow multiple semicolon-separated statements
        statements = [s.strip() for s in clean_query.split(";") if s.strip()]
        if len(statements) > 1:
            raise PermissionError("Multiple SQL statements in a single query are forbidden.")

    def execute(self, query: str, max_rows: int = 50) -> SQLToolResult:
        """Execute validated query safely and return structured rows."""
        try:
            self.validate_query(query)

            if not os.path.exists(self.db_path):
                return SQLToolResult(
                    query=query,
                    is_success=False,
                    error_message=f"Database file not found at: {self.db_path}"
                )

            # Open read-only SQLite URI connection
            uri_path = f"file:{os.path.abspath(self.db_path)}?mode=ro"
            conn = sqlite3.connect(uri_path, uri=True, timeout=5.0)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(query)
            col_names = [d[0] for d in cur.description] if cur.description else []
            fetched_rows = cur.fetchmany(max_rows)
            
            rows = [dict(row) for row in fetched_rows]
            conn.close()

            # Format human-readable summary
            summary_lines = [f"SQL Result ({len(rows)} rows):"]
            for r in rows[:5]:
                summary_lines.append(" | ".join(f"{k}: {v}" for k, v in r.items()))
            if len(rows) > 5:
                summary_lines.append(f"... and {len(rows) - 5} more rows")

            return SQLToolResult(
                query=query,
                is_success=True,
                columns=col_names,
                rows=rows,
                row_count=len(rows),
                formatted_summary="\n".join(summary_lines)
            )
        except Exception as e:
            return SQLToolResult(
                query=query,
                is_success=False,
                error_message=str(e)
            )

    def execute_as_evidence(self, query: str) -> List[EvidenceItem]:
        """Execute query and convert into structured EvidenceItems."""
        res = self.execute(query)
        if not res.is_success or not res.rows:
            return []

        evidence_items = []
        for i, row in enumerate(res.rows):
            excerpt_text = ", ".join([f"{k}: {v}" for k, v in row.items()])
            evidence_items.append(EvidenceItem(
                id=f"src-sql-{i+1}",
                source_type=SourceType.SQL_RESULT,
                title=f"Structured Benchmark DB (Row {i+1})",
                excerpt=excerpt_text,
                metadata=SourceMetadata(
                    query_used=query,
                    custom={"row_data": row}
                ),
                credibility_score=1.0
            ))
        return evidence_items
