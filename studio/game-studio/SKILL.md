---
name: game-studio
description: Develop and maintain the user's paid games using the shared studio workflow, including new game setup, implementation, verification, mobile test delivery, and handoff. Use for this user's game projects or requests to start a new paid game; do not apply to unrelated software or assume authority to publish a new product.
---

Use this skill to reduce repeated instructions across the user's game projects. Communicate in Traditional Chinese. Read the current project's AGENTS.md, HANDOFF.md and studio.project.json before deciding scope; their verified project-specific constraints take precedence over these defaults.

- For a new game idea, read [the architecture](references/architecture.md), then use `scripts/studio.py init` to create the agreed destination. Accept a natural-language idea; infer reversible prototype choices and record assumptions. Ask only for missing consequential identity, audience or commercial decisions. Do not create a separate Codex task unless the user requests one.
- For an existing game, run `scripts/studio.py check --root <project>`, inspect Git and actual artifacts, then follow its configured test/build procedures. This check validates configuration only; it does not run tests or grant release approval.
- Keep game rules separate from platform services conceptually. Do not refactor an existing single-file game merely to match a new template. For a platform failure, test the user action through the bridge and verify the built artifact; browser mocks cannot prove an Android picker works.
- Default to one agent. Read the delegation criteria in the architecture when independent work would help; additional agents require this user's authorization under the project policy. A single writer owns each shared game artifact. Never run performance tests against competing agents, browsers or builds.
- Preserve test failures. Run full regression, change-specific edges, and agreed stress/offline/fresh-save checks. Record actual source hashes and distinguish pass/fail/not-run. CPU-constrained local runs do not silently satisfy an all-parallel gate.
- Deliver mobile test builds through the project's explicitly authorized fixed channel. Maintain app identity, signing continuity and increasing version codes. New projects inherit the workflow, never another game's keys, app ID, price or publishing authorization. Official store publication and pricing changes need their own authorization.
- Update a concise handoff and the decision/history log; report exact commit Summary, fixed test URL, evidence and device checks still needed. Commit/push only within existing project authorization.

If the user wants to brainstorm in ChatGPT first, provide [the idea brief](references/idea-brief.md). It is optional; accept their natural-language idea here as well. Treat returned research as proposals to verify against the repository, not as permission to publish or replace tested code.

The skill is a reusable operating workflow and project initializer, not an autonomous background service, a completed game engine, or a guarantee of store acceptance.
