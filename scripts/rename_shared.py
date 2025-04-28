#!/usr/bin/env python3
"""
Codemod to fix import paths after moving:
  src/docai/models → src/docai/shared/models
  src/docai/utils  → src/docai/shared/utils
"""

from bowler import Query


def _rewrite_import(node, capture, filename):
    """
    Replace any occurrence of 'docai.models' → 'docai.shared.models'
    and 'docai.utils' → 'docai.shared.utils' in the import line.
    """
    # node.value is the text of the import statement
    new_line = node.value.replace("docai.models", "docai.shared.models").replace(
        "docai.utils", "docai.shared.utils"
    )
    # node.clone() + with_changes() will produce a new node with updated text
    return node.clone().with_changes(value=new_line)


def main():
    (
        Query("src/docai")
        # match any import statement that mentions docai.models
        .select_module("docai.models")
        .modify(_rewrite_import)
        # match any import statement that mentions docai.utils
        .select_module("docai.utils")
        .modify(_rewrite_import)
        .write()
    )


if __name__ == "__main__":
    main()
