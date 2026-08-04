import subprocess
import sys
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def test_wheel_uses_one_log_distribution_identity(tmp_path: Path) -> None:
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
    wheel = next(tmp_path.glob("one_log-0.1.1-*.whl"))
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_path = next(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_path))

    assert metadata["Name"] == "one-log"
    assert metadata["Version"] == "0.1.1"
    assert metadata["Author"] == "BottiCelle"
    assert "onelog.py" in names
    assert set(metadata.get_all("Project-URL")) == {
        "Homepage, https://github.com/BottiCelle/onelog",
        "Repository, https://github.com/BottiCelle/onelog",
        "Issues, https://github.com/BottiCelle/onelog/issues",
    }
