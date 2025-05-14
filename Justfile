project_dir := "."
env_prefix := "micromamba run -p ./.micromamba"

lint:
    {{env_prefix}} black --check --diff {{project_dir}}
    {{env_prefix}} ruff check {{project_dir}}
    {{env_prefix}} mypy {{project_dir}} --strict

reformat:
    {{env_prefix}} black {{project_dir}}
    {{env_prefix}} ruff format {{project_dir}}

run:
    {{env_prefix}} python -m src.git2md || true

clean:
    find . -name "__pycache__" -exec rm -rf {} +
    find . -name "*.pyc" -exec rm -f {} +
    rm -rf build dist .eggs .tox .nox .coverage .hypothesis .pytest_cache

# Обновить версию в PKGBUILD и setup.py
update_version version:
    sed -i "s/version=\"[0-9\.]\+\"/version=\"{{version}}\"/" setup.py
    echo "Version updated to {{version}}"
