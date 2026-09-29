# Solar Shader Benchmarking

Solar Shader performance claims must be tied to repeatable test conditions. Average FPS alone is not enough; frame pacing and 1% lows matter.

## Reference Profiles

### Mainstream 1080p

- Resolution: 1920×1080
- Render distance: 12–16 chunks for the primary baseline
- Intended hardware class: contemporary mainstream gaming PC
- Primary Solar design baseline: 120 FPS

### Upper-Mainstream 1440p

- Resolution: 2560×1440
- Render distance: recorded with every result
- Intended purpose: measure scaling beyond the primary 1080p target

Reference hardware classes should be refreshed periodically rather than permanently tied to one GPU model.

## Target-FPS Budget

The nominal total frame interval is:

```text
budget_ms = 1000 / target_fps
```

Examples:

| Target FPS | Total frame interval |
| ---: | ---: |
| 30 | 33.33 ms |
| 60 | 16.67 ms |
| 75 | 13.33 ms |
| 90 | 11.11 ms |
| 120 | 8.33 ms |
| 144 | 6.94 ms |
| 165 | 6.06 ms |
| 240 | 4.17 ms |

These are **total-frame budgets**, not the amount Solar is free to consume. Minecraft CPU/GPU work, other mods, drivers, synchronization, and frame-pacing reserve require headroom.

An intentional lower FPS cap is not a performance failure. A user targeting 60 FPS has more visual-quality budget available than the same system targeting 120 FPS, so AutoTune should spend that headroom on higher-quality rendering where stable.

For uncapped play or caps above 120 FPS, the default cinematic-performance target remains 120 FPS unless the user explicitly selects a higher target.

## Required Benchmark Scenes

Benchmark coverage should eventually include:

- dense forest,
- open plains,
- mountains,
- large bodies of water,
- villages,
- caves,
- Nether,
- End,
- sunrise,
- midday,
- sunset,
- night,
- rain,
- thunderstorms,
- heavy foliage,
- long render distances.

## Record With Every Runtime Result

Where measurable, record:

- average FPS,
- 1% low FPS,
- GPU frame time,
- CPU frame time,
- major rendering-pass timings,
- render resolution,
- render distance,
- shader profile,
- AutoTune state,
- selected target FPS,
- configured game FPS cap where known,
- VSync state where known,
- monitor refresh rate where known,
- Minecraft version,
- Iris version,
- Sodium version where applicable,
- GPU,
- CPU,
- relevant modpack context.

## Evidence Rules

A static source check, generic GLSL compile, CI job, or synthetic test is not measured Minecraft performance.

Do not publish or record a number as in-game FPS unless it came from a genuine runtime benchmark with the relevant conditions attached. Static and synthetic results must be labeled as such.
