# `onelogg` PyPI Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish version `0.1.1` to PyPI as distribution `onelogg` while preserving `from onelog import get_logger`.

**Architecture:** Keep the existing single-module setuptools package and change only its distribution identity and version. Add a release-triggered GitHub Actions pipeline with separate build and OIDC publishing jobs, then validate the published artifact from a clean environment.

**Tech Stack:** Python 3.8+, setuptools, pytest, build, Twine, GitHub Actions, PyPI Trusted Publishing

## Global Constraints

- The PyPI distribution name is exactly `onelogg`.
- The import module remains exactly `onelog` and setuptools keeps `py-modules = ["onelog"]`.
- The release version is exactly `0.1.1`; do not move or replace tag `v0.1.0`.
- The only runtime dependency remains `rich>=13,<15`.
- The repository is `BottiCelle/onelog`, the PyPI environment is `pypi`, and the publishing workflow filename is `publish.yml`.
- Publication must use GitHub OIDC Trusted Publishing without a stored PyPI password or API token.

---

## File map

- `pyproject.toml`: authoritative distribution metadata and setuptools module mapping.
- `onelog.py`: importable module and runtime `__version__` value.
- `test_distribution.py`: wheel identity, metadata, and contents regression tests.
- `test_fatal.py`: public package version and logger behavior tests.
- `README.md`: Chinese installation and distribution-name documentation.
- `README_en.md`: English installation and distribution-name documentation.
- `.github/dependabot.yml`: weekly GitHub Actions dependency updates.
- `.github/workflows/publish.yml`: release build, artifact transfer, and OIDC publication.

### Task 1: Change the distribution identity and version test-first

**Files:**
- Modify: `test_distribution.py`
- Modify: `test_fatal.py`
- Modify: `pyproject.toml`
- Modify: `onelog.py`

**Interfaces:**
- Consumes: setuptools `[project]` metadata and `py-modules = ["onelog"]`.
- Produces: wheel distribution `onelogg==0.1.1`, import module `onelog`, and `onelog.__version__ == "0.1.1"`.

- [ ] **Step 1: Update the wheel test to express the new identity**

Replace the existing distribution test in `test_distribution.py` with:

```python
def test_wheel_uses_onelogg_distribution_identity(tmp_path: Path) -> None:
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
    wheel = next(tmp_path.glob("onelogg-0.1.1-*.whl"))
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_path = next(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_path))

    assert metadata["Name"] == "onelogg"
    assert metadata["Version"] == "0.1.1"
    assert metadata["Author"] == "BottiCelle"
    assert "onelog.py" in names
    assert set(metadata.get_all("Project-URL")) == {
        "Homepage, https://github.com/BottiCelle/onelog",
        "Repository, https://github.com/BottiCelle/onelog",
        "Issues, https://github.com/BottiCelle/onelog/issues",
    }
```

Change the version assertion in `test_fatal.py` to:

```python
assert onelog.__version__ == "0.1.1"
```

Final-review regression hardening: the exact `Project-URL` set assertion above
was added after the metadata implementation was already correct. Its focused
characterization run passed against the current implementation; no artificial
RED result was created for that assertion.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python -m pytest test_distribution.py test_fatal.py::test_package_exposes_version_and_logger -v
```

Expected: FAIL because no `onelogg-0.1.1-*.whl` exists and the module still reports `0.1.0`.

- [ ] **Step 3: Make the minimal metadata and module changes**

In `pyproject.toml`, set:

```toml
[project]
name = "onelogg"
version = "0.1.1"
```

Leave this mapping unchanged:

```toml
[tool.setuptools]
py-modules = ["onelog"]
```

In `onelog.py`, set:

```python
__version__ = "0.1.1"
```

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```bash
python -m pytest test_distribution.py test_fatal.py::test_package_exposes_version_and_logger -v
```

Expected: both tests PASS.

- [ ] **Step 5: Run the complete test suite**

Run:

```bash
python -m pytest -v
```

Expected: all tests PASS with no warnings or errors.

- [ ] **Step 6: Commit the package identity change**

```bash
git add pyproject.toml onelog.py test_distribution.py test_fatal.py
git commit -m "chore: rename PyPI distribution to onelogg"
```

### Task 2: Document and automate the release

**Files:**
- Modify: `README.md`
- Modify: `README_en.md`
- Create: `.github/dependabot.yml`
- Create: `.github/workflows/publish.yml`

**Interfaces:**
- Consumes: `onelogg==0.1.1` metadata from Task 1.
- Produces: public installation instructions and a release-triggered OIDC publisher that uploads the contents of `dist/`.

- [ ] **Step 1: Update both README files**

In both `README.md` and `README_en.md`, replace the local-install-only primary example with:

```bash
python3 -m pip install onelogg
```

Describe version `0.1.1`, distribution name `onelogg`, and import name `onelog`.
Preserve the existing GitHub installation alternative but update its tag to
`v0.1.1`; preserve the existing usage examples.

- [ ] **Step 2: Create the publishing workflow**

Create `.github/workflows/publish.yml` with:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions: {}

jobs:
  build:
    name: Build and verify distributions
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Check out repository
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7

      - name: Set up Python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7
        with:
          python-version: "3.13"

      - name: Install build and test tools
        run: python -m pip install --upgrade build twine ".[test]"

      - name: Run tests
        run: python -m pytest -v

      - name: Build wheel and source distribution
        run: python -m build

      - name: Validate distribution metadata
        run: python -m twine check dist/*

      - name: Store distributions
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7
        with:
          name: python-package-distributions
          path: dist/

  publish:
    name: Publish distributions to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/onelogg
    permissions:
      id-token: write
    steps:
      - name: Download distributions
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish distributions to PyPI
        uses: pypa/gh-action-pypi-publish@dc37677b2e1c63e2034f94d8a5b11f265b73ba33 # release/v1
```

- [ ] **Step 3: Configure GitHub Actions dependency updates**

Create `.github/dependabot.yml` with:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

Dependabot update pull requests must retain full commit-SHA pins in the
publishing workflow, with readable version comments alongside them.

- [ ] **Step 4: Run the complete suite**

Run:

```bash
python -m pytest -v
```

Expected: all tests PASS with no warnings or errors.

- [ ] **Step 5: Inspect the human-facing docs and workflow configuration**

Run:

```bash
rg -n "botticelle-onelog|version is `0\.1\.0`|版本为 `0\.1\.0`" README.md README_en.md pyproject.toml test_distribution.py
sed -n '1,220p' .github/workflows/publish.yml
sed -n '1,120p' .github/dependabot.yml
git diff --check
```

Expected: `rg` returns no matches, the workflow visibly matches the exact
configuration in Step 2 without a password, and `git diff --check` succeeds.
The real release run in Task 4 is the authoritative workflow behavior test;
human prose and YAML source text do not receive brittle string-assertion tests.

- [ ] **Step 6: Commit documentation and automation**

```bash
git add README.md README_en.md .github/dependabot.yml .github/workflows/publish.yml
git commit -m "ci: publish onelogg releases to PyPI"
```

### Task 3: Build and install the exact release artifacts locally

**Files:**
- Verify only; no source changes expected.

**Interfaces:**
- Consumes: source tree at version `0.1.1` from Tasks 1 and 2.
- Produces: validated wheel and source distribution in a temporary directory, plus proof that the wheel imports as `onelog`.

- [ ] **Step 1: Install release tooling in an isolated virtual environment**

```bash
release_env=$(mktemp -d)
python -m venv "$release_env/venv"
"$release_env/venv/bin/python" -m pip install --upgrade pip build twine
```

Expected: the environment is created and build tooling installs successfully.

- [ ] **Step 2: Build wheel and source distribution**

```bash
"$release_env/venv/bin/python" -m build --outdir "$release_env/dist" .
ls -1 "$release_env/dist"
```

Expected files:

```text
onelogg-0.1.1-py3-none-any.whl
onelogg-0.1.1.tar.gz
```

- [ ] **Step 3: Validate artifact metadata**

```bash
"$release_env/venv/bin/python" -m twine check "$release_env"/dist/*
"$release_env/venv/bin/python" -m zipfile -l "$release_env/dist/onelogg-0.1.1-py3-none-any.whl"
```

Expected: Twine reports `PASSED` for both artifacts and the wheel listing contains `onelog.py`.

- [ ] **Step 4: Install only the built wheel and smoke-test the public import**

```bash
install_env=$(mktemp -d)
python -m venv "$install_env/venv"
"$install_env/venv/bin/python" -m pip install "$release_env/dist/onelogg-0.1.1-py3-none-any.whl"
(cd /tmp && "$install_env/venv/bin/python" -c 'import sys; from pathlib import Path; from onelog import get_logger; import onelog; assert Path(sys.prefix).resolve() in Path(onelog.__file__).resolve().parents; assert onelog.__version__ == "0.1.1"; assert callable(get_logger)')
```

Expected: installation and import command both exit successfully, and the
resolved `onelog` module path is inside the isolated environment's
`sys.prefix`, proving the checkout did not satisfy the import.

- [ ] **Step 5: Confirm the worktree is release-ready**

```bash
git status --short --branch
git log --oneline origin/main..HEAD
```

Expected: no uncommitted changes and the intended design, identity, and workflow commits are ahead of `origin/main`.

### Task 4: Configure Trusted Publishing and publish `v0.1.1`

**Files:**
- External state: PyPI pending publisher, GitHub `pypi` environment, `main` branch, tag and release `v0.1.1`, Actions run, and PyPI project `onelogg`.

**Interfaces:**
- Consumes: verified commits and artifacts from Tasks 1–3.
- Produces: public PyPI release `onelogg==0.1.1` installable with import module `onelog`.

- [ ] **Step 1: Recheck that the target PyPI project does not exist**

```bash
python - <<'PY'
from urllib.error import HTTPError
from urllib.request import urlopen

try:
    urlopen("https://pypi.org/pypi/onelogg/json")
except HTTPError as exc:
    assert exc.code == 404, exc
else:
    raise SystemExit("onelogg already exists on PyPI; inspect ownership before publishing")
PY
```

Expected: command exits successfully after observing HTTP 404. If the project now exists, stop and verify ownership instead of publishing.

- [ ] **Step 2: Configure the pending PyPI Trusted Publisher**

Using the authenticated PyPI account, open the pending publisher form and enter exactly:

```text
PyPI project name: onelogg
Owner: BottiCelle
Repository: onelog
Workflow filename: publish.yml
Environment name: pypi
```

Expected: PyPI confirms the pending publisher configuration. Do not create or paste an API token.

- [ ] **Step 3: Create the GitHub deployment environment**

```bash
gh api --method PUT repos/BottiCelle/onelog/environments/pypi
```

Expected: the response identifies environment `pypi`.

- [ ] **Step 4: Run final local verification and push the reviewed commits**

```bash
python -m pytest -v
git status --short --branch
git push origin main
```

Expected: tests pass, the worktree is clean, and `main` pushes successfully.

- [ ] **Step 5: Create the immutable release tag and GitHub Release**

```bash
gh release create v0.1.1 --repo BottiCelle/onelog --target main --title "v0.1.1" --notes "Publish the package to PyPI as onelogg while preserving the onelog import name."
```

Expected: GitHub creates tag and release `v0.1.1`; do not reuse or move `v0.1.0`.

- [ ] **Step 6: Watch the publishing workflow to completion**

```bash
git fetch origin tag v0.1.1
release_sha=$(git rev-parse 'v0.1.1^{commit}')
run_id=
for attempt in $(seq 1 30); do
  run_id=$(gh run list --repo BottiCelle/onelog --workflow publish.yml --event release --limit 50 --json databaseId,headSha --jq "map(select(.headSha == \"$release_sha\"))[0].databaseId // empty")
  if test -n "$run_id"; then
    break
  fi
  if test "$attempt" -eq 30; then
    echo "No release-event publish.yml run found for $release_sha after 30 attempts" >&2
    exit 1
  fi
  sleep 10
done
gh run watch "$run_id" --repo BottiCelle/onelog --exit-status
```

Expected: the command resolves the commit behind `v0.1.1`, finds the
release-event `publish.yml` run whose `headSha` is that exact commit within five
minutes, and watches that run's database ID until both build and publish jobs
complete successfully. If no matching run appears or a job fails, stop, inspect
the run state or logs, and use the CI-debugging workflow before changing or
rerunning anything.

- [ ] **Step 7: Verify the public PyPI release and clean installation**

```bash
published_env=$(mktemp -d)
python -m venv "$published_env/venv"
"$published_env/venv/bin/python" -m pip install --no-cache-dir "onelogg==0.1.1"
(cd /tmp && "$published_env/venv/bin/python" -c 'import sys; from pathlib import Path; from onelog import get_logger; import onelog; assert Path(sys.prefix).resolve() in Path(onelog.__file__).resolve().parents; assert onelog.__version__ == "0.1.1"; assert callable(get_logger)')
"$published_env/venv/bin/python" -m pip show onelogg
```

Expected: PyPI installation succeeds, the import smoke test resolves `onelog`
from inside the isolated environment's `sys.prefix`, and `pip show` reports
`Name: onelogg` and `Version: 0.1.1`.

- [ ] **Step 8: Audit the final external state**

```bash
gh release view v0.1.1 --repo BottiCelle/onelog --json tagName,isDraft,isPrerelease,url
gh run list --repo BottiCelle/onelog --workflow publish.yml --event release --limit 1 --json conclusion,status,url
python - <<'PY'
import json
from urllib.request import urlopen

data = json.load(urlopen("https://pypi.org/pypi/onelogg/0.1.1/json"))
assert data["info"]["name"] == "onelogg"
assert data["info"]["version"] == "0.1.1"
assert {item["packagetype"] for item in data["urls"]} == {"bdist_wheel", "sdist"}
print("PyPI completion audit passed")
PY
```

Expected: the release is neither draft nor prerelease, the latest publishing run succeeded, and PyPI exposes both wheel and source distribution for `onelogg==0.1.1`.
