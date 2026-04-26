# Workflow Rules (Low-Context, Repeatable)

## Objective

Keep progress durable across sessions without bloating chat context or re-discovery time.

## Source of Truth Order

When documentation overlaps, use this precedence:

1. `docs/ball-rotation-architecture.md` (system architecture and hardware references)
2. `docs/project-todo.md` (active backlog, priorities, troubleshooting notes)
3. `docs/conventions.md` (project-wide conventions)
4. `docs/modules/*.md` (module-specific implementation details)
5. `docs/session-handoff.md` (latest session snapshot)
6. `docs/planning/*.md` (archived/imported planning snapshots; reference only)

Long-term planning must live in the canonical docs (`architecture`, `project-todo`, `conventions`), not in snapshot files.

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
- Keep long-term tasks out of handoff; place them in `docs/project-todo.md`.

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

## Consolidation Rule

- Avoid creating new top-level planning docs when an existing source-of-truth file already fits.
- Consolidate old one-off plans into architecture, module docs, or project todo and then retire the redundant doc.
- Keep `docs/planning/` for imported or milestone snapshots only.

## Cross-Reference And Status Rule

- When updating a module, update both:
  - architecture/module planning docs under `docs/`
  - the module summary index under `<module>/<module>_documentation/<module>-documentation.md`
- Module summary indexes should include:
  - component quick reference
  - source URL quick links
  - latest status snapshot (`todo`/`doing`/`blocked`/`done`)
- Source-of-truth precedence remains unchanged: `docs/` is authoritative when conflicts appear.
- Local module documentation folders should be checked for new vendor files whenever work is requested on that module.
