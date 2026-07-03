import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


def outputs_exist(base_dir: Path, relative_paths: Sequence[str]) -> bool:
    return all((base_dir / rel_path).exists() for rel_path in relative_paths)


def run_scripts(base_dir: Path, script_names: Iterable[str], reason: str) -> None:
    scripts_dir = base_dir / "scripts"
    workspace_root = base_dir.parent
    for script_name in script_names:
        script_path = scripts_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"未找到 post-refresh 脚本: {script_path}")
        print(f"[post-refresh] {reason}: {script_name}")
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(workspace_root),
            check=True,
        )
