# `pre-commit` hook to check branch names

This project implements a [pre-commit] [hook] to enforce branch names.
The defaults aim at respecting [conventional branches][cb],
but options are flexible enough to respect other conventions or set of rules.

The official [hooks][official] already contain a `no-commit-to-branch` hook,
but it expresses an inverted logic and can be cumbersome to [use].
This project is more flexible through the use of regular expressions controlling which branch names should be allowed,
and which branch names should be denied.

  [pre-commit]: https://pre-commit.com/
  [hook]: ./.pre-commit-hooks.yaml
  [cb]: https://conventional-branch.github.io/
  [official]: https://github.com/pre-commit/pre-commit-hooks
  [use]: https://github.com/pre-commit/pre-commit/issues/1034

## Usage

Add the following to your `.pre-commit-config.yaml` file.
The default is to respect [conventional branches][cb].
You might want to check the latest [release] of the repository and change the `rev` key.

```yaml
  - repo: https://github.com/efrecon/pre-commit-hook-branch-check
    rev: v0.2.0
    hooks:
      - id: branch-check
```

  [release]: https://github.com/efrecon/pre-commit-branch-check/releases

To adapt to other conventions, you can use the `--allow` and `--deny` arguments.
Each argument's value is a regular expression.
`--allow` and `--deny` can be repeated as many times as possible.
The name of a branch **must** match at least one of the regular expressions from the `--allow` arguments.
The name of a branch **cannot** match any of the regular expressions from the `--deny` arguments.

For example, the following would refrain committing to `master` or `main`,
and would enforce lowercase characters, together with a few separators.

```yaml
  - repo: https://github.com/efrecon/pre-commit-hook-branch-check
    rev: v0.2.0
    hooks:
      - id: branch-check
        args:
          - --deny=^(master|main)$
          - --allow=^[0-9a-z_./-]+$
```

## Branch Detection

When run from CI systems, `git` might be in detached HEAD state.
This happens when running during pull/merge requests.
This hook will use known environment variables containing the name of the source branch to cover those cases.
When the variables are not set -- in most cases -- it will first attempt to run the following command:

```bash
git symbolic-ref --short HEAD
```

When that command fail, it will revert to using:

```bash
git name-rev --name-only HEAD
```
