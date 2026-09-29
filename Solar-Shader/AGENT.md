# Solar Shader Agent Instructions

This file is the durable handoff for future ChatGPT sessions working on Solar Shader.

## Canonical State

GitHub is the source of truth.

Before changing Solar Shader:

1. inspect the current repository files,
2. read the relevant approved specification,
3. read the relevant implementation plan,
4. inspect recent commits on the active branch,
5. verify current external documentation when behavior may be version-sensitive.

Conversation memory must never override the current repository state.

## Project Boundary

Solar-specific work stays under `Solar-Shader/` except for intentionally shared monorepo files such as the root `README.md`.

Do not implement Solar work directly on `main` without explicit user approval. Use focused feature branches for substantial work.

## Development Workflow

For substantial architectural work, use Superpowers:

```text
brainstorm → approve design → commit spec → approve spec → write plan → approve execution → implement → verify → review → integrate
```

Use Context7 for current Iris, Sodium, shaderpack, rendering-library, and other version-sensitive documentation instead of guessing from training knowledge.

Use GitHub as the persistent project workspace and for commits, branches, PRs, CI status, and repository inspection.

A Vercel project named `minecraft` is available to the Aspheral team for future web-facing tooling, benchmark viewers, docs utilities, or related infrastructure when a later approved plan requires it. Do not treat Vercel as the runtime for the Minecraft shaderpack itself.

## Performance and AutoTune Contract

Solar's mainstream design baseline is 120 FPS at 1080p under defined benchmark conditions.

Target FPS is part of the quality budget:

- 60 FPS = 16.67 ms total frame interval,
- 120 FPS = 8.33 ms,
- 240 FPS = 4.17 ms.

Lower intentional FPS targets unlock more visual-quality budget. They are not automatically evidence of poor performance.

For uncapped play or configured caps above 120 FPS, Solar's default Auto behavior should target the 120 FPS cinematic-performance point unless the user explicitly selects a higher target.

Never infer the user's configured FPS cap from Iris `frameTime` alone.

The optional Solar AutoTune companion may later use richer hardware/configuration information where verified APIs support it, but the shaderpack must remain useful without the companion.

## Quality Contract

Solar should maximize perceived cinematic quality within the selected frame-time budget while protecting a minimum visual-quality floor.

Do not solve performance problems by silently removing the visual systems that define Solar's identity.

Every major rendering feature should have an understood approximate performance cost.

## Evidence Rules

Never claim:

- a shader renders correctly in Iris because generic GLSL validation passed,
- visual quality is good without genuine rendered output,
- a target FPS is achieved without real in-game measurement,
- driver-specific behavior works without relevant runtime evidence.

Static validation is static validation. Label it accurately.

## Tool-Use Rule

Do not ask the user to perform work that an available connected tool can perform.

When external state matters, inspect the authoritative connected source first.
