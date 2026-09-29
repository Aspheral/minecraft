from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

from solar_validate import expand_shader, validate_structure


class SolarValidateTests(unittest.TestCase):
    def _repo(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def test_expand_shader_resolves_absolute_lib_include(self):
        root = Path(__file__).parent / "fixtures" / "valid_minimal" / "shaders"
        expanded = expand_shader(root / "entry.vsh", root)
        self.assertIn("SOLAR_COMMON_FIXTURE", expanded)

    def test_expand_shader_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "shaders"
            root.mkdir()
            entry = root / "entry.vsh"
            entry.write_text('#version 330 compatibility\n#include "../outside.glsl"\n', encoding="utf-8")
            (Path(td) / "outside.glsl").write_text("const int BAD = 1;\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                expand_shader(entry, root)

    def test_expand_shader_rejects_include_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "shaders"
            (root / "lib").mkdir(parents=True)
            entry = root / "entry.vsh"
            a = root / "lib" / "a.glsl"
            b = root / "lib" / "b.glsl"
            entry.write_text('#version 330 compatibility\n#include "/lib/a.glsl"\n', encoding="utf-8")
            a.write_text('#include "/lib/b.glsl"\n', encoding="utf-8")
            b.write_text('#include "/lib/a.glsl"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                expand_shader(entry, root)

    def test_structure_rejects_world_directories(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "Solar-Shader" / "shaders" / "world0").mkdir(parents=True)
            findings = validate_structure(repo)
            self.assertTrue(any(f.code == "WORLD_DIR" for f in findings))

    def test_structure_rejects_required_compute_ssbo_or_custom_images(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text(
                "iris.features.required=COMPUTE_SHADERS SSBO CUSTOM_IMAGES\n",
                encoding="utf-8",
            )
            findings = validate_structure(repo)
            self.assertTrue(any(f.code == "REQUIRED_ADVANCED_FEATURE" for f in findings))

    def test_structure_rejects_required_entity_translucent(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text(
                "iris.features.required=ENTITY_TRANSLUCENT\n",
                encoding="utf-8",
            )
            findings = validate_structure(repo)
            self.assertTrue(any(f.code == "REQUIRED_ENTITY_TRANSLUCENT" for f in findings))

    def test_structure_rejects_colortex_two_or_higher(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "bad.fsh").write_text(
                "#version 330 compatibility\nuniform sampler2D colortex2;\n",
                encoding="utf-8",
            )
            findings = validate_structure(repo)
            self.assertTrue(any(f.code == "COLORTEX_RANGE" for f in findings))

    def test_structure_rejects_iris_reserved_symbols(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "bad.glsl").write_text(
                "float iris_bad_name = 0.0;\n",
                encoding="utf-8",
            )
            findings = validate_structure(repo)
            self.assertTrue(any(f.code == "IRIS_RESERVED_SYMBOL" for f in findings))
    def test_foundation_configuration_contract(self):
        repo = self._repo()
        shaders = repo / "Solar-Shader" / "shaders"
        props = (shaders / "shaders.properties").read_text(encoding="utf-8")
        config = (shaders / "lib" / "config.glsl").read_text(encoding="utf-8")
        buffers = (shaders / "lib" / "core" / "buffers.glsl").read_text(encoding="utf-8")
        quality = (shaders / "lib" / "quality" / "quality.glsl").read_text(encoding="utf-8")

        self.assertIn("#define TARGET_FPS 120 // [30 60 75 90 120 144 165 240]", config)
        self.assertIn("#define DEBUG_VIEW 0 // [0 1 2 3 4]", config)
        self.assertNotIn("profile.", props)
        self.assertIn("iris.features.optional=ENTITY_TRANSLUCENT", props)
        self.assertNotIn("iris.features.required=", props)
        self.assertNotIn("separateEntityDraws", props)

        self.assertIn("const int colortex0Format = R11F_G11F_B10F;", buffers)
        self.assertIn("const int colortex1Format = RGB10_A2;", buffers)
        self.assertIn("const bool colortex0Clear = true;", buffers)
        self.assertIn("const bool colortex1Clear = true;", buffers)
        self.assertIn("const vec4 colortex0ClearColor = vec4(0.0);", buffers)
        self.assertIn("const vec4 colortex1ClearColor = vec4(0.0);", buffers)

        for field in (
            "global",
            "atmosphere",
            "clouds",
            "shadows",
            "reflections",
            "indirectLight",
            "postProcessing",
        ):
            self.assertIn(f"float {field};", quality)
        self.assertIn("SolarQuality solarGetQuality()", quality)
    def test_surface_shader_contract(self):
        repo = self._repo()
        shaders = repo / "Solar-Shader" / "shaders"
        surface = (shaders / "lib" / "surface" / "surface_data.glsl").read_text(encoding="utf-8")
        encode = (shaders / "lib" / "surface" / "surface_encode.glsl").read_text(encoding="utf-8")
        decode = (shaders / "lib" / "surface" / "surface_decode.glsl").read_text(encoding="utf-8")
        space = (shaders / "lib" / "core" / "space.glsl").read_text(encoding="utf-8")

        for declaration in (
            "vec3 normal;",
            "float skyLight;",
            "float blockLight;",
            "int surfaceClass;",
        ):
            self.assertIn(declaration, surface)

        self.assertIn("30.0 / 32.0", space)
        self.assertIn("1.0 / 32.0", space)
        self.assertIn("solarEncodeSurface", encode)
        self.assertIn("solarDecodeSurface", decode)

        all_shader_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in shaders.rglob("*")
            if path.is_file() and path.suffix in {".glsl", ".vsh", ".fsh"}
        )
        self.assertNotIn("inverse(", all_shader_text)
        self.assertNotRegex(all_shader_text, r"\bcolortex(?:[2-9]|[12][0-9]|3[01])\b")

        for path in shaders.rglob("*"):
            if not path.is_file() or path.suffix not in {".glsl", ".vsh", ".fsh"}:
                continue
            if path.name in {"surface_encode.glsl", "surface_decode.glsl"}:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"colortex1\s*\.[rgba]")
    def test_opaque_program_contract(self):
        repo = self._repo()
        shaders = repo / "Solar-Shader" / "shaders"
        props = (shaders / "shaders.properties").read_text(encoding="utf-8")
        metadata_programs = [
            "gbuffers_textured_lit",
            "gbuffers_terrain",
            "gbuffers_terrain_solid",
            "gbuffers_terrain_cutout",
            "gbuffers_entities",
            "gbuffers_block",
        ]

        for program in metadata_programs:
            vsh = shaders / f"{program}.vsh"
            fsh = shaders / f"{program}.fsh"
            self.assertTrue(vsh.is_file(), program)
            self.assertTrue(fsh.is_file(), program)

            for wrapper in (vsh, fsh):
                lines = [
                    line.strip()
                    for line in wrapper.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.strip().startswith("//")
                ]
                self.assertLessEqual(len(lines), 12)
                roles = [line for line in lines if line.startswith("#define SOLAR_PROGRAM_")]
                self.assertEqual(len(roles), 1)

            expanded = expand_shader(fsh, shaders)
            self.assertIn("/* RENDERTARGETS: 0,1 */", expanded)
            self.assertIn("solarToLinearApprox", expanded)
            self.assertIn("solarEncodeSurface", expanded)
            self.assertIn("alphaTestRef", expanded)
            self.assertNotIn("texture(lightmap", expanded)

            rule = f"blend.{program}.colortex1=off"
            self.assertIn(rule, props)

        cutout_text = (shaders / "gbuffers_terrain_cutout.fsh").read_text(encoding="utf-8")
        self.assertIn("#define SOLAR_PROGRAM_TERRAIN_CUTOUT", cutout_text)
        shared = (shaders / "lib" / "programs" / "gbuffer_fragment.glsl").read_text(encoding="utf-8")
        self.assertIn("#ifdef SOLAR_PROGRAM_TERRAIN_CUTOUT", shared)
        self.assertIn("surface.surfaceClass = 2;", shared)
        self.assertIn("surface.surfaceClass = 1;", shared)
        self.assertLess(shared.index("discard;"), shared.index("sceneColor ="))
    def test_fullscreen_pipeline_contract(self):
        repo = self._repo()
        shaders = repo / "Solar-Shader" / "shaders"

        for program in ("deferred", "composite", "final"):
            self.assertTrue((shaders / f"{program}.vsh").is_file(), program)
            self.assertTrue((shaders / f"{program}.fsh").is_file(), program)

        deferred = expand_shader(shaders / "deferred.fsh", shaders)
        composite = expand_shader(shaders / "composite.fsh", shaders)
        final = expand_shader(shaders / "final.fsh", shaders)

        self.assertIn("/* RENDERTARGETS: 0 */", deferred)
        self.assertIn("/* RENDERTARGETS: 0 */", composite)
        self.assertNotIn("RENDERTARGETS: 0,1", deferred)
        self.assertNotIn("RENDERTARGETS: 0,1", composite)

        self.assertIn("uniform sampler2D depthtex1;", composite)
        self.assertNotIn("uniform sampler2D depthtex0;", composite)
        self.assertIn("uniform mat4 gbufferProjectionInverse;", composite)
        self.assertNotIn("inverse(", composite)

        for value in range(5):
            self.assertIn(f"#if DEBUG_VIEW == {value}", composite)

        self.assertIn("solarToDisplayApprox", final)
        for forbidden in ("ACES", "Reinhard", "filmic", "bloom", "exposure", "color grading"):
            self.assertNotIn(forbidden, final.lower() if forbidden.islower() else final)
    def test_color_only_and_translucency_contract(self):
        repo = self._repo()
        shaders = repo / "Solar-Shader" / "shaders"
        props = (shaders / "shaders.properties").read_text(encoding="utf-8")
        programs = [
            "gbuffers_basic",
            "gbuffers_textured",
            "gbuffers_particles",
            "gbuffers_skybasic",
            "gbuffers_skytextured",
            "gbuffers_hand",
            "gbuffers_hand_water",
            "gbuffers_water",
            "gbuffers_weather",
            "gbuffers_entities_translucent",
            "gbuffers_block_translucent",
            "gbuffers_lightning",
        ]
        alpha_preserving = {
            "gbuffers_hand_water",
            "gbuffers_water",
            "gbuffers_weather",
            "gbuffers_entities_translucent",
            "gbuffers_block_translucent",
        }

        self.assertIn("iris.features.optional=ENTITY_TRANSLUCENT", props)
        self.assertNotIn("iris.features.required=ENTITY_TRANSLUCENT", props)
        self.assertNotIn("separateEntityDraws", props)

        for program in programs:
            vsh = shaders / f"{program}.vsh"
            fsh = shaders / f"{program}.fsh"
            self.assertTrue(vsh.is_file(), program)
            self.assertTrue(fsh.is_file(), program)

            source = fsh.read_text(encoding="utf-8")
            self.assertIn("/* RENDERTARGETS: 0 */", source)
            self.assertNotIn("RENDERTARGETS: 0,1", source)
            self.assertNotIn("colortex1", source)
            self.assertNotIn(f"blend.{program}.colortex1=off", props)

            expanded = expand_shader(fsh, shaders)
            if program in alpha_preserving:
                self.assertIn("sourceColor.a", expanded)

        for program in ("gbuffers_particles", "gbuffers_lightning", "gbuffers_skybasic", "gbuffers_skytextured"):
            source = (shaders / f"{program}.fsh").read_text(encoding="utf-8")
            self.assertNotIn("SOLAR_PROGRAM_TERRAIN", source)
            self.assertNotIn("SOLAR_PROGRAM_ENTITIES\n", source)
            self.assertNotIn("SOLAR_PROGRAM_BLOCK\n", source)
    def test_complete_mode_requires_every_foundation_program_pair(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text("", encoding="utf-8")
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(
                f.code == "MISSING_FOUNDATION_FILE" and f.path.endswith("gbuffers_terrain.vsh")
                for f in findings
            ))

    def test_complete_mode_requires_core_library_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text("", encoding="utf-8")
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(
                f.code == "MISSING_FOUNDATION_FILE" and f.path.endswith("lib/core/buffers.glsl")
                for f in findings
            ))

    def test_complete_mode_requires_shaders_properties(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "Solar-Shader" / "shaders").mkdir(parents=True)
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(
                f.code == "MISSING_FOUNDATION_FILE" and f.path.endswith("shaders.properties")
                for f in findings
            ))

    def test_complete_mode_proves_translucent_roles_do_not_target_colortex1(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text("", encoding="utf-8")
            (shaders / "gbuffers_water.fsh").write_text(
                '#version 330 compatibility\n/* RENDERTARGETS: 0,1 */\n',
                encoding="utf-8",
            )
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(f.code == "COLOR_ONLY_METADATA_TARGET" for f in findings))

    def test_complete_mode_proves_metadata_roles_have_blend_off_for_colortex1(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "shaders.properties").write_text("", encoding="utf-8")
            (shaders / "gbuffers_terrain.fsh").write_text(
                '#version 330 compatibility\n/* RENDERTARGETS: 0,1 */\n',
                encoding="utf-8",
            )
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(f.code == "MISSING_METADATA_BLEND_RULE" for f in findings))

    def test_complete_mode_allows_only_colortex_zero_and_one(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shaders = repo / "Solar-Shader" / "shaders"
            shaders.mkdir(parents=True)
            (shaders / "bad.fsh").write_text(
                "#version 330 compatibility\nuniform sampler2D colortex7;\n",
                encoding="utf-8",
            )
            findings = validate_structure(repo, mode="complete")
            self.assertTrue(any(f.code == "COLORTEX_RANGE" for f in findings))


if __name__ == "__main__":
    unittest.main()
