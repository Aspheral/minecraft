# Solar Shader Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Solar Shader Foundation v0 as a compact, modular Iris shaderpack skeleton with a two-target hybrid-deferred pipeline, diagnostic views, deterministic quality/configuration interfaces, reproducible static validation, and explicitly separated runtime evidence.

**Architecture:** Thin Iris program entry points delegate to shared GLSL modules. Opaque/cutout geometry writes linear HDR scene color to `colortex0` and compact `SurfaceData` to `colortex1`; deferred/composite stages read those buffers, forward translucent programs write scene color only, and `final` performs only the minimum display transfer. Python standard-library tooling provides S0 structure checks, CPU reference math tests, include expansion, and S1 validation through pinned Khronos glslang.

**Tech Stack:** GLSL 330 compatibility, Iris shaderpack conventions, Fabric, Python 3.12 standard library, GitHub Actions on `ubuntu-24.04`, Khronos glslang 16.5.0.

**Spec:** `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-foundation-design.md`

**Plan status:** Written for user review. No implementation begins until this plan is approved and an execution method is selected.

## Global Constraints

- Repository: `Aspheral/minecraft`.
- Project root: `Solar-Shader/`.
- Implementation branch: `feat/solar-foundation`.
- Primary runtime reference: Minecraft Java 26.3 + Fabric + Iris 1.11.6 + Sodium 0.9.2.
- Secondary compatibility lane: Minecraft Java 1.21.11 + Fabric + Iris 1.10.x; concrete dated reference Iris 1.10.5 + Sodium 0.8.3.
- GLSL baseline: `#version 330 compatibility`.
- Foundation owns exactly two full-resolution color targets.
- `colortex0`: `R11F_G11F_B10F`, linear-light HDR scene/base color.
- `colortex1`: `RGB10_A2`, compact `SurfaceData`, cleared to zero each frame.
- `colortex1` logical layout: R10 oct-normal X, G10 oct-normal Y, B10 = 5-bit block light + 5-bit sky light, A2 surface class.
- Surface classes: 0 invalid/background, 1 regular opaque, 2 cutout/foliage-capable, 3 reserved.
- Opaque/cutout programs may write `colortex1`; forward translucent programs must never target or blend into it.
- Position is reconstructed from depth; no position or motion-vector render target is added.
- Base shader tree serves all dimensions; no `world0/`, `world-1/`, or `world1/`.
- Do not require `COMPUTE_SHADERS`, `SSBO`, or `CUSTOM_IMAGES`.
- Do not use `separateEntityDraws`.
- `ENTITY_TRANSLUCENT` may be declared optional to improve metadata separation; it must never be required.
- No shadow program, AO, GI, volumetrics, reflections, PBR, TAA, bloom, exposure controller, artistic tone mapper, runtime AutoTune controller, or companion code in Foundation v0.
- `TARGET_FPS` default: 120; allowed values: 30, 60, 75, 90, 120, 144, 165, 240.
- `DEBUG_VIEW` values: 0 normal, 1 normals, 2 reconstructed depth/position, 3 light metadata, 4 surface class.
- Foundation quality API returns deterministic static values; no adaptive controller is implemented.
- Static validation levels are S0 and S1. Iris runtime load/compile is I0. Rendered visual/performance evidence is I1.
- Never describe S0/S1 success as proof of Iris runtime compatibility, visual quality, or FPS.
- The connected Vercel `minecraft` project is not a shader runtime or validation environment and must not be deployed for this milestone.
- Use GitHub as canonical state. Changes should be coherent task commits on `feat/solar-foundation`.
- Because development is chat-only, GitHub Actions is the canonical executable test environment. Intentional failing test commits are allowed as TDD checkpoints and must be followed by the task implementation commit that restores Solar CI to green.

## Review Focus

1. **Include graph abuse:** absolute Solar includes must resolve only inside `Solar-Shader/shaders/`; path traversal, missing includes, and include cycles must fail S0 validation.
2. **Metadata contamination:** every program classified as translucent/color-only must be statically proven not to target `colortex1`; metadata-writing programs must disable blending on `colortex1`.
3. **Light-coordinate endpoints:** the documented Iris lightmap transform/normalization must clamp edge values into [0,1] and round-trip through the 5+5-bit codec within the defined quantization error.
4. **Reconstruction edge cases:** representative center/corner pixels and near/far depths must reconstruct within tolerance without NaN/Inf from the supplied inverse projection matrix.
5. **Optional entity translucency:** `ENTITY_TRANSLUCENT` may improve separation when available, but static validation must reject it if placed in `iris.features.required`; the base pack must remain structurally valid without a required advanced/optional capability.

---

## Planned File Map

### Repository/CI

- Create: `.github/workflows/solar-static.yml`
  - Runs Python tests, S0 validation, and S1 glslang validation for Solar-related changes only.
  - Downloads Khronos glslang 16.5.0 Linux x86_64 release tarball and verifies SHA-256 before execution.
- Modify near completion: `Solar-Shader/README.md`, `Solar-Shader/CHANGELOG.md`, `Solar-Shader/ROADMAP.md`
  - Record Foundation state without claiming I0/I1 evidence that was not actually produced.
- Create: `Solar-Shader/benchmarks/foundation-runtime-template.md`
  - Human/runtime evidence template only; no fabricated result.

### Validation/reference tooling

- Create: `Solar-Shader/tools/solar_validate.py`
  - S0 structure checks, include expansion, generic S1 invocation.
- Create: `Solar-Shader/tools/solar_reference.py`
  - CPU reference math for SurfaceData and reconstruction tests.
- Create: `Solar-Shader/tools/tests/test_solar_validate.py`
- Create: `Solar-Shader/tools/tests/test_solar_reference.py`
- Create fixture directories under `Solar-Shader/tools/tests/fixtures/` only where a test needs a real file graph.

### Shader configuration and libraries

- Create: `Solar-Shader/shaders/shaders.properties`
- Create: `Solar-Shader/shaders/lib/config.glsl`
- Create: `Solar-Shader/shaders/lib/core/buffers.glsl`
- Create: `Solar-Shader/shaders/lib/core/color.glsl`
- Create: `Solar-Shader/shaders/lib/core/space.glsl`
- Create: `Solar-Shader/shaders/lib/core/encoding.glsl`
- Create: `Solar-Shader/shaders/lib/core/compatibility.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_data.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_encode.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_decode.glsl`
- Create: `Solar-Shader/shaders/lib/quality/quality.glsl`
- Create: `Solar-Shader/shaders/lib/debug/debug_view.glsl`
- Create: `Solar-Shader/shaders/lib/programs/gbuffer_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/programs/gbuffer_fragment.glsl`
- Create: `Solar-Shader/shaders/lib/programs/fullscreen_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/programs/deferred_fragment.glsl`
- Create: `Solar-Shader/shaders/lib/programs/composite_fragment.glsl`
- Create: `Solar-Shader/shaders/lib/programs/final_fragment.glsl`

### Iris entry points

Each listed program receives one `.vsh` and one `.fsh`. These files remain thin wrappers that set a program-role macro and include the appropriate shared program module.

Metadata-capable:
- `gbuffers_textured_lit`
- `gbuffers_terrain`
- `gbuffers_terrain_solid`
- `gbuffers_terrain_cutout`
- `gbuffers_entities`
- `gbuffers_block`

Color-only / no SurfaceData target:
- `gbuffers_basic`
- `gbuffers_textured`
- `gbuffers_particles`
- `gbuffers_skybasic`
- `gbuffers_skytextured`
- `gbuffers_hand`
- `gbuffers_hand_water`
- `gbuffers_water`
- `gbuffers_weather`
- `gbuffers_entities_translucent`
- `gbuffers_block_translucent`
- `gbuffers_lightning`

Fullscreen:
- `deferred`
- `composite`
- `final`

This is 21 logical programs / 42 thin stage files. Shared behavior remains concentrated in the GLSL libraries above.

---

### Task 1: Build the Solar Validation Harness and CI Skeleton

**Files:**
- Create: `Solar-Shader/tools/solar_validate.py`
- Create: `Solar-Shader/tools/tests/test_solar_validate.py`
- Create: `Solar-Shader/tools/tests/fixtures/valid_minimal/shaders/entry.vsh`
- Create: `Solar-Shader/tools/tests/fixtures/valid_minimal/shaders/entry.fsh`
- Create: `Solar-Shader/tools/tests/fixtures/valid_minimal/shaders/lib/common.glsl`
- Create: `.github/workflows/solar-static.yml`

**Interfaces:**
- Produces Python API:
  - `Finding(code: str, path: str, message: str)`
  - `expand_shader(entry: Path, shader_root: Path) -> str`
  - `validate_structure(repo_root: Path, mode: str = "incremental") -> list[Finding]`
  - `validate_glsl(repo_root: Path, glslang_path: Path) -> list[Finding]`
  - CLI: `python Solar-Shader/tools/solar_validate.py --repo-root . --mode <incremental|complete> [--glslang PATH]`
- `incremental` validates every Solar shader/config artifact that exists without requiring the full final file set.
- `complete` additionally requires every Foundation file/program listed in this plan.
- S1 compilation expands Iris-style `#include "/lib/..."` paths to temporary source, injects validator-only definitions immediately after `#version`, and links each discovered vertex/fragment pair.
- Later tasks consume this validator unchanged except to extend final expected-file/program constants where explicitly listed.

- [ ] **Step 1: Add failing validator tests and CI test job**

Tests in `test_solar_validate.py` must initially import an absent `solar_validate` module and define these behaviors:

```python
def test_expand_shader_resolves_absolute_lib_include(): ...
def test_expand_shader_rejects_parent_traversal(): ...
def test_expand_shader_rejects_include_cycle(): ...
def test_structure_rejects_world_directories(): ...
def test_structure_rejects_required_compute_ssbo_or_custom_images(): ...
def test_structure_rejects_required_entity_translucent(): ...
def test_structure_rejects_colortex_two_or_higher(): ...
def test_structure_rejects_iris_reserved_symbols(): ...
```

CI initially runs:

```text
python -m unittest discover -s Solar-Shader/tools/tests -p "test_*.py" -v
```

Path filters:
- `Solar-Shader/**`
- `.github/workflows/solar-static.yml`

Commit this intentionally failing TDD checkpoint:

```text
test: define Solar foundation validation contract
```

- [ ] **Step 2: Verify the TDD checkpoint fails in GitHub Actions**

Inspect the workflow run for the test-only commit.

Expected:
- Solar static workflow runs.
- Unit-test job fails because `solar_validate` does not yet provide the required API.
- Vercel status, if present, is ignored as shader-validation evidence.

- [ ] **Step 3: Implement `solar_validate.py` minimally to satisfy the tests**

Required behavior:

- `Finding` is a frozen dataclass or equivalent immutable record.
- absolute shader include `/lib/x.glsl` resolves to `<shader_root>/lib/x.glsl`,
- relative/absolute include resolution may not escape `shader_root`,
- include cycles produce a finding/error rather than recursion,
- scan rejects `world0`, `world-1`, `world1`,
- parse `iris.features.required` and reject `COMPUTE_SHADERS`, `SSBO`, `CUSTOM_IMAGES`, and `ENTITY_TRANSLUCENT`,
- scan shader source for user symbols matching `iris_`, `irisMain`, or `moj_import`,
- reject any `colortexN` reference with N >= 2 in Foundation source/config,
- incremental mode does not require the final shader entrypoint list yet.

Validator-only S1 preamble, inserted after the first `#version` line:

```glsl
#define R11F_G11F_B10F 1
#define RGB10_A2 2
#define IS_IRIS 1
#define IRIS_VERSION 11106
#define IRIS_FEATURE_ENTITY_TRANSLUCENT 1
```

These values exist only to make generic validation parse Iris symbols; they are not runtime constants.

`validate_glsl` maps:
- `.vsh` -> temporary `.vert`
- `.fsh` -> temporary `.frag`

and runs glslang in link mode on each pair.

- [ ] **Step 4: Extend CI with pinned glslang 16.5.0**

Download:

```text
https://github.com/KhronosGroup/glslang/releases/download/16.5.0/glslang-16.5.0-linux-x86_64-release.tar.gz
```

Required SHA-256:

```text
b9b1f96acb898a62251b171f7695efcecfc206a530299054071919b06820f657
```

The workflow must:
1. download the archive,
2. run `sha256sum -c`,
3. extract it,
4. locate executable `glslangValidator`,
5. run unit tests,
6. run `solar_validate.py --mode incremental --glslang <path>`.

If there are no root shader program pairs yet, S1 reports a neutral "no program pairs yet" result and exits successfully.

The workflow summary must include:

```text
S0/S1 static validation only. Passing does not prove Iris runtime compatibility, visual quality, or FPS.
```

- [ ] **Step 5: Commit the implementation**

Commit:

```text
test: add Solar foundation validation harness
```

- [ ] **Step 6: Verify CI is green**

Expected:
- unit tests PASS,
- incremental S0 PASS,
- S1 PASS or explicitly skips because no program pairs exist,
- no claim of I0/I1 evidence appears.

---

### Task 2: Build CPU Reference Math for SurfaceData and Reconstruction

**Files:**
- Create: `Solar-Shader/tools/solar_reference.py`
- Create: `Solar-Shader/tools/tests/test_solar_reference.py`

**Interfaces:**
- Produces:
  - `quantize_unorm(value: float, bits: int) -> int`
  - `dequantize_unorm(code: int, bits: int) -> float`
  - `oct_encode(normal: tuple[float, float, float]) -> tuple[float, float]`
  - `oct_decode(encoded: tuple[float, float]) -> tuple[float, float, float]`
  - `pack_light_pair(block_light: float, sky_light: float) -> float`
  - `unpack_light_pair(encoded: float) -> tuple[float, float]`
  - `encode_surface_class(surface_class: int) -> float`
  - `decode_surface_class(encoded: float) -> int`
  - `normalize_lightmap_coord(raw_uv: tuple[float, float]) -> tuple[float, float]`
  - `project_view_position(position, projection) -> tuple[float, float, float]`
  - `reconstruct_view_position(screen, projection_inverse) -> tuple[float, float, float]`
- Values returned by light helpers are normalized [0,1], with X = block light and Y = sky light.

- [ ] **Step 1: Add failing reference-math tests**

Required cases:

```python
def test_oct_axes_round_trip_after_10bit_quantization(): ...
def test_oct_arbitrary_normals_keep_dot_at_least_0_9998(): ...
def test_light_pair_round_trip_error_is_at_most_half_5bit_step(): ...
def test_lightmap_normalization_maps_documented_endpoints_to_zero_and_one(): ...
def test_lightmap_normalization_clamps_outside_documented_endpoints(): ...
def test_surface_classes_zero_through_three_round_trip_exactly(): ...
def test_reconstruction_round_trips_center_near_and_far_points(): ...
def test_reconstruction_round_trips_viewport_corners(): ...
def test_reconstruction_outputs_only_finite_values_for_valid_depths(): ...
```

Lightmap normalization is fixed by current Iris documentation:

```text
normalized = raw / (30/32) - (1/32)
```

then clamped to [0,1].

The 5-bit quantization error bound is:

```text
0.5 / 31 + 1e-6
```

Use known projection + precomputed inverse fixtures; do not add NumPy.

Commit failing checkpoint:

```text
test: define Solar surface and reconstruction math
```

- [ ] **Step 2: Verify CI fails on the missing reference API**

Expected: unit-test job FAILS only in the new reference tests.

- [ ] **Step 3: Implement `solar_reference.py` using Python standard library only**

Rules:

- oct encoding/decoding operates on normalized vectors,
- test helper rejects a zero-length input normal with `ValueError`,
- emulate attachment quantization in tests with 10-bit UNORM for oct channels,
- block light occupies low five bits of the B10 integer,
- sky light occupies high five bits,
- encode B10 as `packed_integer / 1023.0`,
- decode with `round(encoded * 1023)`,
- A2 surface class uses `class / 3.0` and rounds back to [0,3],
- reconstruction maps UV/depth [0,1] to NDC [-1,1], multiplies by supplied inverse projection, and divides XYZ by W.

- [ ] **Step 4: Commit the implementation**

Commit:

```text
test: add Solar foundation reference math
```

- [ ] **Step 5: Verify CI is green**

Expected:
- all validator tests PASS,
- all reference math tests PASS,
- incremental S0 PASS,
- S1 still skips cleanly if no program pairs exist.

---

### Task 3: Establish Shader Configuration, Buffers, Compatibility, and Quality ABI

**Files:**
- Create: `Solar-Shader/shaders/shaders.properties`
- Create: `Solar-Shader/shaders/lib/config.glsl`
- Create: `Solar-Shader/shaders/lib/core/buffers.glsl`
- Create: `Solar-Shader/shaders/lib/core/color.glsl`
- Create: `Solar-Shader/shaders/lib/core/compatibility.glsl`
- Create: `Solar-Shader/shaders/lib/quality/quality.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- `config.glsl` exposes:
  - `const int TARGET_FPS = 120; // [30 60 75 90 120 144 165 240]`
  - `const int DEBUG_VIEW = 0; // [0 1 2 3 4]`
- `buffers.glsl` exposes Iris buffer directives:
  - `colortex0Format = R11F_G11F_B10F`
  - `colortex1Format = RGB10_A2`
  - both clear each frame,
  - both clear to zero.
- `color.glsl` exposes:
  - `vec3 solarToLinearApprox(vec3 encodedColor)`
  - `vec3 solarToDisplayApprox(vec3 linearColor)`
- `quality.glsl` exposes:
  - `struct SolarQuality`
  - `SolarQuality solarGetQuality()`
- `compatibility.glsl` is the sole location for Iris/version compatibility macros used by shared code.

- [ ] **Step 1: Add failing configuration-contract tests**

Add tests asserting the actual repository, once files exist, must contain:

- target FPS default and exact allowed values,
- debug view default and exact allowed values,
- no `profile.*` declarations yet,
- `iris.features.optional=ENTITY_TRANSLUCENT`,
- no `iris.features.required` advanced feature,
- no `separateEntityDraws`,
- exact buffer formats,
- exact clear booleans/colors,
- static quality API fields:
  - global,
  - atmosphere,
  - clouds,
  - shadows,
  - reflections,
  - indirectLight,
  - postProcessing.

Commit failing checkpoint:

```text
test: define Solar foundation configuration ABI
```

- [ ] **Step 2: Verify CI fails because configuration files are absent**

Expected: new configuration tests FAIL, existing tests remain green.

- [ ] **Step 3: Implement `shaders.properties`**

Exact settings surface:

```properties
iris.features.optional=ENTITY_TRANSLUCENT

screen=TARGET_FPS DEBUG_VIEW
sliders=TARGET_FPS
```

Add per-buffer blend overrides only when metadata-writing programs exist in Task 5; do not predeclare unknown behavior here.

Do not expose fake `AUTO/PERFORMANCE/BALANCED/CINEMATIC/ULTRA` profile buttons yet.

- [ ] **Step 4: Implement `config.glsl`, `buffers.glsl`, `color.glsl`, `compatibility.glsl`, and `quality.glsl`**

Color conversion uses the Iris tutorial's Foundation approximation:

```text
linear  = pow(max(encoded, 0), 2.2)
display = pow(max(linear, 0), 1/2.2)
```

This is a minimal transfer boundary, not Solar's future artistic tone mapper.

`solarGetQuality()` returns deterministic `1.0` for all seven fields.

`compatibility.glsl` may expose a compile-time Solar macro derived from `IS_IRIS`, but must contain no version branch unless current code actually needs one.

- [ ] **Step 5: Commit implementation**

Commit:

```text
feat: establish Solar foundation configuration
```

- [ ] **Step 6: Verify CI is green**

Expected:
- configuration ABI tests PASS,
- S0 incremental PASS,
- no root shader program pair yet, so S1 may still skip.

---

### Task 4: Implement the SurfaceData GLSL Codec and Space Helpers

**Files:**
- Create: `Solar-Shader/shaders/lib/core/encoding.glsl`
- Create: `Solar-Shader/shaders/lib/core/space.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_data.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_encode.glsl`
- Create: `Solar-Shader/shaders/lib/surface/surface_decode.glsl`
- Create: `Solar-Shader/shaders/lib/debug/debug_view.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- GLSL `SurfaceData`:
  - `vec3 normal`
  - `float skyLight`
  - `float blockLight`
  - `int surfaceClass`
- Produces:
  - `vec2 solarOctEncode(vec3 normal)`
  - `vec3 solarOctDecode(vec2 encoded)`
  - `float solarPackLights(float blockLight, float skyLight)`
  - `vec2 solarUnpackLights(float encoded)` returning `(blockLight, skyLight)`
  - `float solarEncodeSurfaceClass(int surfaceClass)`
  - `int solarDecodeSurfaceClass(float encoded)`
  - `vec4 solarEncodeSurface(SurfaceData surface)`
  - `SurfaceData solarDecodeSurface(vec4 packed)`
  - `vec2 solarNormalizeLightmapCoord(vec2 rawLightmapUV)`
  - `vec3 solarReconstructViewPosition(vec2 uv, float depth, mat4 projectionInverse)`
  - debug helpers used later by composite/deferred.

- [ ] **Step 1: Add failing source-contract tests**

Tests assert:

- SurfaceData field names/types exist exactly,
- logical packing is only referenced inside `surface_encode.glsl` / `surface_decode.glsl`,
- no consumer outside codec files directly names `colortex1.r/g/b/a`,
- light normalization constants `30.0 / 32.0` and `1.0 / 32.0` live in one helper,
- no `inverse()` call is used in shader source; Iris supplies inverse matrices,
- no `colortex2+` reference appears.

Commit failing checkpoint:

```text
test: define Solar SurfaceData shader contract
```

- [ ] **Step 2: Verify CI fails on absent codec files**

Expected: source-contract tests FAIL only for missing/new interfaces.

- [ ] **Step 3: Implement codec and space helpers to match Task 2 reference math**

Rules:

- GLSL oct codec matches the Python reference equations,
- encode normal safely normalizes input and uses +Y fallback only if squared length is effectively zero to avoid NaN,
- B10 light packing matches block-low / sky-high 5-bit layout,
- surface class clamps to [0,3],
- reconstructed view position uses provided `gbufferProjectionInverse`,
- helpers never allocate or reference another color target.

- [ ] **Step 4: Implement `debug_view.glsl` helpers**

Expose:

```glsl
vec3 solarDebugNormal(SurfaceData surface);
vec3 solarDebugPosition(vec3 viewPosition, float farPlane);
vec3 solarDebugLight(SurfaceData surface);
vec3 solarDebugSurfaceClass(SurfaceData surface);
```

Surface-class palette is diagnostic and fixed:
- 0 -> black,
- 1 -> white,
- 2 -> green,
- 3 -> magenta.

- [ ] **Step 5: Commit implementation**

Commit:

```text
feat: add Solar SurfaceData codec and space helpers
```

- [ ] **Step 6: Verify CI is green**

Expected:
- Python reference tests remain green,
- source-contract tests PASS,
- S0 incremental PASS.

---

### Task 5: Implement Shared G-Buffer Programs and Opaque/Cutout Entry Points

**Files:**
- Create: `Solar-Shader/shaders/lib/programs/gbuffer_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/programs/gbuffer_fragment.glsl`
- Create pairs:
  - `Solar-Shader/shaders/gbuffers_textured_lit.vsh/.fsh`
  - `Solar-Shader/shaders/gbuffers_terrain.vsh/.fsh`
  - `Solar-Shader/shaders/gbuffers_terrain_solid.vsh/.fsh`
  - `Solar-Shader/shaders/gbuffers_terrain_cutout.vsh/.fsh`
  - `Solar-Shader/shaders/gbuffers_entities.vsh/.fsh`
  - `Solar-Shader/shaders/gbuffers_block.vsh/.fsh`
- Modify: `Solar-Shader/shaders/shaders.properties`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Each wrapper:
  1. starts with `#version 330 compatibility`,
  2. defines exactly one `SOLAR_PROGRAM_*` role,
  3. includes the shared program module.
- Shared vertex outputs:
  - texture coordinate,
  - normalized light coordinates,
  - vertex/biome color,
  - view-space normal.
- Shared fragment writes:
  - location 0 -> linear scene color,
  - location 1 -> encoded SurfaceData.
- Metadata writer `RENDERTARGETS`: `0,1`.

- [ ] **Step 1: Add failing opaque-program tests**

Tests require all six program pairs and assert:

- wrappers stay at or below 12 non-comment/non-empty lines,
- each wrapper defines one program role,
- metadata fragments contain or expand to `/* RENDERTARGETS: 0,1 */`,
- `gbuffers_terrain_cutout` maps to surface class 2,
- the other five map to surface class 1,
- `shaders.properties` contains `blend.<program>.colortex1=off` for all six metadata programs,
- scene-color code does not multiply sampled albedo by `lightmap`,
- alpha test occurs before color/metadata output,
- color is converted to linear before writing `colortex0`.

Commit failing checkpoint:

```text
test: define Solar opaque G-buffer programs
```

- [ ] **Step 2: Verify CI fails on missing entry points**

Expected: opaque-program tests FAIL; other tests stay green.

- [ ] **Step 3: Implement shared vertex path**

Use current Iris compatibility-profile inputs:

- `ftransform()`,
- `gl_TextureMatrix[0] * gl_MultiTexCoord0` for atlas UV,
- `gl_TextureMatrix[1] * gl_MultiTexCoord1` for lightmap UV,
- `gl_Color`,
- `gl_NormalMatrix * gl_Normal`.

Normalize light coordinates with `solarNormalizeLightmapCoord`.

- [ ] **Step 4: Implement shared opaque fragment path**

Use:

- `uniform sampler2D gtexture`,
- `uniform float alphaTestRef = 0.1`,
- `texture(gtexture, texcoord) * glcolor`,
- discard when source alpha < `alphaTestRef`,
- convert RGB to linear with `solarToLinearApprox`,
- write alpha 1.0 to scene output,
- encode view normal + normalized block/sky light + program-selected surface class into `colortex1`.

Do not multiply by Minecraft's `lightmap` sampler. Foundation stores light information for later use instead.

- [ ] **Step 5: Add per-buffer blend rules**

For exactly the six metadata programs:

```properties
blend.<program>.colortex1=off
```

No global blend override.

- [ ] **Step 6: Commit implementation**

Commit:

```text
feat: add Solar opaque G-buffer foundation
```

- [ ] **Step 7: Verify CI is green including first real S1 programs**

Expected:
- unit/source tests PASS,
- incremental S0 PASS,
- glslang S1 compiles and links all six vertex/fragment pairs,
- workflow still labels result static-only.

---

### Task 6: Implement Fullscreen Deferred, Debug Composite, and Final Display Transfer

**Files:**
- Create: `Solar-Shader/shaders/lib/programs/fullscreen_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/programs/deferred_fragment.glsl`
- Create: `Solar-Shader/shaders/lib/programs/composite_fragment.glsl`
- Create: `Solar-Shader/shaders/lib/programs/final_fragment.glsl`
- Create pairs:
  - `Solar-Shader/shaders/deferred.vsh/.fsh`
  - `Solar-Shader/shaders/composite.vsh/.fsh`
  - `Solar-Shader/shaders/final.vsh/.fsh`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Fullscreen vertex outputs `texcoord`.
- `deferred` samples `colortex0` and passes linear HDR scene color through unchanged.
- `composite` samples:
  - `colortex0`,
  - `colortex1`,
  - `depthtex1`,
  - uniforms `gbufferProjectionInverse`, `far`.
- `composite` applies DEBUG_VIEW:
  - 0 scene,
  - 1 decoded normal,
  - 2 reconstructed position/depth diagnostic,
  - 3 block/sky-light diagnostic,
  - 4 surface-class diagnostic.
- `final` samples linear `colortex0` and applies only `solarToDisplayApprox`.

- [ ] **Step 1: Add failing fullscreen-pipeline tests**

Tests assert:

- all three program pairs exist,
- deferred/composite `RENDERTARGETS` is only 0,
- neither deferred nor composite writes `colortex1`,
- composite declares/uses `depthtex1`, not `depthtex0`, for opaque reconstruction,
- composite uses `gbufferProjectionInverse`,
- source contains no GPU `inverse()`,
- all five debug values route to distinct branches,
- final uses `solarToDisplayApprox`,
- final does not implement exposure, filmic, Reinhard, ACES, bloom, or color grading.

Commit failing checkpoint:

```text
test: define Solar fullscreen foundation pipeline
```

- [ ] **Step 2: Verify CI fails on missing fullscreen programs**

Expected: new tests FAIL only for absent fullscreen implementation.

- [ ] **Step 3: Implement shared fullscreen vertex and deferred pass**

Deferred fragment must be neutral:

```text
linear colortex0 input -> linear colortex0 output
```

No lighting, tone mapping, history, or adaptation.

- [ ] **Step 4: Implement composite debug selection**

Rules:

- decode `SurfaceData` from `colortex1`,
- class 0/background renders black in metadata debug modes,
- DEBUG_VIEW 2 reconstructs view position from `depthtex1` and displays a stable grayscale distance normalized by `far`,
- normal debug displays `normal * 0.5 + 0.5`,
- light debug displays block light in red and sky light in green,
- class debug uses Task 4 palette,
- DEBUG_VIEW 0 returns scene color unchanged.

- [ ] **Step 5: Implement final display transfer**

Final fragment:
- samples `colortex0`,
- applies approximate 1/2.2 display transfer,
- keeps alpha 1.0,
- performs no artistic tone mapping.

- [ ] **Step 6: Commit implementation**

Commit:

```text
feat: add Solar deferred diagnostics and final output
```

- [ ] **Step 7: Verify CI is green**

Expected:
- fullscreen tests PASS,
- all existing S0 tests PASS,
- glslang links opaque + deferred + composite + final pairs.

---

### Task 7: Implement Sky, Color-Only, and Forward-Translucent Coverage

**Files:**
- Create pairs:
  - `gbuffers_basic.vsh/.fsh`
  - `gbuffers_textured.vsh/.fsh`
  - `gbuffers_particles.vsh/.fsh`
  - `gbuffers_skybasic.vsh/.fsh`
  - `gbuffers_skytextured.vsh/.fsh`
  - `gbuffers_hand.vsh/.fsh`
  - `gbuffers_hand_water.vsh/.fsh`
  - `gbuffers_water.vsh/.fsh`
  - `gbuffers_weather.vsh/.fsh`
  - `gbuffers_entities_translucent.vsh/.fsh`
  - `gbuffers_block_translucent.vsh/.fsh`
  - `gbuffers_lightning.vsh/.fsh`
- Modify: `Solar-Shader/shaders/lib/programs/gbuffer_vertex.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/gbuffer_fragment.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Color-only G-buffer fragments target only `colortex0`.
- Sky/basic paths may omit normals/light where geometry semantics do not supply meaningful values.
- Textured color-only paths preserve source alpha for forward blending.
- No file in this task writes or names `colortex1` except shared-library code behind compile-time metadata roles.

- [ ] **Step 1: Add failing color-only/translucency tests**

Tests require all 12 pairs and assert:

- each fragment role expands to `/* RENDERTARGETS: 0 */`,
- none of these role macros selects metadata writing,
- no per-buffer `colortex1` blend rule exists for these programs,
- `ENTITY_TRANSLUCENT` remains optional only,
- `separateEntityDraws` remains absent,
- `gbuffers_particles` and `gbuffers_lightning` are color-only so they cannot contaminate metadata,
- sky programs are color-only,
- water/weather/hand-water/translucent-entity/translucent-block programs preserve alpha for blending.

Commit failing checkpoint:

```text
test: define Solar color-only and translucency coverage
```

- [ ] **Step 2: Verify CI fails on missing color-only programs**

Expected: new tests FAIL, prior program pairs continue to pass S1.

- [ ] **Step 3: Extend shared vertex/fragment modules with explicit role families**

Role families:

```text
SOLAR_ROLE_BASIC_COLOR
SOLAR_ROLE_TEXTURED_COLOR
SOLAR_ROLE_METADATA_REGULAR
SOLAR_ROLE_METADATA_CUTOUT
SOLAR_ROLE_SKY_BASIC
SOLAR_ROLE_SKY_TEXTURED
SOLAR_ROLE_TRANSLUCENT_TEXTURED
```

A root wrapper maps one Iris program to one family.

Do not duplicate full shader bodies per entrypoint.

- [ ] **Step 4: Implement color-only behavior**

- basic color: vertex color -> linear RGB, source alpha,
- textured color: texture * vertex color -> alpha test when applicable -> linear RGB,
- sky basic: vertex sky color -> linear RGB, alpha 1,
- sky textured: texture * vertex color -> linear RGB with source alpha,
- translucent textured: texture * vertex color -> linear RGB while preserving alpha.

No Foundation color-only path samples `lightmap` to produce final lighting.

- [ ] **Step 5: Commit implementation**

Commit:

```text
feat: complete Solar foundation program coverage
```

- [ ] **Step 6: Verify CI is green**

Expected:
- all program ownership tests PASS,
- S0 incremental PASS,
- S1 glslang compiles/links all 21 program pairs.

---

### Task 8: Promote S0 to Complete Mode and Lock Reproducible CI

**Files:**
- Modify: `Solar-Shader/tools/solar_validate.py`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`
- Modify: `.github/workflows/solar-static.yml`

**Interfaces:**
- `validate_structure(..., mode="complete")` now enforces the exact Foundation file/program manifest from Planned File Map.
- Workflow switches from incremental to complete mode.
- CI remains S0/S1 only.

- [ ] **Step 1: Add failing complete-manifest tests**

Required tests:

```python
def test_complete_mode_requires_every_foundation_program_pair(): ...
def test_complete_mode_requires_core_library_manifest(): ...
def test_complete_mode_requires_shaders_properties(): ...
def test_complete_mode_proves_translucent_roles_do_not_target_colortex1(): ...
def test_complete_mode_proves_metadata_roles_have_blend_off_for_colortex1(): ...
def test_complete_mode_allows_only_colortex0_and_colortex1(): ...
```

Commit failing checkpoint:

```text
test: define complete Solar foundation manifest
```

- [ ] **Step 2: Verify CI fails until complete mode is implemented**

Expected: test job FAILS on missing complete-manifest behavior, while incremental validation itself still reports green.

- [ ] **Step 3: Implement complete manifest and switch CI to complete mode**

Workflow command becomes equivalent to:

```text
python Solar-Shader/tools/solar_validate.py --repo-root . --mode complete --glslang "$GLSLANG_BIN"
```

Require all 21 stage pairs and all shared libraries listed in this plan.

- [ ] **Step 4: Verify workflow summaries label evidence correctly**

Workflow summary must record:
- S0 PASS/FAIL,
- S1 PASS/FAIL,
- exact glslang version,
- explicit statement that I0/I1 were not performed.

- [ ] **Step 5: Commit implementation**

Commit:

```text
ci: enforce complete Solar foundation static validation
```

- [ ] **Step 6: Verify branch CI is green**

Expected:
- Python tests PASS,
- complete S0 PASS,
- S1 PASS for all 21 program pairs,
- Vercel checks are not cited as Solar evidence.

---

### Task 9: Add Runtime Evidence Template and Reconcile Durable Project Status

**Files:**
- Create: `Solar-Shader/benchmarks/foundation-runtime-template.md`
- Modify: `Solar-Shader/README.md`
- Modify: `Solar-Shader/CHANGELOG.md`
- Modify: `Solar-Shader/ROADMAP.md`

**Interfaces:**
- Documentation distinguishes:
  - implemented/static-validated Foundation,
  - pending/recorded I0 runtime evidence,
  - pending/recorded I1 performance/visual evidence.
- Runtime template is a data-entry artifact, not benchmark output.

- [ ] **Step 1: Add documentation assertions to validator tests**

Tests require:
- README links Foundation spec and plan,
- README states S0/S1 do not prove Iris runtime,
- changelog records Foundation implementation only after Tasks 1-8 are green,
- roadmap no longer says the workspace is pending integration into main,
- runtime template contains all required fields below and contains no fabricated values.

Commit failing checkpoint:

```text
test: define Solar foundation evidence documentation
```

- [ ] **Step 2: Verify CI fails on stale/missing documentation**

Expected: documentation assertions FAIL.

- [ ] **Step 3: Create runtime template**

Required fields:

```text
Date
Commit SHA
Evidence level (I0 or I1)
Shaderpack discovered by Iris
Shaderpack enable result
Solar/Iris compile error result
Compile/debug log reference
Minecraft version
Fabric Loader version
Iris version
Sodium version
GPU
GPU driver
CPU
RAM
OS
Resolution
Render distance
FPS cap
VSync
Monitor refresh where known
Solar TARGET_FPS
Solar DEBUG_VIEW
Scene / seed / coordinates / camera description
Shader reload result
Overworld result
Nether result
End result
Terrain result
Entity result
Block-entity result
Sky result
Hand result
Water/translucency result
Weather result
Dimension-switching result
Average FPS (I1 only)
1% low FPS (I1 only)
GPU frame time where measurable
CPU frame time where measurable
Notes / screenshots / logs
```

Blank fields are acceptable. Invented values are not.

- [ ] **Step 4: Update README, CHANGELOG, and ROADMAP truthfully**

README:
- current state: Foundation source implemented and S0/S1 validated if CI is green,
- runtime status: pending unless real evidence was actually supplied during execution,
- primary/secondary compatibility references,
- link Foundation spec + plan.

CHANGELOG:
- record two-buffer architecture,
- shared GLSL modules,
- static validation/CI,
- debug views,
- no claim of cinematic feature completion or 120 FPS.

ROADMAP:
- correct Milestone 0 to integrated/complete on `main`,
- mark Milestone 1 source/static validation complete on branch when true,
- state I0/I1 separately,
- keep later rendering systems unimplemented.

- [ ] **Step 5: Commit documentation**

Commit:

```text
docs: record Solar foundation validation status
```

- [ ] **Step 6: Verify CI remains green**

Expected: complete S0/S1 and documentation tests PASS.

---

### Task 10: Whole-Branch Verification and Review Handoff

**Files:**
- Verify only unless a defect is found.
- Any fix must be narrowly scoped, tested, and committed before repeating this task.

**Interfaces:**
- Consumes every task output.
- Produces a review-ready Foundation branch; does not merge it.

- [ ] **Step 1: Compare `feat/solar-foundation` against `main`**

Verify:
- only approved Solar work + `.github/workflows/solar-static.yml` changed,
- no Vercel configuration/deployment files were added,
- no shadow/volumetric/reflection/PBR/TAA/AutoTune implementation slipped into scope,
- no `worldN` directories exist,
- no `colortex2+` use exists.

- [ ] **Step 2: Re-read the Foundation spec and map every Definition-of-Done item to branch evidence**

Produce an internal checklist for all 18 Definition-of-Done requirements.

Expected:
- items requiring S0/S1 have concrete CI evidence,
- I0/I1 are marked either recorded or pending,
- no runtime-only item is inferred from static checks.

- [ ] **Step 3: Inspect latest Solar workflow**

Use GitHub workflow/status tools.

Expected:
- unit tests PASS,
- S0 complete PASS,
- S1 PASS,
- glslang reports version 16.5.0,
- static-only disclaimer is present.

- [ ] **Step 4: Perform source review**

Review at minimum:
- SurfaceData packing parity between Python reference and GLSL,
- block/sky light bit order,
- cutout class assignment,
- linear/display transfer placement,
- metadata blend disable rules,
- translucent target ownership,
- include boundaries,
- root wrapper thinness,
- no duplicate configuration definitions,
- no runtime quality adaptation.

- [ ] **Step 5: If any defect is found, add a failing regression test first**

Commit test-only checkpoint, verify failure, implement fix, verify green, then return to Step 1.

- [ ] **Step 6: Record review-ready status**

Do not merge automatically.

At this point the branch is ready for:
1. fresh whole-branch review,
2. optional real Minecraft I0/I1 evidence if available,
3. PR creation/integration only after the implementation execution workflow authorizes those steps.

---

## Execution Notes

### Chat-only TDD

This repository is being developed without assuming a local IDE or Minecraft installation. During execution:

- use GitHub for all canonical file writes and commits,
- use GitHub Actions as the executable test environment,
- create intentional test-only red commits where the plan requires TDD proof,
- inspect the resulting workflow failure,
- then commit the implementation and require green CI before moving to the next task,
- never ask the user to copy files into a local repository to make progress.

### Static GLSL Validation Boundary

Khronos glslang 16.5.0 is generic GLSL evidence only. The CI preprocessor expands Solar includes and supplies validator-only definitions for Iris-specific symbolic constants/macros. This makes S1 useful without pretending to reproduce Iris' `glsl-transformer`.

Iris itself remains required for I0.

### Vercel Boundary

The connected Vercel project `minecraft` may continue to emit an unrelated repository status because of existing Git integration. That status is not Solar shader evidence.

Do not:
- deploy Solar to Vercel,
- use Vercel build success as S0/S1/I0/I1 proof,
- add web tooling during this plan.

### Runtime Validation

If genuine Minecraft runtime evidence becomes available during execution, record it using the runtime template and classify it I0/I1.

If it does not, completion wording is:

```text
Foundation source and static validation complete. Iris/Minecraft runtime validation pending.
```

not:

```text
Solar Foundation works in Iris.
```
