"""Sandboxed Quantitative Calculation Tool using AST evaluation"""
import ast
import math
import operator
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.evidence import EvidenceItem, SourceType, SourceMetadata

# Allowed operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed math functions
ALLOWED_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "ceil": math.ceil,
    "floor": math.floor,
    "pow": math.pow,
    "pi": math.pi,
    "e": math.e,
}

class CalcToolResult(BaseModel):
    expression: str
    is_success: bool
    result: Optional[Union[float, int, str]] = None
    formatted_output: Optional[str] = None
    error_message: Optional[str] = None

class CalculationTool:
    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, complex)):
                return node.value
            raise ValueError(f"Constant of type {type(node.value)} is not allowed.")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in OPERATORS:
                return OPERATORS[op_type](left, right)
            raise ValueError(f"Operator {op_type} is not supported.")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in OPERATORS:
                return OPERATORS[op_type](operand)
            raise ValueError(f"Unary operator {op_type} is not supported.")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in ALLOWED_FUNCTIONS:
                    args = [self._eval_node(arg) for arg in node.args]
                    return ALLOWED_FUNCTIONS[func_name](*args)
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "math" and node.func.attr in ALLOWED_FUNCTIONS:
                    args = [self._eval_node(arg) for arg in node.args]
                    return ALLOWED_FUNCTIONS[node.func.attr](*args)
            raise ValueError("Unauthorized or unknown function call in calculation.")

        elif isinstance(node, ast.Name):
            if node.id in ALLOWED_FUNCTIONS:
                return ALLOWED_FUNCTIONS[node.id]
            raise ValueError(f"Variable name '{node.id}' is not defined.")

        elif isinstance(node, ast.List):
            return [self._eval_node(elt) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt) for elt in node.elts)

        else:
            raise ValueError(f"Unsupported AST node type: {type(node).__name__}")

    def evaluate(self, expression: str) -> CalcToolResult:
        """Safely parse and evaluate a mathematical expression."""
        clean_expr = expression.strip()
        if not clean_expr:
            return CalcToolResult(
                expression=expression,
                is_success=False,
                error_message="Empty mathematical expression"
            )

        try:
            # Parse into AST expression
            parsed = ast.parse(clean_expr, mode="eval")
            res = self._eval_node(parsed)

            if isinstance(res, float):
                if res.is_integer():
                    formatted = f"{int(res):,}"
                else:
                    formatted = f"{res:,.2f}"
            else:
                formatted = f"{res:,}" if isinstance(res, int) else str(res)

            return CalcToolResult(
                expression=clean_expr,
                is_success=True,
                result=res,
                formatted_output=f"{clean_expr} = {formatted}"
            )
        except Exception as e:
            return CalcToolResult(
                expression=clean_expr,
                is_success=False,
                error_message=f"Calculation error: {str(e)}"
            )

    def evaluate_as_evidence(self, expression: str) -> List[EvidenceItem]:
        """Evaluate mathematical expression and return EvidenceItem."""
        res = self.evaluate(expression)
        if not res.is_success or res.result is None:
            return []

        return [
            EvidenceItem(
                id="src-calc-1",
                source_type=SourceType.CALCULATION,
                title=f"Quantitative Calculation: {expression}",
                excerpt=res.formatted_output or str(res.result),
                metadata=SourceMetadata(
                    query_used=expression,
                    custom={"result_value": res.result}
                ),
                credibility_score=1.0
            )
        ]
