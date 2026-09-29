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


if __name__ == "__main__":
    unittest.main()
