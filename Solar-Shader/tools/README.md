# Solar Shader Tools

This directory is reserved for development, validation, benchmark, and analysis tooling that later approved implementation plans actually require.

Do not add tools simply to make the repository look mature.

## Validation Boundary

Generic GLSL compilers, linters, source scanners, CI checks, and generated reports can be useful static evidence, but they do **not** prove that Iris will preprocess and render Solar correctly inside Minecraft.

No tool may present a static check as proof of:

- visual quality,
- real in-game FPS,
- Iris runtime compatibility,
- driver-specific behavior.

## Vercel

A Vercel project named `minecraft` is connected to the Aspheral team and is available for future web-facing Solar tooling, documentation, benchmark viewers, or related utilities when an approved plan calls for them.

Vercel is **not** the runtime for the Minecraft shaderpack itself. This workspace milestone does not deploy anything to Vercel.

Current project identifier observed during workspace execution:

```text
prj_GnhC9DJ8ceyqtszem3M44JfxUyor
```

Future work should re-check live Vercel project state rather than assuming this README is current.
