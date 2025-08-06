#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Normalize all hierarchies. Hierarchy normalize tool adds locators to the hierarchy nodes
# at an mesh and mesh instance items

import modo
import modo.constants as c

from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_unparent import normalize_hierarchy


def main() -> None:
    roots = [root for root in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True) if root.children()]
    if not roots:
        return

    updated_roots: set[modo.Item] = set()
    for root in roots:
        updated_root = normalize_hierarchy(root)
        updated_roots.add(updated_root)

    modo.Scene().deselect()
    for root in updated_roots:
        root.select()


if __name__ == '__main__':
    main()
