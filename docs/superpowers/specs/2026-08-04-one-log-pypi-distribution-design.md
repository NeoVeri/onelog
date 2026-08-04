# `one-log` PyPI Distribution Design

## Goal

Publish the project on PyPI under the distribution name `one-log` while
preserving `onelog` as its Python import name:

```bash
pip install one-log
```

```python
from onelog import get_logger
```

## Package identity and version

- Change `[project].name` in `pyproject.toml` from `botticelle-onelog` to
  `one-log`.
- Keep the setuptools module declaration as `py-modules = ["onelog"]`; the
  installed module and public Python API do not change.
- Release version `0.1.1`. The repository already has an immutable `v0.1.0`
  tag, so the release must use a new version and tag.

## Documentation

Update the Chinese and English README files so their installation examples use
`pip install one-log`, their distribution-name descriptions say `one-log`, and
their import examples continue to use `onelog`.

## Tests and verification

Update the distribution test before changing the package metadata. The test
must initially fail because the existing wheel is named for
`botticelle-onelog`, then pass after the metadata change. It will assert that:

- the wheel filename is normalized as `one_log-0.1.1-*.whl`;
- wheel metadata contains `Name: one-log` and `Version: 0.1.1`;
- the author and project URLs remain unchanged; and
- the wheel contains `onelog.py`.

Run the complete test suite, build both wheel and source distribution, and run
Twine metadata checks. Install the built wheel into a clean virtual environment
and execute an import smoke test using `from onelog import get_logger`.

## Publishing

Add a GitHub Actions workflow that publishes on a GitHub Release event. The job
will use PyPI Trusted Publishing with GitHub OIDC (`id-token: write`) and the
PyPI publish action, so the repository does not store a long-lived API token.
The workflow will run tests, build artifacts once, validate them, and publish
those exact artifacts.

Configure a pending Trusted Publisher for project `one-log` on PyPI using the
repository `BottiCelle/onelog` and the committed workflow filename. After the
implementation is merged to the default branch, create and push tag `v0.1.1`
and create the corresponding GitHub Release to trigger publication.

## Completion criteria

The work is complete only when the release workflow succeeds, PyPI reports
`one-log` version `0.1.1`, a clean environment can run
`pip install one-log==0.1.1`, and importing `get_logger` from `onelog` succeeds.
