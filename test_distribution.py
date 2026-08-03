import subprocess
import sys
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def test_wheel_uses_the_botticelle_distribution_identity(tmp_path: Path) -> None:
    project_root = Path(__file__).parent
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(project_root),
            "--no-build-isolation",
            "--no-deps",
            "--wheel-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    wheel = next(tmp_path.glob("botticelle_onelog-*.whl"))
    with ZipFile(wheel) as archive:
        metadata_path = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_path))

    assert metadata["Name"] == "botticelle-onelog"
    assert metadata["Author"] == "BottiCelle"
    assert any(
        value.endswith("https://github.com/BottiCelle/onelog")
        for value in metadata.get_all("Project-URL")
    )
