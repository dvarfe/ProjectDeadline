#!/usr/bin/env python3
import glob
from doit.tools import create_folder
PODEST = "Deadline/po"


def task_gitclean():
    """Clean all generated files not tracked by GIT."""
    return {
        'actions': ['git clean -xdf'],
    }


def task_build_docs():
    """Make HTML documentation."""
    return {
        'actions': ['sphinx-build -M html docs/sphinx docs/build'],
        'task_dep': ['run_autodoc']
    }


def task_clean_docs():
    """Remove all documentation build files."""
    return {
        'actions': ['rm -rf docs/build'],
    }


def task_run_autodoc():
    """Run autodoc to extract all docstrings."""
    return {
        'actions': ['sphinx-apidoc -o docs/sphinx Deadline'],
    }


def task_pot():
    """Re-create .pot."""
    return {
        'actions': ['pybabel extract -o Deadline.pot Deadline'],
        'file_dep': glob.glob('Deadline/*.py'),
        'targets': ['DateTime.pot'],
    }


def task_po():
    """Update translations."""
    return {
        'actions': [f'pybabel update --ignore-pot-creation-date -D Deadline -d {PODEST} -i Deadline.pot'],
        'file_dep': ['Deadline.pot'],
    }


def task_mo():
    """Compile translations."""
    return {
        'actions': [
            (create_folder, [f'{PODEST}/u_RU.UTF-8/LC_MESSAGES']),
            f'pybabel compile -D Deadline -d {PODEST}'
        ],
        'file_dep': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/Deadline.po'],
        'targets': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/Deadline.mo'],
    }


def task_requirements():
    """Dump Pipfile requirements"""
    return {
        'actions': ['pipenv requirements --categories="packages" > requirements.txt'],
        'file_dep': ['Pipfile'],
        'targets': ['requirements.txt'],
    }


def task_style():
    """Check style against flake8."""
    return {
        'actions': ['flake8 Deadline']
    }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {'actions': ['']}  # TODO: Remove
    return {
        'actions': ['pydocstyle Deadline']
    }


def task_test():
    """Preform tests."""
    yield {'actions': ['coverage run -m unittest -v'], 'name': "run"}
    yield {'actions': ['coverage report'], 'verbosity': 2, 'name': "report"}


def task_check():
    """Perform all checks."""
    return {
        'actions': None,
        'task_dep': ['style', 'docstyle', 'test']
    }


def task_wheel():
    """Create binary wheel distribution."""
    return {
        'actions': ['python -m build -w'],
        'task_dep': ['mo', 'requirements'],
    }


def task_all():
    """Perform all build task."""
    return {
        'actions': None,
        'task_dep': ['check', 'build_docs', 'wheel']
    }
