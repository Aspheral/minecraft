# Solar Shader Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the durable Solar Shader repository workspace, benchmark documentation, AutoTune boundaries, and agent-facing project documentation without introducing speculative rendering or companion-mod implementation.

**Architecture:** `Aspheral/minecraft` remains a multi-project monorepo with Solar Shader isolated under `Solar-Shader/`. This milestone creates only the documentation and directory boundaries defined by the approved specification, using README-backed directories where Git cannot preserve empty folders. GitHub is the canonical project state and all verification is read-back/static verification only.

**Tech Stack:** GitHub repository contents, Markdown, Iris shaderpack directory conventions documented through Context7.

**Spec:** `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-workspace-design.md`

## Global Constraints

- Repository: `Aspheral/minecraft`.
- Project root: `Solar-Shader/`.
- Implementation branch: `feat/solar-workspace`.
- `main` remains the stable integrated branch.
- Permanent project boundaries are directories, not branches.
- Solar Shader runtime files eventually live under `Solar-Shader/shaders/`.
- Shared GLSL libraries eventually live under `Solar-Shader/shaders/lib/`.
- `shaders.properties` eventually lives at `Solar-Shader/shaders/shaders.properties`.
- Primary mainstream design baseline: at least 120 FPS during normal gameplay at 1080p under defined benchmark conditions.
- 120 FPS nominal total frame budget: 8.33 ms.
- Lower intentional FPS targets unlock larger quality budgets and must not be treated as performance failures.
- Solar must protect a minimum cinematic quality floor.
- No actual rendering pipeline, AutoTune controller, companion-mod implementation, fabricated benchmark result, or fake Iris runtime validation may be added in this milestone.
- Static validation must never be described as proof of Minecraft/Iris runtime behavior.
- Context7 should be used for version-sensitive Iris/Sodium assumptions rather than guessing.

## Review Focus

1. **Future multi-project growth:** root documentation must make it obvious that Solar Shader is one project inside a monorepo rather than the repository itself.
2. **Chat-only development:** a future ChatGPT session with no local IDE or Minecraft runtime must be able to identify the canonical spec, project root, validation limits, and next architectural step from repository files alone.
3. **Intentional 60 FPS cap:** benchmark/AutoTune documentation must state that a lower intentional cap increases available visual-quality budget rather than signaling overload.
4. **High-refresh hardware:** documentation must preserve 120 FPS as the default cinematic-performance target for uncapped or >120 FPS play unless the user explicitly selects a higher target.
5. **No false validation claims:** benchmark and architecture docs must explicitly separate static checks from real in-game FPS/visual verification.

---

### Task 1: Establish Monorepo and Solar Project Entry Points

**Files:**
- Create: `README.md`
- Create: `Solar-Shader/README.md`
- Create: `Solar-Shader/CHANGELOG.md`

**Interfaces:**
- Consumes: approved workspace spec at `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-workspace-design.md`.
- Produces: canonical human/agent entry points linking to the spec and describing the monorepo/project boundary.

- [ ] **Step 1: Verify the entry-point files do not already exist on `feat/solar-workspace`**

Use GitHub `fetch_file` for:
- `README.md`
- `Solar-Shader/README.md`
- `Solar-Shader/CHANGELOG.md`

Expected: each absent file returns not-found. If any exists, read it fully and change the plan action for that path from create to update while preserving unrelated content.

- [ ] **Step 2: Create root `README.md`**

Required assertions:
- contains `Aspheral/minecraft`,
- describes the repository as a monorepo for multiple Minecraft projects,
- links to `Solar-Shader/`,
- states that permanent projects use directories and development uses temporary branches.

- [ ] **Step 3: Create `Solar-Shader/README.md`**

Required assertions:
- names the project `Solar Shader`,
- states the cinematic + high-performance goal,
- states the 120 FPS mainstream baseline and 1080p benchmark focus,
- explains that lower intentional FPS targets permit larger visual budgets,
- summarizes the hybrid AutoTune architecture,
- links to the approved spec,
- states that current workspace status is pre-renderer/scaffolding,
- distinguishes static validation from actual Minecraft/Iris runtime verification.

- [ ] **Step 4: Create `Solar-Shader/CHANGELOG.md`**

Required assertions:
- contains an `Unreleased` section,
- records workspace/spec establishment,
- does not claim any rendering feature is implemented.

- [ ] **Step 5: Read back all three files and verify assertions**

Use GitHub `fetch_file` on all three paths.

Expected: all paths exist and every required assertion is present.

- [ ] **Step 6: Commit task**

Commit message:

```text
docs: establish Solar Shader workspace entry points
```

---

### Task 2: Establish Architecture, Benchmark, Tooling, and AutoTune Boundaries

**Files:**
- Create: `Solar-Shader/docs/architecture/README.md`
- Create: `Solar-Shader/benchmarks/README.md`
- Create: `Solar-Shader/tools/README.md`
- Create: `Solar-Shader/companion/Solar-AutoTune/README.md`

**Interfaces:**
- Consumes: product/performance/AutoTune contracts from the approved spec.
- Produces: durable ownership boundaries for architecture decisions, benchmark methodology/results, development tooling, and the optional companion.

- [ ] **Step 1: Verify the four boundary files do not already exist**

Use GitHub `fetch_file` on each path.

Expected: not-found for absent files. If any exists, read it fully before updating.

- [ ] **Step 2: Create architecture README**

Required assertions:
- architecture docs are for durable rendering/system decisions,
- links to the approved workspace spec,
- states rendering systems require their own later design/spec cycles,
- names performance as a first-class architectural constraint,
- states AutoTune must protect a minimum cinematic quality floor.

- [ ] **Step 3: Create benchmark README**

Required assertions:
- defines 1080p mainstream and 1440p upper-mainstream benchmark profiles,
- records 12–16 chunks for the main baseline,
- lists required scene categories from the spec,
- lists average FPS and 1% lows,
- records target FPS, configured cap where known, VSync where known, and refresh rate where known,
- includes `budget_ms = 1000 / target_fps`,
- explicitly gives 60 FPS = 16.67 ms, 120 FPS = 8.33 ms, 240 FPS = 4.17 ms,
- states total frame budget is not entirely available to the shader,
- prohibits presenting static/synthetic checks as measured in-game FPS.

- [ ] **Step 4: Create tools README**

Required assertions:
- reserves `tools/` for development/validation/benchmark tooling,
- prohibits claiming generic GLSL/static checks prove Iris runtime correctness,
- states tools should be added only when a later plan needs them.

- [ ] **Step 5: Create Solar AutoTune companion README**

Required assertions:
- companion is optional,
- shaderpack remains usable without it,
- companion may use hardware/configuration information where supported,
- intended inputs include display resolution, render distance, configured FPS cap, VSync/refresh behavior where supported, and measured performance,
- explicitly distinguishes an intentional cap from rendering overload,
- states exact Iris/Sodium integration must be verified in a later dedicated architecture cycle,
- contains no invented API or implementation claim.

- [ ] **Step 6: Read back all four files and verify assertions**

Expected: every path exists and all required content is present.

- [ ] **Step 7: Commit task**

Commit message:

```text
docs: define Solar architecture and AutoTune boundaries
```

---

### Task 3: Establish Shader Source and Superpowers Planning Boundaries

**Files:**
- Create: `Solar-Shader/shaders/lib/README.md`
- Create: `Solar-Shader/docs/superpowers/plans/README.md`

**Interfaces:**
- Consumes: Iris directory assumptions and Superpowers workflow from the approved spec.
- Produces: clear future locations for reusable GLSL and implementation plans.

- [ ] **Step 1: Verify both files do not already exist**

Use GitHub `fetch_file`.

Expected: not-found unless a prior partial setup created them.

- [ ] **Step 2: Create shader library README**

Required assertions:
- this directory is reserved for reusable GLSL includes,
- runtime shader implementation is not part of the workspace milestone,
- future files must follow verified Iris conventions,
- version-sensitive behavior should be checked through current documentation before implementation.

- [ ] **Step 3: Create plans README**

Required assertions:
- approved implementation plans live here,
- plans must link to their authoritative spec,
- substantial new systems follow brainstorm → spec → plan → implement → verify → review,
- GitHub state overrides conversation recollection.

- [ ] **Step 4: Read back and verify both files**

Expected: both paths exist and assertions are present.

- [ ] **Step 5: Commit task**

Commit message:

```text
docs: establish Solar shader and planning boundaries
```

---

### Task 4: Add Agent Continuity and Current-State Documentation

**Files:**
- Create: `Solar-Shader/AGENT.md`
- Create: `Solar-Shader/ROADMAP.md`

**Interfaces:**
- Consumes: all workspace entry-point and boundary documentation from Tasks 1–3.
- Produces: compact durable instructions that let later normal-ChatGPT sessions resume correctly without depending on conversation memory.

- [ ] **Step 1: Verify `AGENT.md` and `ROADMAP.md` do not already exist**

Use GitHub `fetch_file`.

Expected: not-found unless previously created.

- [ ] **Step 2: Create `Solar-Shader/AGENT.md`**

Required assertions:
- GitHub is the canonical source of truth,
- inspect current files/spec/plans/recent commits before modifying Solar,
- use Superpowers for substantial architectural work,
- use Context7 for current Iris/Sodium/version-sensitive documentation,
- never claim static checks prove visual quality or FPS,
- do not implement on `main` without explicit approval,
- Solar-specific work stays under `Solar-Shader/`,
- respect the target-FPS-aware AutoTune contract,
- do not ask the user to do work an available connected tool can perform.

- [ ] **Step 3: Create `Solar-Shader/ROADMAP.md`**

Required assertions:
- milestone 0: workspace/documentation,
- next milestone: shader foundation architecture,
- later milestone families include lighting/shadows, atmosphere/clouds, materials/water, temporal reconstruction, adaptive performance, and optional companion,
- each major rendering subsystem gets its own design/spec cycle before implementation,
- roadmap ordering is directional rather than a claim that every listed feature is already approved.

- [ ] **Step 4: Read back both files and verify assertions**

Expected: both files exist and provide enough state for a new ChatGPT session to resume without relying on prior-chat memory.

- [ ] **Step 5: Commit task**

Commit message:

```text
docs: add Solar agent continuity and roadmap
```

---

### Task 5: Whole-Workspace Verification

**Files:**
- Verify only. Do not add rendering code.

**Interfaces:**
- Consumes: all outputs from Tasks 1–4.
- Produces: evidence that the workspace matches the approved spec and contains no premature implementation.

- [ ] **Step 1: Verify every required workspace path**

Use GitHub `fetch_file` for:

```text
README.md
Solar-Shader/README.md
Solar-Shader/CHANGELOG.md
Solar-Shader/AGENT.md
Solar-Shader/ROADMAP.md
Solar-Shader/benchmarks/README.md
Solar-Shader/companion/Solar-AutoTune/README.md
Solar-Shader/docs/architecture/README.md
Solar-Shader/docs/superpowers/specs/2026-09-29-solar-workspace-design.md
Solar-Shader/docs/superpowers/plans/README.md
Solar-Shader/docs/superpowers/plans/2026-09-29-solar-workspace.md
Solar-Shader/shaders/lib/README.md
Solar-Shader/tools/README.md
```

Expected: every path exists.

- [ ] **Step 2: Verify target-FPS-aware AutoTune invariants**

Confirm repository documentation states all of the following:

- 120 FPS remains the mainstream design baseline,
- 120 FPS = 8.33 ms total frame budget,
- 60 FPS = 16.67 ms total frame budget,
- intentional lower caps can receive higher quality,
- uncapped or >120 FPS defaults to the 120 FPS cinematic-performance target unless the user explicitly selects higher,
- `frameTime` alone must not be used to infer an FPS cap,
- the shader remains useful without the optional companion,
- no runtime benchmark result is claimed without real runtime evidence.

Expected: all invariants present.

- [ ] **Step 3: Verify no premature implementation was introduced**

Inspect files added on this branch.

Expected:
- no `.vsh`, `.fsh`, `.csh`, executable AutoTune implementation, or fabricated benchmark result was introduced by this workspace plan,
- documentation may mention future files/features but must not claim they already work.

- [ ] **Step 4: Verify project isolation**

Expected:
- Solar-specific workspace files live under `Solar-Shader/` except the monorepo root `README.md`,
- no unrelated Minecraft project path is modified.

- [ ] **Step 5: Record verification outcome**

If all checks pass, update `Solar-Shader/CHANGELOG.md` under `Unreleased` to state that the workspace scaffolding milestone has been established. Do not claim runtime shader functionality.

- [ ] **Step 6: Read back the changelog and final required paths**

Expected: workspace status is accurately documented and all required files remain readable.

- [ ] **Step 7: Commit verification/status update**

Commit message:

```text
docs: complete Solar workspace scaffolding
```

---

## Completion Contract

This plan is complete only when:

1. Every Task 1–5 checkbox is satisfied with fresh GitHub read-back evidence.
2. The approved spec remains present and authoritative.
3. The repository exposes the monorepo/project boundary clearly.
4. The 120 FPS baseline and target-FPS-aware AutoTune philosophy are documented in durable project files.
5. The optional companion has a boundary but no invented implementation.
6. Static validation limitations are explicit.
7. No rendering pipeline has been prematurely introduced.
8. The workspace clearly points to the next architectural cycle: shader foundation.
9. A whole-branch review is performed before integration.
