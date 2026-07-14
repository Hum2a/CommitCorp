# Contributing to the Infinite Commit Machine

Thank you for your interest in advancing CommitCorp's Autonomous Historical
Expansion Platform.

## Mission Alignment

Contributions should reinforce Continuous Chronological Integration.
If a change reduces repository seriousness, it will be returned for revision
by the Office of Repository Excellence.

## Development Environment

* Python 3.12+
* Git
* No runtime third-party packages

```bash
python -m unittest discover -s tests -v
python scripts/validate_config.py
python -m compileall commit_machine run.py
```

## Running Locally

The Historical Persistence Engine must only run on a machine you control
(local workstation or VPS). GitHub Actions must never generate chronology.

```bash
python run.py --doctor
python run.py --dry-run
python run.py --once
python run.py
```

## Pull Request Expectations

* Type hints on public functions
* Unit tests for behavioural changes
* Documentation updates when enterprise terminology changes
* No force-push to protected branches
* No jokes that acknowledge the joke

## Commit Messages (for human contributors)

Human contributors may write normal commit messages. The Infinite Commit
Machine maintains its own corpus of ≥250 ceremonial messages for autonomous
operation.

## Code Review

Reviews are conducted by the Version Control Steering Committee (and you).
Approval criteria include correctness, safety of Git operations, and tone.
