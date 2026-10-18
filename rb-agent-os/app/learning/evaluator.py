"""
Cross-Model Benchmark Evaluator for RB Agent OS.
Evaluates model accuracy, response latency, and verifies benchmark cases.
"""

import time
import uuid
from typing import Any, Dict, List, Optional
from ..database.db import get_db
from ..models import get_model_adapter

class ModelEvaluator:
    def __init__(self):
        pass

    async def run_benchmark(self, benchmark_id: Optional[str] = None, provider_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Runs benchmark cases against the selected provider and records scores."""
        db = get_db()
        if benchmark_id:
            cases = db.fetchall("SELECT * FROM benchmark_cases WHERE id = ? AND is_active = 1", (benchmark_id,))
        else:
            cases = db.fetchall("SELECT * FROM benchmark_cases WHERE is_active = 1 LIMIT 5")

        adapter = get_model_adapter(provider_name)
        results = []

        for case in cases:
            prompt = case["prompt"]
            expected = case["expected_output"].lower()
            start = time.time()

            try:
                res = await adapter.generate_response([{"role": "user", "content": prompt}])
                elapsed = int((time.time() - start) * 1000)
                actual = res.content.lower()

                # Basic evaluation score
                score = 1.0 if expected in actual else 0.5 if any(w in actual for w in expected.split()) else 0.0

                eval_id = str(uuid.uuid4())
                prov_row = db.fetchone("SELECT id FROM model_providers WHERE provider_name = ?", (adapter.provider,))
                prov_id = prov_row["id"] if prov_row else "default_prov"

                db.execute(
                    "INSERT INTO model_evaluations (id, provider_id, benchmark_id, score, latency_ms, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (eval_id, prov_id, case["id"], score, elapsed, f"Output length: {len(actual)}")
                )

                results.append({
                    "evaluation_id": eval_id,
                    "benchmark_id": case["id"],
                    "prompt": prompt,
                    "score": score,
                    "latency_ms": elapsed,
                    "provider": adapter.provider,
                    "model": adapter.model_name
                })
            except Exception as e:
                results.append({
                    "benchmark_id": case["id"],
                    "error": str(e),
                    "score": 0.0
                })

        return results

_evaluator_instance: Optional[ModelEvaluator] = None

def get_model_evaluator() -> ModelEvaluator:
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = ModelEvaluator()
    return _evaluator_instance
