# Session Handoff Template

Use this at the end of each session to keep next-chat context small and actionable.

## 1) Snapshot (5 lines max)

- Branch:
- Sync status (ahead/behind clean/dirty):
- Primary focus:
- Last validated command:
- Blocking issue (if any):

## 2) Current State

- **Done:** short bullet list of completed outcomes
- **In progress:** what is partially done
- **Not started:** what is next but untouched

## 3) Validation

- **Commands run:** exact commands used for verification
- **Observed result:** pass/fail and key outputs
- **Confidence:** high/medium/low with one-line reason

## 4) Next Action (Operator Ready)

Provide one copy/paste block that starts the next session quickly.

```bash
# Example
cd ~/robotics-fundamentals-lab/optical_flow
source .venv/bin/activate
python src/of_sensor_smoke.py --samples 4
```

## 5) Risks and Assumptions

- List only active risks that can affect next actions.
- Keep to 3 bullets max.

## 6) Backlog Pointer

- Link to longer-term docs/issues instead of expanding details here.

---

## Length Rules

- Target 20-30 lines total.
- Prefer commands and outcomes over narrative.
- If details exceed 30 lines, move them to a dedicated doc in `docs/`.
