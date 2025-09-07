.PHONY: .uv
.uv: ## Check that uv is installed
	@uv --version || echo "Please make sure uv is installed"

.PHONY: .pre-commit
.pre-commit: ## Check that pre-commit is installed
	@uv run pre-commit -V || echo "Please make sure pre-commit is installed"

.PHONY: help
help: ## Display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: generate-lock-file
generate-lock-file: .uv ## Generate a uv.lock file from pyproject.toml
	@uv lock

.PHONY: sync-venv
sync-venv: .uv ## Sync local environment for Python development on pipelines
	@uv sync --all-groups

.PHONY: pre-commit-install
pre-commit-install: .uv .pre-commit ## Install pre-commit hooks
	@uv run pre-commit install --install-hooks

.PHONY: pre-commit
pre-commit: .uv .pre-commit ## Runs the pre-commit checks over entire repo
	@uv run pre-commit run --all-files --color=always

.PHONY: ruff
ruff: .uv .pre-commit ## Runs ruff linting and formatting
	@if [ -n "$(path)" ]; then \
		uv run ruff check --fix $(path) && \
		uv run ruff format $(path); \
	else \
		uv run ruff check --fix && \
		uv run ruff format; \
	fi

.PHONY: mypy
mypy: .uv .pre-commit ## Runs mypy type checking
	@if [ -n "$(path)" ]; then \
		uv run mypy $(path); \
	else \
		uv run mypy src; \
	fi
