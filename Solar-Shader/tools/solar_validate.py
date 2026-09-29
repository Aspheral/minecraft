from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

INCLUDE_RE = re.compile(r'^\s*#include\s+"([^"]+)"\s*$')
COLORTEX_RE = re.compile(r'\bcolortex(\d+)\b')
IRIS_RESERVED_RE = re.compile(r'\b(?:iris_[A-Za-z0-9_]*|irisMain[A-Za-z0-9_]*|moj_import[A-Za-z0-9_]*)\b')
FORBIDDEN_REQUIRED_FEATURES = {"COMPUTE_SHADERS", "SSBO", "CUSTOM_IMAGES"}
WORLD_DIRS = {"world0", "world-1", "world1"}

VALIDATOR_PREAMBLE = """#define R11F_G11F_B10F 1
#define RGB10_A2 2
#define IS_IRIS 1
#define IRIS_VERSION 11106
#define IRIS_FEATURE_ENTITY_TRANSLUCENT 1
"""


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _resolve_include(current: Path, include_path: str, shader_root: Path) -> Path:
    if include_path.startswith("/"):
        target = shader_root / include_path.lstrip("/")
    else:
        target = current.parent / include_path
    target = target.resolve()
    if not _inside(shader_root, target):
        raise ValueError(f"include escapes shader root: {include_path}")
    return target


def expand_shader(entry: Path, shader_root: Path) -> str:
    shader_root = shader_root.resolve()
    entry = entry.resolve()
    if not _inside(shader_root, entry):
        raise ValueError(f"entry escapes shader root: {entry}")

    def visit(path: Path, stack: tuple[Path, ...]) -> str:
        if path in stack:
            cycle = " -> ".join(p.name for p in (*stack, path))
            raise ValueError(f"include cycle: {cycle}")
        if not path.is_file():
            raise FileNotFoundError(path)
        out: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            match = INCLUDE_RE.match(line)
            if match:
                child = _resolve_include(path, match.group(1), shader_root)
                out.append(visit(child, (*stack, path)))
            else:
                out.append(line)
        return "\n".join(out) + "\n"

    return visit(entry, ())


def _scan_required_features(properties: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not properties.is_file():
        return findings
    for raw in properties.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("iris.features.required"):
            continue
        _, _, rhs = line.partition("=")
        features = set(rhs.split())
        for feature in sorted(features & FORBIDDEN_REQUIRED_FEATURES):
            findings.append(Finding(
                "REQUIRED_ADVANCED_FEATURE",
                str(properties),
                f"{feature} must not be required by Foundation v0",
            ))
        if "ENTITY_TRANSLUCENT" in features:
            findings.append(Finding(
                "REQUIRED_ENTITY_TRANSLUCENT",
                str(properties),
                "ENTITY_TRANSLUCENT may be optional but must not be required",
            ))
    return findings


def validate_structure(repo_root: Path, mode: str = "incremental") -> list[Finding]:
    if mode not in {"incremental", "complete"}:
        raise ValueError(f"unknown validation mode: {mode}")

    repo_root = repo_root.resolve()
    shaders = repo_root / "Solar-Shader" / "shaders"
    findings: list[Finding] = []
    if not shaders.exists():
        return findings

    for name in WORLD_DIRS:
        path = shaders / name
        if path.exists():
            findings.append(Finding("WORLD_DIR", str(path), f"{name} is forbidden in Foundation v0"))

    findings.extend(_scan_required_features(shaders / "shaders.properties"))

    for path in shaders.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".vsh", ".fsh", ".glsl", ".properties"}:
            continue
        text = path.read_text(encoding="utf-8")
        for match in COLORTEX_RE.finditer(text):
            index = int(match.group(1))
            if index >= 2:
                findings.append(Finding(
                    "COLORTEX_RANGE",
                    str(path),
                    f"Foundation v0 may not reference colortex{index}",
                ))
        for match in IRIS_RESERVED_RE.finditer(text):
            findings.append(Finding(
                "IRIS_RESERVED_SYMBOL",
                str(path),
                f"Solar symbol collides with Iris-reserved pattern: {match.group(0)}",
            ))

    return findings


def _inject_preamble(source: str) -> str:
    lines = source.splitlines()
    if not lines or not lines[0].lstrip().startswith("#version"):
        raise ValueError("shader source must start with #version")
    return "\n".join([lines[0], VALIDATOR_PREAMBLE.rstrip(), *lines[1:]]) + "\n"


def validate_glsl(repo_root: Path, glslang_path: Path) -> list[Finding]:
    repo_root = repo_root.resolve()
    shader_root = repo_root / "Solar-Shader" / "shaders"
    if not shader_root.exists():
        return []

    pairs: list[tuple[Path, Path]] = []
    for vertex in sorted(shader_root.glob("*.vsh")):
        fragment = vertex.with_suffix(".fsh")
        if fragment.is_file():
            pairs.append((vertex, fragment))

    if not pairs:
        print("S1: no program pairs yet")
        return []

    findings: list[Finding] = []
    with tempfile.TemporaryDirectory(prefix="solar-glsl-") as td:
        temp_root = Path(td)
        for vertex, fragment in pairs:
            try:
                vsrc = _inject_preamble(expand_shader(vertex, shader_root))
                fsrc = _inject_preamble(expand_shader(fragment, shader_root))
            except (ValueError, FileNotFoundError) as exc:
                findings.append(Finding("S1_PREPROCESS", str(vertex), str(exc)))
                continue

            vtmp = temp_root / f"{vertex.stem}.vert"
            ftmp = temp_root / f"{fragment.stem}.frag"
            vtmp.write_text(vsrc, encoding="utf-8")
            ftmp.write_text(fsrc, encoding="utf-8")
            proc = subprocess.run(
                [str(glslang_path), "-l", str(vtmp), str(ftmp)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if proc.returncode != 0:
                findings.append(Finding(
                    "S1_GLSL",
                    vertex.stem,
                    proc.stdout.strip() or f"glslang exited {proc.returncode}",
                ))
    return findings


def _print_findings(label: str, findings: list[Finding]) -> bool:
    if not findings:
        print(f"{label}: PASS")
        return True
    print(f"{label}: FAIL ({len(findings)} finding(s))")
    for finding in findings:
        print(f"[{finding.code}] {finding.path}: {finding.message}")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solar Foundation static validator")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--mode", choices=("incremental", "complete"), default="incremental")
    parser.add_argument("--glslang", type=Path)
    args = parser.parse_args(argv)

    s0 = validate_structure(args.repo_root, args.mode)
    ok = _print_findings("S0", s0)

    if args.glslang:
        if not args.glslang.is_file():
            print(f"S1: FAIL glslangValidator not found: {args.glslang}")
            return 1
        s1 = validate_glsl(args.repo_root, args.glslang)
        ok = _print_findings("S1", s1) and ok
    else:
        print("S1: SKIP (no --glslang supplied)")

    print("Static validation only. Passing does not prove Iris runtime compatibility, visual quality, or FPS.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
