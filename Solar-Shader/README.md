# Solar Shader

Solar Shader is a Minecraft shader project focused on **extremely cinematic visuals, high temporal stability, and unusually strong real-time performance**.

The project is being designed so visual quality scales intelligently with the machine and the player's intended frame-rate target instead of forcing every system into the same preset.

## Performance Target

The mainstream design baseline is **at least 120 FPS during normal gameplay at 1080p under defined benchmark conditions**, using a contemporary mainstream gaming-PC class as the reference rather than an enthusiast-only machine.

At 120 FPS, the nominal total frame interval is 8.33 ms. Solar does not assume the shader owns that entire interval because Minecraft, CPU work, other mods, drivers, and frame-pacing reserve all consume time too.

Lower intentional frame-rate targets unlock larger visual budgets. For example, a player intentionally targeting 60 FPS has a 16.67 ms total frame interval, so AutoTune should be able to spend more time on higher-quality clouds, shadows, reflections, indirect lighting, atmosphere, and related effects than the same machine targeting 120 FPS.

## AutoTune

Solar is planned around a hybrid adaptive-quality architecture:

1. **Shader-native adaptation** uses runtime information available to the shader, such as frame timing, screen dimensions, and render distance, to fine-tune scalable work.
2. **Static profiles and controls** provide predictable quality envelopes such as Auto, Performance, Balanced, Cinematic, and Ultra.
3. **Optional Solar AutoTune companion** may later provide richer hardware/configuration awareness, including intended FPS cap and presentation behavior where supported.

The shaderpack must remain useful without the companion.

AutoTune must protect a minimum cinematic quality floor. If a target cannot be maintained without destroying Solar's intended visual identity, quality should stop degrading rather than turning the shader into a radically different product.

## Current Status

Solar is currently in the **workspace/scaffolding architecture stage**. No rendering pipeline is implemented by this milestone.

The authoritative workspace and performance specification is:

- [Solar Shader Workspace and Performance Architecture](docs/superpowers/specs/2026-09-29-solar-workspace-design.md)

The approved implementation plan is:

- [Solar Shader Workspace Implementation Plan](docs/superpowers/plans/2026-09-29-solar-workspace.md)

## Validation

ChatGPT-only development does not guarantee access to a live Minecraft + Iris runtime.

Static source inspection, generic GLSL checks, CI, and documentation verification are useful engineering evidence, but they **do not prove**:

- that Minecraft/Iris renders a shader correctly,
- that the visual result is good,
- that a specific GPU reaches a stated FPS,
- or that driver-specific behavior works.

Runtime visual and performance claims require genuine in-game evidence.
