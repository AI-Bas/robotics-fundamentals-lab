# Workflow Rules (Low-Context, Repeatable)

## Objective

Keep progress durable across sessions without bloating chat context or re-discovery time.

## Daily Working Rules

- Work in small, testable increments.
- Validate each increment with one explicit command.
- Prefer deterministic scripts over ad-hoc manual steps.
- Keep hardware observations and code behavior clearly separated.

## Git Rules

- Commit frequently with why-focused messages.
- Include validation notes in commit body when useful.
- Keep commits scoped to one intent (feature/fix/docs).
- Do not push unless explicitly requested in chat.

## Handoff Rules

- Update `docs/session-handoff.md` at session end using the template in `docs/session-handoff-template.md`.
- Keep handoff concise (20-30 lines).
- Include one copy/paste restart block.
- Move long investigation details into dedicated docs.

## Verification Rules

- Every behavior change should have:
  - command used
  - expected output
  - observed output
- If observed behavior differs from expected, record the mismatch before changing code.

## LED/Sensor-Specific Rules (Current Project)

- Default operator behavior should use constrained raw LED window (`80..212`).
- Keep raw-linear and magic mapping modes available for diagnostics.
- Final smoke standby setting should be explicit and printed in output.
- Treat visual brightness as empirical unless externally measured.

## Future Calibration Rule

- Add external brightness feedback (LDR + ADC) before finalizing perceptual mapping.
- Build LUT-based control once measured data is available.
