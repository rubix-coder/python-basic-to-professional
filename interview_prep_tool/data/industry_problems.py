"""
Industry / applied problems that bridge SDET / AI-validation experience into
coding credibility. All code below was run and tested locally before inclusion.
"""

INDUSTRY_PROBLEMS = [
    {
        "name": "LRU Cache",
        "tag": "Systems / Data structures",
        "why": (
            "Classic onsite problem; tests doubly linked list + hashmap fluency. "
            "Comes up in caching-layer designs."
        ),
        "code": '''class _Node:
    __slots__ = ('k', 'v', 'prev', 'nxt')
    def __init__(self, k=0, v=0):
        self.k, self.v = k, v
        self.prev = self.nxt = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = _Node(), _Node()
        self.head.nxt = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.nxt = node.nxt
        node.nxt.prev = node.prev

    def _add_front(self, node):
        node.nxt = self.head.nxt
        node.prev = self.head
        self.head.nxt.prev = node
        self.head.nxt = node

    def get(self, key):
        if key not in self.map: return -1
        node = self.map[key]
        self._remove(node); self._add_front(node)
        return node.v

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = _Node(key, value)
        self.map[key] = node
        self._add_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.k]''',
        "complexity": "Time: O(1) get/put, Space: O(capacity)",
    },
    {
        "name": "Token Bucket Rate Limiter",
        "tag": "Systems / Concurrency",
        "why": (
            "API gateway pattern. Validates understanding of clocks, "
            "monotonic-time, and lock-free refill logic."
        ),
        "code": '''import time, threading

class TokenBucket:
    """Thread-safe token bucket. capacity = burst, refill_rate = tokens/sec."""

    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last = time.monotonic()
        self.lock = threading.Lock()

    def allow(self, n=1):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False''',
        "complexity": "Time: O(1), Space: O(1)",
    },
    {
        "name": "LLM Evaluation Pipeline with Judge Aggregation",
        "tag": "AI / Evaluation",
        "why": (
            "Maps directly to AI-validation work. Shows you can frame quality "
            "as a measurable signal and aggregate multi-judge votes safely."
        ),
        "code": '''from collections import Counter
from statistics import median

def aggregate_judges(judgements):
    """
    judgements: list of dicts like
       {"id": str, "label": "good" | "bad", "score": 0..1, "rationale": str}
    Returns aggregated verdict with confidence and disagreement.
    """
    if not judgements:
        return {"label": "abstain", "confidence": 0.0, "disagreement": 0.0, "n": 0}

    labels = [j["label"] for j in judgements]
    scores = [float(j.get("score", 0.5)) for j in judgements]
    cnt = Counter(labels)
    top_label, top_n = cnt.most_common(1)[0]
    confidence = top_n / len(labels)
    disagreement = 1.0 - confidence
    return {
        "label": top_label if confidence >= 0.6 else "abstain",
        "confidence": round(confidence, 3),
        "score_median": round(median(scores), 3),
        "disagreement": round(disagreement, 3),
        "n": len(labels),
    }

def run_eval(samples, judge_fns):
    """Apply each judge to each sample, return aggregated verdicts."""
    results = []
    for s in samples:
        judgements = [{"id": fn.__name__, **fn(s)} for fn in judge_fns]
        results.append({"input": s, "verdict": aggregate_judges(judgements)})
    return results''',
        "complexity": "Time: O(N * J), Space: O(N)",
    },
    {
        "name": "Hallucinated API-Call Detection",
        "tag": "AI / Safety",
        "why": (
            "Concrete agent-safety problem. Detects when an LLM invents a tool "
            "or argument outside its declared schema."
        ),
        "code": '''import json

def detect_hallucinated_calls(llm_calls, tool_schema):
    """
    llm_calls: list of {"name": str, "arguments": dict-or-json-str}
    tool_schema: {tool_name: {arg_name: ("required" | "optional", type_str)}}
    Returns list of issues; empty means clean.
    """
    issues = []
    for i, call in enumerate(llm_calls):
        name = call.get("name")
        if name not in tool_schema:
            issues.append({"idx": i, "kind": "unknown_tool", "name": name})
            continue
        spec = tool_schema[name]
        args = call.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                issues.append({"idx": i, "kind": "bad_json", "name": name})
                continue
        for arg, (req, typ) in spec.items():
            if req == "required" and arg not in args:
                issues.append({"idx": i, "kind": "missing_required", "name": name, "arg": arg})
        for arg in args:
            if arg not in spec:
                issues.append({"idx": i, "kind": "unknown_arg", "name": name, "arg": arg})
    return issues''',
        "complexity": "Time: O(C * A), Space: O(issues)",
    },
    {
        "name": "Flaky Test Quarantine Detector",
        "tag": "SDET / Reliability",
        "why": (
            "Test-engineering credibility. Classifies a test as flaky vs broken "
            "from a recent history window."
        ),
        "code": '''def classify_tests(history, window=20, flaky_threshold=0.15):
    """
    history: {test_id: [True/False, ...]} latest-first results.
    Returns {test_id: "stable" | "flaky" | "broken"}
    """
    out = {}
    for test, results in history.items():
        recent = results[:window]
        if not recent:
            out[test] = "stable"; continue
        fails = sum(1 for r in recent if not r)
        passes = len(recent) - fails
        rate = fails / len(recent)
        if fails == len(recent):
            out[test] = "broken"
        elif 0 < rate < (1 - flaky_threshold) and passes > 0 and fails > 0:
            out[test] = "flaky"
        else:
            out[test] = "stable"
    return out''',
        "complexity": "Time: O(T * window), Space: O(T)",
    },
]
