# Solar AutoTune Companion

Solar AutoTune is a reserved location for an **optional future companion** that can provide richer calibration and configuration awareness than a shaderpack alone can reliably obtain.

The companion is not required for Solar Shader to function. The shaderpack must remain useful with standalone profiles, controls, and shader-native adaptation.

## Intended Responsibilities

Where supported by verified APIs, a future companion may use:

- hardware capability information,
- display resolution,
- Minecraft render distance,
- configured FPS cap,
- VSync behavior,
- monitor refresh behavior,
- measured runtime performance,
- other relevant configuration or telemetry.

Its purpose is to select a better initial quality envelope and distinguish **intentional frame-rate limits** from actual rendering overload.

For example, a game intentionally capped at 60 FPS naturally presents a roughly 16.67 ms frame cadence. That must not be interpreted as evidence that Solar is too expensive merely because the 120 FPS baseline uses an 8.33 ms interval.

## Integration Rule

No companion-to-Iris or companion-to-Sodium API is assumed here.

Before implementation, a dedicated architectural cycle must verify the current supported Iris/Sodium integration surface and choose an implementation path from real documentation. Do not invent APIs, hooks, configuration channels, or capabilities.

## Current Status

Boundary only. No Solar AutoTune companion code is implemented by the workspace milestone.
