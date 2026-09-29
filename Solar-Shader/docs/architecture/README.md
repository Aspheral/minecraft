# Solar Shader Architecture

This directory stores durable architectural decisions for Solar Shader.

The current authoritative foundation is the [Solar Shader Workspace and Performance Architecture](../superpowers/specs/2026-09-29-solar-workspace-design.md).

## Principles

- Performance is a first-class architectural constraint, not a cleanup pass.
- Solar targets a cinematic visual identity with strong temporal stability and gameplay readability.
- AutoTune must protect a minimum cinematic quality floor instead of reducing quality without bound.
- Major rendering systems require their own design/specification cycle before implementation.
- Version-sensitive assumptions about Iris, Sodium, OpenGL, or related tooling must be verified against current documentation before implementation.

Future architecture documents may cover shader foundation, lighting and shadows, atmosphere and clouds, materials and water, temporal reconstruction, adaptive performance, and the optional Solar AutoTune companion.

This workspace milestone establishes boundaries only. It does not implement those rendering systems.
