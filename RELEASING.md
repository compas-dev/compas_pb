# Releasing

Releases are prepared and approved through pull requests. Do not create a
release by running `invoke release` or by pushing a tag locally.

## Prepare a release

1. Keep user-facing changes in the `Unreleased` section of `CHANGELOG.md` as
   normal pull requests are merged.
2. Open **Actions → prepare release → Run workflow**.
3. Select `patch`, `minor`, or `major`.
4. Review the generated `release/vX.Y.Z` pull request. Edit the changelog in
   that branch if the release notes need additional work.
5. Merge the pull request using merge, squash, or rebase. The merge strategy
   does not affect the release.

The merge to `main` validates the version and changelog, runs the full build,
publishes to PyPI with trusted publishing, creates the version tag and GitHub
release, and deploys the versioned documentation.

## Repository setup

PyPI's trusted publisher must match this repository, the
`.github/workflows/release.yml` workflow, and the `pypi` environment.

The preparation workflow uses the repository's standard `GITHUB_TOKEN`. In
**Settings → Actions → General → Workflow permissions**, enable **Allow GitHub
Actions to create and approve pull requests**. GitHub holds checks from the
automatically created release pull request for manual approval; a maintainer
with write access must select **Approve workflows to run** before it can be
merged.
