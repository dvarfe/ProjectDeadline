#!/usr/bin/env python3

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
