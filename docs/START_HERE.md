# Mercy Ledger — Priority-Based Four-Person Implementation Pack

This pack is a **sequenced implementation plan with copy/paste AI prompts**. It is not a claim that the features are already implemented.

## Downloaded baseline

Use the included `BASELINE/mercy_ledger_attribution_ready.zip` as the common starting project. Extract it into each person's own working folder. Do not have two AI agents edit the same project folder at the same time.

The latest baseline's `attribution.py` is the protected working module. **Do not replace or edit it in any priority unless the integrator explicitly approves a bug fix.** The existing data contract, golden files, checker and SOP references must remain the source of truth.

## How the team should work

1. All four people start Priority 1 at the same time, each in a separate project copy.
2. Each person opens their project folder in their coding AI (for example, Antigravity) and pastes the matching `Person_X_Prompt.md` from `Priority_1_Core_MVP`.
3. A, B and C return only their assigned completed files and their test output to Person D. Person D owns `static/index.html`, integration, shared files, and end-to-end testing.
4. **Do not start Priority 2 until Priority 1's acceptance gate is passed.** Use the `ACCEPTANCE_GATE.md` in that folder.
5. Repeat the same process for Priority 2. Start Priority 3 only if Priority 2 is passing and enough time remains. Priority 3 is explicitly optional/stretch scope.

## What each priority means

- **Priority 1 — Working core MVP:** implement the existing six backend modules and the frontend, integrate, test, and rehearse. No novel feature work yet.
- **Priority 2 — Judge-visible depth, low integration risk:** conservation invariants, real stress-test reporting, useful review flags, plain-language victim explanations, transaction replay, and three impact/review scenario cards.
- **Priority 3 — Stretch features:** controlled synthetic multi-account chain visualization, assumption sensitivity, and report fingerprint verification. These must not endanger the core app.

## Critical instructions

- The AI must inspect the actual project files before coding. It must not invent API fields or claim a test passed without running it.
- Follow `00_RULES_FOR_EVERY_AI.md` and `01_DATA_CONTRACT.md` in the baseline.
- Keep financial arithmetic deterministic; use `Decimal` for money in Python. Do not calculate rupee amounts in JavaScript.
- Never change golden fixtures or the checker to force a pass. If a golden, data contract, implementation and SOP appear to conflict, stop and report the conflict to Person D.
- Synthetic outputs must be labelled as synthetic. A transaction pattern is not proof of guilt. “Not attributed by the model” does not mean “legally cleared.”
- Do not claim live bank/NCRP/CFCFRMS integration, comprehensive real-world cross-bank tracing, OCR, or legal decision-making.
- Each person sends the *complete file(s)* listed in their prompt plus a short note showing commands executed and actual pass/fail results. Do not send only snippets.

## Recommended startup

In each project copy, from inside the extracted `mercy_ledger/` directory:

```bash
python -m pip install -r requirements.txt
python check_my_work.py attribution
```

The attribution check should pass before any teammate begins. Some module checks are expected to fail while their assigned modules are still stubs.
