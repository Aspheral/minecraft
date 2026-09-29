# Solar Shader Workspace Design

**Date:** 2026-09-29  
**Repository:** `Aspheral/minecraft`  
**Project root:** `Solar-Shader/`  
**Status:** Proposed workspace specification awaiting user review

## 1. Purpose

`Aspheral/minecraft` is a monorepo intended to hold multiple independent Minecraft-related projects over time. Solar Shader is the first project and must remain isolated under `Solar-Shader/`.

The repository must be structured so ChatGPT can use GitHub as the canonical source of truth while development is performed entirely through normal ChatGPT conversations, without assuming a local IDE, local terminal, Minecraft installation, Codex, or ChatGPT Work.

## 2. Repository Model

Permanent project boundaries are directories, not branches.

- `main` is the stable integrated state of the Minecraft monorepo.
- `Solar-Shader/` permanently contains Solar Shader.
- Future Minecraft projects receive their own top-level directories.
- Feature branches are temporary development timelines and are merged back into `main`.
- Solar Shader work must not modify unrelated top-level projects unless explicitly requested.

Example future monorepo:

```text
minecraft/
├── README.md
├── Solar-Shader/
├── Another-Shader/
├── Mods/
├── Resource-Packs/
└── Tools/
```

## 3. Solar Shader Workspace Target

The first workspace implementation should establish documentation and project boundaries without prematurely generating a large shader pipeline.

Initial target structure:

```text
minecraft/
├── README.md
└── Solar-Shader/
    ├── README.md
    ├── CHANGELOG.md
    ├── docs/
    │   ├── architecture/
    │   │   └── README.md
    │   └── superpowers/
    │       ├── specs/
    │       │   └── 2026-09-29-solar-workspace-design.md
    │       └── plans/
    │           └── README.md
    └── shaders/
        └── lib/
            └── README.md
```

The implementation plan may simplify placeholder files where Git does not preserve empty directories. No actual rendering implementation belongs in this workspace-only milestone.

## 4. Shaderpack Layout Assumptions

Current Iris documentation confirms that a shaderpack contains a top-level `shaders/` directory inside the pack root. Shared GLSL library files may be organized under `shaders/lib/`, and `shaders.properties` belongs inside `shaders/` when introduced.

Accordingly:

- `Solar-Shader/` is the eventual shaderpack root.
- Runtime shader files will live under `Solar-Shader/shaders/`.
- Shared GLSL modules will live under `Solar-Shader/shaders/lib/`.
- `shaders.properties` will eventually live at `Solar-Shader/shaders/shaders.properties`.
- Runtime files should be introduced by later implementation milestones, not by workspace scaffolding simply to make the tree look full.

## 5. Documentation Model

Durable architectural knowledge must live in the repository rather than only in ChatGPT conversations.

Solar-specific Superpowers artifacts live under:

- `Solar-Shader/docs/superpowers/specs/`
- `Solar-Shader/docs/superpowers/plans/`

Additional long-lived architectural documentation lives under:

- `Solar-Shader/docs/architecture/`

The Solar README should eventually identify:
- project purpose,
- current development status,
- compatibility targets once decided,
- repository layout,
- validation limitations,
- links to architectural documentation.

The monorepo root README should explain that `Aspheral/minecraft` contains multiple Minecraft projects and link to Solar Shader.

## 6. Branching Model

Use `main` for stable integrated work.

Solar Shader branches should be descriptive and scoped, for example:

- `feat/solar-workspace`
- `feat/solar-foundation`
- `feat/solar-lighting`
- `feat/solar-shadows`
- `feat/solar-water`
- `feat/solar-atmosphere`
- `fix/solar-<issue>`

Branches are not permanent containers for independent projects.

Substantial future feature work should normally:
1. start from current `main`,
2. use a focused branch,
3. make small meaningful commits,
4. receive available static/CI verification,
5. be reviewed,
6. merge back into `main`.

## 7. ChatGPT Development Contract

Before modifying Solar Shader, ChatGPT should inspect:
1. the relevant repository files,
2. the approved specification and implementation plan for the task,
3. recent relevant commits,
4. current external documentation when behavior may have changed.

GitHub is the canonical project state. Conversation memory must never override the current repository contents.

For substantial new systems, use the Superpowers flow:
1. brainstorm,
2. approve design,
3. commit specification,
4. review specification,
5. write implementation plan,
6. review plan and choose execution method,
7. implement,
8. verify,
9. review and merge.

## 8. Validation Boundaries

The project has no guaranteed Minecraft runtime available during ChatGPT-only development.

Therefore:
- source inspection is static validation,
- generic GLSL compilation is static validation,
- GitHub Actions checks are static validation,
- successful static validation must never be described as proof that Iris or Minecraft renders the shader correctly,
- visual quality cannot be claimed without genuine runtime output,
- driver-specific behavior cannot be claimed verified without genuine runtime evidence.

Iris preprocesses and transforms shader source before final GPU compilation, so generic GLSL validation is useful but not authoritative for complete Iris compatibility.

## 9. Performance Philosophy

Performance is a first-class design constraint for future rendering work.

Future feature specifications should consider:
- texture/sample count,
- resolution-dependent work,
- branching,
- bandwidth,
- temporal stability,
- render-target usage,
- memory footprint,
- lower-performance hardware,
- configurable quality levels where useful.

This workspace milestone itself contains no rendering feature implementation.

## 10. Out of Scope for Workspace Setup

The workspace setup must not yet implement:
- terrain rendering,
- deferred rendering,
- shadows,
- atmosphere,
- volumetric clouds,
- water,
- reflections,
- ambient occlusion,
- anti-aliasing,
- bloom,
- PBR,
- tonemapping,
- quality presets,
- compatibility profiles,
- GitHub Actions that pretend to validate Iris runtime behavior.

Those belong to later approved specifications and implementation plans.

## 11. Workspace Success Criteria

The workspace milestone is complete when:

1. Solar Shader is clearly isolated under `Solar-Shader/`.
2. Root and project documentation make the monorepo/project boundary obvious.
3. Superpowers specification and plan directories are established.
4. The repository contains no speculative rendering implementation.
5. Future ChatGPT sessions can immediately discover where Solar source and durable decisions belong.
6. Branch conventions are documented.
7. The workspace is ready for a separate shader-foundation architectural cycle.

## 12. External Technical References

Current Iris documentation was consulted through Context7 (`/irisshaders/docs`), including:
- Your First Shaderpack / shaderpack file structure
- `shaders.properties` overview and settings documentation
- recommended use of `shaders/lib/` for reusable GLSL includes

Primary documentation repository:
https://github.com/IrisShaders/docs

---

After this specification is approved, the next required step is a dedicated implementation plan for the workspace setup. No shader rendering implementation should begin as part of that plan.
