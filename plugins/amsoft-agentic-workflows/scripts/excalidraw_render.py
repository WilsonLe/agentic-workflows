#!/usr/bin/env python3
"""Validate and render one complete Excalidraw scene document to PNG."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from excalidraw_api import ExcalidrawAPIError, validate_scene_content

DEFAULT_RENDERER_PACKAGE = "excalidraw-export-cli@1.0.0"
DEFAULT_TIMEOUT_SECONDS = 180.0
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ExcalidrawRenderError(Exception):
    """A local render request was refused or could not be verified."""


@dataclass(frozen=True)
class RenderResult:
    """Secret-free summary of a verified render."""

    output_path: Path
    element_count: int
    file_count: int


def load_json(path: Path) -> object:
    """Read one JSON file without printing its content."""

    try:
        resolved = path.expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise ExcalidrawRenderError("the render input must be a regular file")
        return json.loads(resolved.read_text(encoding="utf-8"))
    except ExcalidrawRenderError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExcalidrawRenderError("the render input is not valid JSON") from error


def complete_scene_document(payload: object) -> dict[str, object]:
    """Extract and validate a complete scene from raw or API-helper JSON."""

    if not isinstance(payload, dict):
        raise ExcalidrawRenderError("the render input must contain a JSON object")

    candidate: object = payload
    if isinstance(payload.get("operation"), str) and isinstance(
        payload.get("result"), dict
    ):
        candidate = payload["result"]

    try:
        return validate_scene_content(candidate, partial=False)
    except ExcalidrawAPIError as error:
        raise ExcalidrawRenderError(
            f"the render input is not a complete scene document: {error}"
        ) from error


def _resolve_executable(value: str) -> str:
    resolved = shutil.which(value)
    if resolved:
        return resolved
    candidate = Path(value).expanduser().resolve(strict=False)
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return str(candidate)
    raise ExcalidrawRenderError(f"renderer executable is unavailable: {value}")


def _renderer_command(
    temporary_input: Path,
    output_path: Path,
    *,
    renderer_bin: str | None,
    renderer_package: str,
) -> list[str]:
    if renderer_bin:
        executable = _resolve_executable(renderer_bin)
        return [executable, str(temporary_input), str(output_path)]

    if not renderer_package or any(character.isspace() for character in renderer_package):
        raise ExcalidrawRenderError("renderer package must be one non-empty token")
    npx = shutil.which("npx")
    if npx is None:
        raise ExcalidrawRenderError(
            "npx is required unless --renderer-bin selects a compatible renderer"
        )
    return [npx, "--yes", renderer_package, str(temporary_input), str(output_path)]


def _failure_detail(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stderr or result.stdout or "").strip()
    if not output:
        return "no renderer diagnostic was returned"
    return output.splitlines()[-1][:500]


def render_scene(
    input_path: Path,
    output_path: Path,
    *,
    renderer_bin: str | None = None,
    renderer_package: str = DEFAULT_RENDERER_PACKAGE,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> RenderResult:
    """Validate a scene, invoke the renderer, and verify a non-empty PNG."""

    if timeout_seconds <= 0:
        raise ExcalidrawRenderError("render timeout must be greater than zero")

    resolved_input = input_path.expanduser().resolve(strict=True)
    resolved_output = output_path.expanduser().resolve(strict=False)
    if resolved_input == resolved_output:
        raise ExcalidrawRenderError("render output must not overwrite the JSON input")

    document = complete_scene_document(load_json(resolved_input))
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )

    with tempfile.TemporaryDirectory(
        prefix=".amsoft-excalidraw-render-", dir=resolved_output.parent
    ) as directory:
        temporary_input = Path(directory) / "scene.excalidraw"
        temporary_output = Path(directory) / "render.png"
        temporary_input.write_text(serialized + "\n", encoding="utf-8")
        temporary_input.chmod(0o600)
        command = _renderer_command(
            temporary_input,
            temporary_output,
            renderer_bin=renderer_bin,
            renderer_package=renderer_package,
        )
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except FileNotFoundError as error:
            raise ExcalidrawRenderError("the configured renderer could not be started") from error
        except subprocess.TimeoutExpired as error:
            raise ExcalidrawRenderError(
                f"renderer timed out after {timeout_seconds:g} seconds"
            ) from error
        if result.returncode != 0:
            raise ExcalidrawRenderError(
                f"renderer failed with exit code {result.returncode}: "
                f"{_failure_detail(result)}"
            )
        try:
            with temporary_output.open("rb") as rendered:
                signature = rendered.read(len(PNG_SIGNATURE))
                has_content = rendered.read(1) != b""
            if signature != PNG_SIGNATURE:
                raise ExcalidrawRenderError("renderer output is not a PNG file")
            if not has_content:
                raise ExcalidrawRenderError("renderer output is an empty PNG file")
        except OSError as error:
            raise ExcalidrawRenderError(
                "renderer did not produce a readable PNG"
            ) from error
        try:
            os.replace(temporary_output, resolved_output)
        except OSError as error:
            raise ExcalidrawRenderError("verified PNG could not be published") from error

    return RenderResult(
        output_path=resolved_output,
        element_count=len(document["elements"]),
        file_count=len(document["files"]),
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate and render one complete Excalidraw scene to PNG."
    )
    result.add_argument("input", type=Path, help="raw scene JSON or API-helper response")
    result.add_argument("output", type=Path, help="PNG output path")
    result.add_argument(
        "--renderer-bin",
        help="compatible renderer executable; otherwise use pinned npx package",
    )
    result.add_argument(
        "--renderer-package",
        default=os.environ.get(
            "AMSOFT_EXCALIDRAW_RENDERER_PACKAGE", DEFAULT_RENDERER_PACKAGE
        ),
        help="exact npm package spec used by npx",
    )
    result.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="renderer timeout in seconds",
    )
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        rendered = render_scene(
            arguments.input,
            arguments.output,
            renderer_bin=arguments.renderer_bin,
            renderer_package=arguments.renderer_package,
            timeout_seconds=arguments.timeout,
        )
    except (ExcalidrawRenderError, OSError) as error:
        print(f"Excalidraw render refused: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "elements": rendered.element_count,
                "files": rendered.file_count,
                "output": str(rendered.output_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
