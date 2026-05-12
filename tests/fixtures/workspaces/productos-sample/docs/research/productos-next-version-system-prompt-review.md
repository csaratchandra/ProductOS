# ProductOS Next-Version System Prompt Review

Review date: 2026-04-12

Source reviewed: `https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools`

## Executive Summary

This review inspected `83` prompt-bearing text or YAML files and `17` adjacent tool manifests across `32` vendor or product folders in the external system-prompt corpus. The purpose was not to copy vendor prompts into ProductOS. The purpose was to identify operating patterns that would materially improve ProductOS as a repo-first PM operating system for AI-assisted execution.

What stood out most:

- The strongest coding-agent prompts are not just “smart assistants.” They are explicit operating systems with planning, tool-use, validation, and reporting rules. `48` files showed strong planning structure and `43` showed clear verification behavior. ProductOS should keep this in the repo and expose it through thin adapters, not vendor-specific magic.
- Research-oriented prompts repeatedly enforce freshness, source handling, and formatting discipline. `61` files were explicitly research-connected. This is directly relevant to ProductOS discovery, market intelligence, and leadership/customer-facing narrative generation.
- Memory and steering are first-class in the stronger systems. `34` prompts visibly model workspace context, reusable steering docs, or retrieval behavior. ProductOS already has `memory_retrieval_state` and `intake_routing_state`; it should harden these into a more opinionated steering layer.
- Parallelism is present, but the better systems bound it. `43` prompts referenced parallel routes, task boundaries, or multi-step execution. This aligns with ProductOS swarm ambitions, but only if PM approval, reviewer stacks, and anti-loop controls remain explicit.
- Safety and approval are operational, not ceremonial. `29` prompts encoded refusal boundaries, approval rules, or claim controls. ProductOS should borrow that discipline for release claims, research freshness, and autonomous PM boundary enforcement.

## ProductOS Implications For The Next Version

Recommended next-version moves, in priority order:

- Add a mission-first mode router in ProductOS before deeper agent execution. Kiro, Antigravity, Qoder, and Orchids all show the value of separating planning, execution, and decision-routing instead of overloading one giant prompt.
- Harden a first-class planning artifact for complex work. Strong systems do not jump straight from request to implementation; they create visible plans, track status, and update progress. ProductOS should make this a standard governed surface inside `discover`, `align`, and `operate`.
- Enforce validation-before-claim across product, research, and messaging flows. Amp, Codex CLI, Cursor, Claude Code, Qoder, and VSCode Agent repeatedly treat tests and verification as part of the operating loop, not optional cleanup.
- Add explicit freshness and citation policy to ProductOS research surfaces. Perplexity and Notion AI are especially strong examples of search-first retrieval, source-aware answering, and answer formatting that does not bury the evidence model.
- Promote steering and reusable workspace context to a named ProductOS mechanism. Kiro steering files, Notion workspace semantics, and the memory-aware coding prompts all support the same pattern: stable instructions and prior context should be externalized, inspectable, and reusable.
- Keep adapters thin but measurable. The external repo is full of host-specific tool schemas; ProductOS should benchmark them in `runtime_adapter_registry` and adapter-parity artifacts, but should not let those tool surfaces become ProductOS logic.
- Add task-boundary progress reporting to the PM-visible cockpit. Antigravity, Codex CLI, and several IDE agents make long-running work easier to trust by exposing explicit step changes and current activity.
- Split small helper prompts from the main prompt. Poke, Xcode, Manus modules, and VSCode helper prompts show that micro-prompts are useful when the responsibility is narrow. ProductOS should use this pattern for reviewer, formatter, classifier, and presentation helpers.
- Improve ProductOS doc and deck generation using stronger presentation rules. v0, Dia, and Perplexity show disciplined output formatting, asset handling, and audience-aware rendering that can feed leadership and customer-ready artifacts without drifting from source truth.
- Keep PM approval explicit for decision-driving actions. Many leaked prompts push farther into autonomy than ProductOS should currently claim. ProductOS should borrow their control mechanics, not their marketing posture.

## Recommended ProductOS Changes

Specific repo surfaces that should absorb these lessons:

- `core/docs/thin-agent-adapter-model.md`: extend from “thin adapter” principle to an explicit adapter capability matrix covering planning, tool orchestration, citation/freshness, validation, delegation, and approval controls.
- `core/docs/runtime-state-model.md`: add a sharper route-budget and reviewer-stack policy informed by the bounded parallelism patterns seen in Codex CLI, Antigravity, and Qoder.
- `core/docs/continuous-intake-and-memory-model.md`: add a named steering/context layer for reusable workspace instructions, stable norms, and retrieved memory with provenance.
- `core/docs/live-doc-and-messaging-model.md`: add formatting and evidence rules for leadership- and customer-facing outputs so messaging stays traceable to artifacts.
- `core/docs/research-command-center-model.md` and related research artifacts: incorporate search-first freshness and citation expectations similar to Perplexity and Notion AI.
- `tests/fixtures/workspaces/productos-sample/artifacts/runtime_adapter_registry.example.json`: expand to record prompt-pattern capabilities, not just host parity.
- `tests/fixtures/workspaces/productos-sample/artifacts/orchestration_state` and `cockpit_state` examples: show task boundary, current stage, next action, reviewer lane, and blocked reason explicitly.

## What ProductOS Should Not Copy

- Do not import vendor-specific UX tricks as core architecture. Examples: Dia Ask-links, Notion compressed URL semantics, v0 framework defaults, and browser-only media tags.
- Do not move operating truth into hidden prompt lore. The external corpus is useful precisely because it shows how much behavior vendors hide; ProductOS should keep core rules in docs, schemas, tests, and artifacts.
- Do not broaden autonomous PM claims just because other prompts sound confident. ProductOS still needs proof, reviewer discipline, and repeatable Ralph-complete runs.
- Do not make tool manifests the product. Tool catalogs change quickly; ProductOS should stay repo-first and adapter-thin.

## Review Method

- Pulled the source repository on 2026-04-12 and unpacked it locally for inspection.
- Counted and reviewed all prompt-bearing `.txt`, `.yaml`, and prompt-named files, while separating adjacent `.json` tool manifests.
- Classified each file by likely role: primary prompt, planning prompt, spec prompt, helper, classifier, or micro action.
- Mapped each file to what would actually improve ProductOS versus what is merely product-specific leakage.

## File-By-File Inventory

The tables below list every prompt-bearing file found in the reviewed repository. “ProductOS use” is intentionally opinionated: it states whether the file is strategically useful, weakly useful, or mostly noise for ProductOS next-version work.

### Amp

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Amp/claude-4-sonnet.yaml` | Full agent config | Large embedded agent configuration that combines identity, tools, plan quality rules, and code-edit workflow. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Amp/gpt-5.yaml` | Full agent config | Large embedded agent configuration parallel to the Claude variant, with stronger approval and patch language. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |

### Anthropic

Adjacent tool manifests: `Anthropic/Claude Code/Tools.json`, `Anthropic/Claude for Chrome/Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Anthropic/Claude Code 2.0.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Anthropic/Claude Code/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Anthropic/Claude Sonnet 4.6.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Anthropic/Claude for Chrome/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Anthropic/Sonnet 4.5 Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, memory/context handling. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### Augment Code

Adjacent tool manifests: `Augment Code/claude-4-sonnet-tools.json`, `Augment Code/gpt-5-tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Augment Code/claude-4-sonnet-agent-prompts.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior. |
| `Augment Code/gpt-5-agent-prompts.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, fresh evidence gathering. |

### Cluely

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Cluely/Default Prompt.txt` | Primary prompt | Chat/research prompt emphasizing explicit planning. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Cluely/Enterprise Prompt.txt` | Primary prompt | Chat/research prompt emphasizing explicit planning. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### CodeBuddy Prompts

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `CodeBuddy Prompts/Chat Prompt.txt` | Chat prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Interesting benchmark signal, but lower-priority for ProductOS than the stronger planning, validation, and governance-oriented prompts. |
| `CodeBuddy Prompts/Craft Prompt.txt` | Builder prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, approval/safety gates. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### Comet Assistant

Adjacent tool manifests: `Comet Assistant/tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Comet Assistant/System Prompt.txt` | Primary system prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### Cursor Prompts

Adjacent tool manifests: `Cursor Prompts/Agent Tools v1.0.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Cursor Prompts/Agent CLI Prompt 2025-08-07.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Cursor Prompts/Agent Prompt 2.0.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Cursor Prompts/Agent Prompt 2025-09-03.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Cursor Prompts/Agent Prompt v1.0.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, parallel route handling. | Useful as a thin-adapter benchmark for Ralph-compatible planning, bounded swarm/parallel route control, fresh evidence gathering. |
| `Cursor Prompts/Agent Prompt v1.2.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Cursor Prompts/Chat Prompt.txt` | Chat prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research. | Useful as a thin-adapter benchmark for Ralph-compatible planning, fresh evidence gathering. |

### Devin AI

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Devin AI/DeepWiki Prompt.txt` | Research prompt | Coding-agent prompt emphasizing freshness-aware research. | Useful as a thin-adapter benchmark for fresh evidence gathering. |
| `Devin AI/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |

### Emergent

Adjacent tool manifests: `Emergent/Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Emergent/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules, memory/context handling. | Useful as a thin-adapter benchmark for validation-before-claim behavior, workspace memory or steering, fresh evidence gathering. |

### Google

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Google/Antigravity/Fast Prompt.txt` | Primary prompt | Execution-heavy coding agent that still preserves visible task status and verification posture. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Google/Antigravity/planning-mode.txt` | Planning-mode prompt | Dedicated planning lane with task-boundary updates, review checkpoints, and artifact expectations. | Strong fit for turning ProductOS discover/align work into explicit plan artifacts before operate-mode execution begins. |
| `Google/Gemini/AI Studio vibe-coder.txt` | Fast-build prompt | Coding-agent prompt emphasizing freshness-aware research, approval/safety gates. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### Junie

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Junie/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research. | Interesting benchmark signal, but lower-priority for ProductOS than the stronger planning, validation, and governance-oriented prompts. |

### Kiro

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Kiro/Mode_Clasifier_Prompt.txt` | Classifier prompt | Intent classifier that routes users into the right operating mode before deeper work starts. | Strong fit for ProductOS mode routing: mission classification, workflow entry, and reviewer/referee escalation before execution fans out. |
| `Kiro/Spec_Prompt.txt` | Spec prompt | Spec-first delivery surface for requirements, design, and implementation sequencing. | Strong fit for turning ProductOS discover/align work into explicit plan artifacts before operate-mode execution begins. |
| `Kiro/Vibe_Prompt.txt` | Fast-build prompt | Faster builder mode that still keeps planning, testing, and context hooks visible. | High leverage for ProductOS because it cleanly separates classifier, spec, and fast-build modes instead of overloading one giant PM prompt. |

### Leap.new

Adjacent tool manifests: `Leap.new/tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Leap.new/Prompts.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules, memory/context handling. | Interesting benchmark signal, but lower-priority for ProductOS than the stronger planning, validation, and governance-oriented prompts. |

### Lovable

Adjacent tool manifests: `Lovable/Agent Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Lovable/Agent Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |

### Manus Agent Tools & Prompt

Adjacent tool manifests: `Manus Agent Tools & Prompt/tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Manus Agent Tools & Prompt/Agent loop.txt` | Loop controller | Minimal controller prompt that frames the overall execution loop. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Manus Agent Tools & Prompt/Modules.txt` | Capability module | Capability and workflow module that broadens Manus beyond one static prompt. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Manus Agent Tools & Prompt/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### NotionAi

Adjacent tool manifests: `NotionAi/tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `NotionAi/Prompt.txt` | Primary prompt | Workspace operating prompt for search-first knowledge retrieval and structured page/database actions. | Useful for ProductOS knowledge/workspace surfaces: default search-first retrieval, structured action semantics, and doc/database mutation rules. |

### Open Source prompts

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Open Source prompts/Bolt/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules, approval/safety gates. | Interesting benchmark signal, but lower-priority for ProductOS than the stronger planning, validation, and governance-oriented prompts. |
| `Open Source prompts/Cline/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Open Source prompts/Codex CLI/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing approval/safety gates. | Useful as a thin-adapter benchmark for thin-adapter benchmarking. |
| `Open Source prompts/Codex CLI/openai-codex-cli-system-prompt-20250820.txt` | Primary prompt | Terminal agent prompt with concise preambles, plan updates, sandbox awareness, and apply-patch discipline. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Open Source prompts/Gemini CLI/google-gemini-cli-system-prompt.txt` | Primary prompt | CLI coding prompt with safety and tool-use structure similar to modern repo agents. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Open Source prompts/Lumo/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Open Source prompts/RooCode/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |

### Orchids.app

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Orchids.app/Decision-making prompt.txt` | Decision prompt | Decision router used to arbitrate next actions rather than generate final work product. | Strong fit for ProductOS mode routing: mission classification, workflow entry, and reviewer/referee escalation before execution fans out. |
| `Orchids.app/System Prompt.txt` | Primary system prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful for ProductOS decision-routing and supervised builder loops, especially where PM approval must stay explicit. |

### Perplexity

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Perplexity/Prompt.txt` | Primary prompt | Search-answering surface with strict formatting and per-sentence citation discipline. | Directly useful for Discover and research-command-center surfaces: freshness, citation placement, and leadership-grade formatting. |

### Poke

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Poke/Poke agent.txt` | Prompt variant | Chat/research prompt emphasizing freshness-aware research, parallel route handling. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p1.txt` | Prompt variant | Chat/research prompt emphasizing freshness-aware research, parallel route handling, approval/safety gates. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p2.txt` | Prompt variant | WhatsApp-specific operational constraint prompt. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p3.txt` | Prompt variant | Behavioral recovery prompt for user frustration and mistakes. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p4.txt` | Prompt variant | Integration-handling prompt for connected systems. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p5.txt` | Prompt variant | Protocol note for email-link behavior. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |
| `Poke/Poke_p6.txt` | Prompt variant | Memory/context persistence helper. | Useful as a reminder to split operational constraints into small auxiliary prompts. Better for adapter layering than for ProductOS core behavior. |

### Qoder

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Qoder/Quest Action.txt` | Execution prompt | Coding-agent prompt emphasizing explicit planning, verification rules, memory/context handling. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `Qoder/Quest Design.txt` | Design prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Strong fit for turning ProductOS discover/align work into explicit plan artifacts before operate-mode execution begins. |
| `Qoder/prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |

### Replit

Adjacent tool manifests: `Replit/Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Replit/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, parallel route handling. | Useful as a thin-adapter benchmark for Ralph-compatible planning, bounded swarm/parallel route control. |

### Same.dev

Adjacent tool manifests: `Same.dev/Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Same.dev/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |

### Trae

Adjacent tool manifests: `Trae/Builder Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Trae/Builder Prompt.txt` | Builder prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules, memory/context handling. | Useful as a thin-adapter benchmark for validation-before-claim behavior, workspace memory or steering, fresh evidence gathering. |
| `Trae/Chat Prompt.txt` | Chat prompt | Coding-agent prompt emphasizing freshness-aware research. | Useful as a thin-adapter benchmark for fresh evidence gathering. |

### Traycer AI

Adjacent tool manifests: `Traycer AI/phase_mode_tools.json`, `Traycer AI/plan_mode_tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Traycer AI/phase_mode_prompts.txt` | Primary prompt | Coding-agent prompt emphasizing heavy tool orchestration. | Useful as a reference for shaping ProductOS adapter behavior without moving core logic out of the repo. |
| `Traycer AI/plan_mode_prompts` | Planning-mode prompt | Coding-agent prompt emphasizing explicit planning. | Strong fit for turning ProductOS discover/align work into explicit plan artifacts before operate-mode execution begins. |

### VSCode Agent

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `VSCode Agent/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `VSCode Agent/chat-titles.txt` | UI helper | Title-generation helper for chat organization rather than core reasoning. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `VSCode Agent/claude-sonnet-4.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing explicit planning, freshness-aware research, parallel route handling. | Useful as a thin-adapter benchmark for Ralph-compatible planning, bounded swarm/parallel route control, fresh evidence gathering. |
| `VSCode Agent/gemini-2.5-pro.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing freshness-aware research, parallel route handling. | Useful as a thin-adapter benchmark for bounded swarm/parallel route control, fresh evidence gathering. |
| `VSCode Agent/gpt-4.1.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing freshness-aware research, parallel route handling. | Useful as a thin-adapter benchmark for bounded swarm/parallel route control, fresh evidence gathering. |
| `VSCode Agent/gpt-4o.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing freshness-aware research, parallel route handling. | Useful as a thin-adapter benchmark for bounded swarm/parallel route control, fresh evidence gathering. |
| `VSCode Agent/gpt-5-mini.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `VSCode Agent/gpt-5.txt` | Model-specific prompt variant | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, bounded swarm/parallel route control. |
| `VSCode Agent/nes-tab-completion.txt` | Inline completion prompt | Inline edit-completion helper focused on precise local code changes. | Useful as a thin-adapter benchmark for validation-before-claim behavior, bounded swarm/parallel route control, fresh evidence gathering. |

### Warp.dev

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Warp.dev/Prompt.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules, memory/context handling. | Useful as a thin-adapter benchmark for validation-before-claim behavior, workspace memory or steering, fresh evidence gathering. |

### Windsurf

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Windsurf/Prompt Wave 11.txt` | Primary prompt | Coding-agent prompt emphasizing explicit planning, freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for Ralph-compatible planning, validation-before-claim behavior, workspace memory or steering. |
| `Windsurf/Tools Wave 11.txt` | Prompt variant | Coding-agent prompt emphasizing freshness-aware research, memory/context handling, parallel route handling. | Useful as a thin-adapter benchmark for bounded swarm/parallel route control, workspace memory or steering, fresh evidence gathering. |

### Xcode

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Xcode/DocumentAction.txt` | Micro action prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `Xcode/ExplainAction.txt` | Micro action prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `Xcode/MessageAction.txt` | Micro action prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `Xcode/PlaygroundAction.txt` | Micro action prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `Xcode/PreviewAction.txt` | Micro action prompt | Chat/research prompt with relatively light behavioral structure compared with the stronger agent surfaces. | Low strategic leverage. Mostly useful as a reminder that ProductOS may want small presentation helpers, but not as core runtime design. |
| `Xcode/System.txt` | Primary system prompt | Code-analysis assistant prompt for IDE help inside the active file context. | Interesting benchmark signal, but lower-priority for ProductOS than the stronger planning, validation, and governance-oriented prompts. |

### Z.ai Code

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `Z.ai Code/prompt.txt` | Primary prompt | Coding-agent prompt emphasizing freshness-aware research, verification rules. | Useful as a thin-adapter benchmark for validation-before-claim behavior, fresh evidence gathering. |

### dia

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `dia/Prompt.txt` | Primary prompt | Browser-native chat prompt with response decoration rules, inline follow-up links, and media placement logic. | Useful for output presentation ideas, but ProductOS should borrow the response-decoration discipline, not browser-specific hyperlink/media mechanics. |

### v0 Prompts and Tools

Adjacent tool manifests: `v0 Prompts and Tools/Tools.json`.

| File | Type | Observed Focus | ProductOS Use |
| --- | --- | --- | --- |
| `v0 Prompts and Tools/Prompt.txt` | Primary prompt | High-control builder prompt tuned for UI generation, asset handling, scripts, and framework defaults. | Useful for ProductOS document/deck/build generation: strong environment defaults, asset handling, and user-question gating. |

## Tool Manifest Appendix

These files are not themselves the main prompt bodies, but they are still useful because they reveal what each host treats as a first-class tool surface.

| Tool Manifest | Why It Matters To ProductOS |
| --- | --- |
| `Anthropic/Claude Code/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Anthropic/Claude for Chrome/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Augment Code/claude-4-sonnet-tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Augment Code/gpt-5-tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Comet Assistant/tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Cursor Prompts/Agent Tools v1.0.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Emergent/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Leap.new/tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Lovable/Agent Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Manus Agent Tools & Prompt/tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `NotionAi/tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Replit/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Same.dev/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Trae/Builder Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Traycer AI/phase_mode_tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `Traycer AI/plan_mode_tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |
| `v0 Prompts and Tools/Tools.json` | Useful adapter benchmark for tool capability coverage, invocation shape, and what the host assumes the agent may do. |

## Bottom Line

The biggest lesson from this corpus is that the winning systems are not relying on one magical system prompt. They combine mode selection, visible plans, tool contracts, memory retrieval, validation rules, and bounded autonomy. ProductOS already has many of the right repo-level ingredients. The next version should turn those ingredients into a tighter governed operating loop and a clearer PM-visible control surface, while keeping the repository, not the hidden prompt, as the system of record.
