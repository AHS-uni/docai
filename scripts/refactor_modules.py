#!/usr/bin/env python3
import re
import shutil
from pathlib import Path

# ------------------------------------------------------------------------------
# Adjust this if your layout differs. This assumes:
# <project_root>/
#   scripts/rename_pkg_to_service.py
#   src/docai/
# ------------------------------------------------------------------------------

# 1. Locate the docai root
ROOT = Path(__file__).resolve().parent.parent / "src" / "docai"

# 2. Gather every immediate sub-package name under src/docai/
all_pkgs = [d.name for d in ROOT.iterdir() if d.is_dir()]

# 3. Find which still have pkg/pkg.py but lack pkg/service.py
to_rename = []
for pkg in all_pkgs:
    pkg_dir = ROOT / pkg
    if (pkg_dir / f"{pkg}.py").exists() and not (pkg_dir / "service.py").exists():
        to_rename.append(pkg)

if to_rename:
    print("→ Renaming modules:")
    for pkg in to_rename:
        old = ROOT / pkg / f"{pkg}.py"
        new = ROOT / pkg / "service.py"
        print(f"   • {old.relative_to(ROOT)} → {new.relative_to(ROOT)}")
        shutil.move(old, new)
else:
    print("⚠️  No pkg/pkg.py modules found to rename. Skipping rename step.")

# 4. Build regex patterns for EVERY pkg to catch old imports
patterns = []
for pkg in all_pkgs:
    patterns += [
        # absolute imports
        (re.compile(rf"\bimport\s+{pkg}\.{pkg}\b"), f"import {pkg}.service"),
        (
            re.compile(rf"\bfrom\s+{pkg}\s+import\s+{pkg}\b"),
            f"from {pkg} import service",
        ),
        (
            re.compile(rf"\bfrom\s+{pkg}\.{pkg}\s+import\b"),
            f"from {pkg}.service import",
        ),
        # relative imports
        (re.compile(rf"\bfrom\s+\.{pkg}\s+import\b"), "from .service import"),
        (re.compile(rf"\bimport\s+\.{pkg}\.{pkg}\b"), "import .service.service"),
        (
            re.compile(rf"\bfrom\s+\.{pkg}\.{pkg}\s+import\b"),
            "from .service.service import",
        ),
    ]


def patch_file(path: Path, root: Path):
    text = path.read_text(encoding="utf-8")
    new_text = text
    for pat, repl in patterns:
        new_text = pat.sub(repl, new_text)
    if new_text != text:
        print(f"  ↳ Patched {path.relative_to(root)}")
        path.write_text(new_text, encoding="utf-8")


# 5. Apply patches under src/docai/
print("\n→ Patching imports in src/docai/")
for py in ROOT.rglob("*.py"):
    patch_file(py, ROOT)

# 6. Apply patches under <project_root>/tests/ (if it exists)
PROJECT = Path(__file__).resolve().parent.parent
TESTS_ROOT = PROJECT / "tests"
if TESTS_ROOT.exists():
    print("\n→ Patching imports in tests/")
    for py in TESTS_ROOT.rglob("*.py"):
        patch_file(py, PROJECT)

print("\n✅ Done! Don’t forget to run:\n    isort . && black .\n    pytest")
