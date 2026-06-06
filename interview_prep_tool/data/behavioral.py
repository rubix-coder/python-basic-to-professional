"""
STAR story scaffolding and SDET/automation question pool. The 7 STAR stories
are templates — the tool fills S/T/A/R from the candidate's real bullets.
"""

STAR_SLOTS = [
    {
        "slot": "Why leaving / why now",
        "prompt": "Honest framing of the gap as a deliberate validation-to-generative pivot.",
        "lands": "Leads with conviction (what you want), not avoidance (what you left).",
    },
    {
        "slot": "Conflict with a peer or stakeholder",
        "prompt": "Specific disagreement, your move, the outcome — not the venting version.",
        "lands": "Shows you can stay in disagreement without making it personal.",
    },
    {
        "slot": "Mentoring / multiplying others",
        "prompt": "Concrete person, concrete delta in their output. Not 'I led trainings.'",
        "lands": "Levels above L4 require evidence you scale others, not just yourself.",
    },
    {
        "slot": "Hardest technical challenge",
        "prompt": "The one debug or design that almost broke you. Trace the actual reasoning.",
        "lands": "Demonstrates depth + how you reason under uncertainty.",
    },
    {
        "slot": "Proudest project",
        "prompt": "Pick the one where you owned end-to-end and the business cared.",
        "lands": "Shows scope and ownership at L4/L5 bar.",
    },
    {
        "slot": "Failure",
        "prompt": "Real failure, real cost, what you actually changed afterwards.",
        "lands": "Refusing to give a real one tanks the round. Specifics earn trust.",
    },
    {
        "slot": "Decision under incomplete information",
        "prompt": "What you knew, what you didn't, what you bet on, the outcome.",
        "lands": "Maps to senior judgment signal interviewers are calibrating for.",
    },
]

SDET_POOL = [
    {
        "q": "Severity vs priority — define each, give an example where they diverge.",
        "a": (
            "Severity = technical impact of the bug. Priority = business urgency to fix. "
            "Example: a typo on the homepage banner — severity Low, priority High (CEO sees it). "
            "Conversely: a memory leak in a nightly batch — severity High, priority Low if the batch runs in <1h."
        ),
    },
    {
        "q": "How do you design a UI test framework for a new product from scratch?",
        "a": (
            "Layers: driver (Playwright / Selenium) → page objects → flows → tests. "
            "Hard rules: no Thread.sleep, all waits are explicit conditions; one source of test data; "
            "tests parallelizable (no shared state); CI runs headless with screenshots/video on failure; "
            "tagging for smoke / regression / nightly; reports machine-readable (JUnit XML)."
        ),
    },
    {
        "q": "A test is flaky 1 in 10 runs. How do you triage?",
        "a": (
            "Stabilize before quarantine. Capture logs/video on failure, run with --repeat-until-fail locally. "
            "Common causes: implicit timing, animation, test data collision, order dependence. "
            "If root-cause is not found in a defined window (e.g., 2 days), quarantine with a tracked ticket — "
            "never silently disable. Track flake rate as a CI metric."
        ),
    },
    {
        "q": "Describe the test pyramid and when you'd invert it.",
        "a": (
            "Unit (many, fast) → component / integration → end-to-end (few, slow). "
            "Invert only when the system is mostly orchestration with little business logic (e.g., a thin Lambda) — "
            "then E2E gives more signal per test than unit coverage of glue code."
        ),
    },
    {
        "q": "How do you test an API contract?",
        "a": (
            "Schema validation (OpenAPI / JSON Schema) on request/response; golden examples committed to repo; "
            "contract tests (Pact) between consumer and producer in CI; status-code, header, and error-shape coverage; "
            "negative tests for required fields, types, auth, rate limits."
        ),
    },
    {
        "q": "Mocking vs stubbing vs faking — when do you use each?",
        "a": (
            "Stub: returns canned values, no behavior check. Fake: working in-memory implementation (in-memory DB). "
            "Mock: stub + assertion on how it was called. Prefer fakes for collaborators you exercise heavily, "
            "stubs for boundaries you don't care about, mocks only when the interaction itself is the contract."
        ),
    },
    {
        "q": "CI build is red and you don't know why. Walk me through triage.",
        "a": (
            "Reproduce locally with the exact CI command. Bisect: is it the new commit or pre-existing? "
            "Compare last-green vs current — diff is the suspect set. Check infra signals (runner image, secrets). "
            "If flaky → re-run twice; if same failure → fix forward. Never merge over red without a tracked exception."
        ),
    },
    {
        "q": "How do you parallelize a suite that has shared fixtures?",
        "a": (
            "Isolate state: per-worker DB schema or namespaced records; randomize seed data IDs; "
            "remove ordering assumptions; serialize only the tests that genuinely conflict (annotate them). "
            "Measure speedup and flake-rate delta before declaring success."
        ),
    },
    {
        "q": "What's idempotency and how do you test it?",
        "a": (
            "Same request applied N times yields the same end state. Test by replaying the request "
            "(same idempotency key) and asserting state hash + side-effect count unchanged. "
            "For payment/order APIs, also assert no duplicate downstream events."
        ),
    },
    {
        "q": "How do you load-test a new service?",
        "a": (
            "Define SLOs first (p95 latency, error rate). Tools: k6, Locust, JMeter. "
            "Ramp profiles: steady-state, spike, soak. Monitor system + downstream resources. "
            "Identify saturation point and the failure mode (queue overflow vs timeout vs error)."
        ),
    },
    {
        "q": "How do you validate an LLM feature's quality?",
        "a": (
            "Layered: (1) deterministic checks (schema, citation presence, refusal triggers); "
            "(2) reference-based metrics (exact match, ROUGE, embedding similarity) on a curated set; "
            "(3) LLM-as-judge with rubrics and inter-judge agreement; "
            "(4) red-team set for safety + jailbreaks. Track each as a CI gate with thresholds."
        ),
    },
    {
        "q": "Root-cause an intermittent silicon/system failure that only repros at scale.",
        "a": (
            "Capture maximum telemetry pre-failure (ring buffers, signal traces). "
            "Reduce repro: isolate the smallest config that triggers it (clock, voltage, workload mix). "
            "Form hypotheses, design experiments that distinguish between them. "
            "Bisect firmware/driver versions if applicable. Don't accept 'cosmic ray' until evidence supports it."
        ),
    },
    {
        "q": "How do you decide what NOT to automate?",
        "a": (
            "Cost of automation > expected savings * frequency. Skip: one-off exploratory work, "
            "tests that change every sprint, UX nuance only humans catch. Automate stable contracts, "
            "regression-prone areas, and anything blocking release."
        ),
    },
    {
        "q": "Difference between integration test and end-to-end test in your framework?",
        "a": (
            "Integration: real components, fake boundaries (fake auth, fake payment provider). "
            "E2E: real environment, real boundaries. E2E catches config / wiring bugs; integration catches contract bugs. "
            "Run integration on every PR, E2E nightly + pre-release."
        ),
    },
    {
        "q": "How do you measure test effectiveness?",
        "a": (
            "Escape rate (bugs found in prod / total bugs); mutation testing score for unit suites; "
            "flake rate; mean time to triage a failure. Coverage alone is misleading without these."
        ),
    },
    {
        "q": "What do you do when QA cycle blocks release every sprint?",
        "a": (
            "Inspect the work: which checks are manual, which can shift left, what's actually catching bugs. "
            "Shift cheap deterministic checks into CI (linters, contract tests, smoke). "
            "Keep manual for genuinely judgment-dependent paths. Track release-blocker cost per sprint."
        ),
    },
    {
        "q": "Walk me through testing a payment flow.",
        "a": (
            "Happy path + each terminal state (success, decline, timeout, fraud-flag). "
            "Idempotency on retries. Currency rounding edge cases. Chargeback / refund paths. "
            "PCI surface — assert no PAN in logs. Sandbox provider for E2E; contract tests for unit."
        ),
    },
    {
        "q": "Designing observability for tests themselves — what do you collect?",
        "a": (
            "Per-test: duration, pass/fail, retries, screenshots/video on fail, logs, trace IDs. "
            "Per-suite: trend, flake rate, slowest 10. Per-CI-run: queue time, infra failures. "
            "Dashboards beat alerts here — you want to see trends, not just spikes."
        ),
    },
]
