# 00 - RULES FOR EVERY AI (READ FIRST, OBEY EXACTLY)

You are an AI assistant helping a non-programmer build ONE part of a hackathon project called **Mercy Ledger**
(a decision-support tool that helps Indian police Investigating Officers and bank nodal officers decide how much of a
bank account to freeze after UPI cyber-fraud complaints, and how to restore money to victims fairly).
Three teammates own separate modules while the team lead owns the UI and integration. Everything must follow the shared contract.
That only works if you follow these rules. They are not suggestions.

## A. Scope
1. Build ONLY the file(s) named in your PERSON_X document. Use the exact file name(s). Do not create extra files.
2. Do NOT edit, rename, or "improve" any other file: `presets.py`, `pipeline.py`, `app.py`, `check_my_work.py`,
   `make_sample_data.py`, anything in `golden/`, or any other person's file. If you think one of them is wrong,
   STOP and tell the human in plain words. Do not work around it.
3. Function names, argument order, JSON key names, enum spellings and file names are FROZEN by `01_DATA_CONTRACT.md`.
   Never rename, add, remove or reorder anything. A different spelling breaks the whole project.
4. Do not add features nobody asked for. No extra endpoints, no extra fields, no "bonus" logic.

## B. Output format
5. Reply with the COMPLETE file(s). Never use "...", "rest of code here", "unchanged", or TODO. No partial files.
6. One code block per file, with the file name on the line above it. No long explanations before or after.
7. If anything is unclear, or the spec seems to contradict a `golden/` file or the supplied SOP, ASK THE HUMAN. Never guess silently. The human/integrator must correct the contract/golden fixture before implementation continues.

## C. Python rules (all .py files except app.py)
8. Python 3.10+ and the **standard library only**. No pip packages. No pandas, numpy, pydantic, requests, etc.
9. **Money is `decimal.Decimal`, never float.** In every input and output, money is a STRING with exactly two decimals,
   like `"150000.00"`. Round with `ROUND_HALF_UP` to 0.01 ONLY at the moment you write an output value.
   Never write `float(` anywhere. Never put a Decimal object into the output (convert to string).
10. **Deterministic.** Same input must give the same output every time. No `datetime.now()`, `date.today()`, `time`,
    or randomness (except `simulator.py`, which may use `random.Random(seed)` and nothing else).
    Dates/"today" always arrive as arguments.
11. **Pure functions.** Never change the input dictionaries (work on copies). No printing, no files, no network,
    no environment variables, no `input()`.
12. **NO AI/LLM calls, NO internet, NO machine-learning anywhere in the product.** Every rupee figure and every legal
    deadline must come from plain arithmetic on the input. (Reason: auditability. This is the project's main selling point.)
13. Do not invent legal content. Only cite SOP clauses that appear in your PERSON document or in
    `golden/*.json` text. Copy those strings character for character.
14. Every output that recommends an action must stay "decision support": a human officer signs off.
    Never remove the words DRAFT / "human_signoff_required" / the disclaimers.

## D. How you know you are finished
15. The human will run `python check_my_work.py <your-module>` (or `python3` on Mac). It prints PASS or FAIL.
    You are finished ONLY when it prints PASS. If it prints FAIL, the human will paste the problems to you.
    Fix exactly those problems and change nothing else.
16. The `golden/` folder holds the current acceptance targets, but the human/integrator must verify legal references and material fixtures against the supplied SOP. If an output differs, compare the code, contract, golden fixture and SOP; do not silently change a fixture or blindly assume the fixture is legally correct. Flag any conflict for the human/integrator.
17. When you are done, tell the human in ONE line which file(s) to send to the integrator.

## E. The 8 mistakes AIs make most often on this project (do not make them)
- Using float or rounding in the middle of a calculation. (Round only at output.)
- Changing key names (e.g. `restorable_amount` -> `restorableAmount`).
- "Helpfully" adding a pandas / FastAPI / pydantic import.
- Writing a long explanation instead of the complete file.
- Using today's date instead of the `as_of` argument.
- Putting the user-supplied text into HTML without escaping it (`html.escape`). Never trust input text.
- Silently reinterpreting legal rules. Implement the agreed, source-checked contract; if the PERSON document conflicts with the supplied SOP or data contract, stop and flag the conflict for the integrator.
- Declaring "done" without the checker saying PASS.
