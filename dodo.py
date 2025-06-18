#!/usr/bin/env python3
import glob
from doit.tools import create_folder

PODEST = 'Deadline/po'


def task_build_docs():
    """Make HTML documentation."""
    return {
        'actions': ['sphinx-build -M html docs/sphinx docs/build'],
    }


def task_clean_build_docs():
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
        'actions': ['pybabel update --ignore-pot-creation-date -D Deadline -d po -i Deadline.pot'],
        'file_dep': ['Deadline.pot'],
        'targets': ['po/ru/LC_MESSAGES/Deadline.po'],
    }


def task_mo():
    """Compile translations."""
    return {
        'actions': [
            (create_folder, [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES']),
            f'pybabel compile -D Deadline -d po'
        ],
        'file_dep': ['po/ru_RU.UTF-8/LC_MESSAGES/Deadline.po'],
        'targets': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/Deadline.mo'],
    }
