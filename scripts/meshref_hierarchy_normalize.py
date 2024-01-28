#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy normalize tool adds locators to the hierarchy nodes at mesh and mesh instance items
# usage:
# 1. select hierarchy root
# 2. run the Normalize Hierarchy command

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import replace_file_ext
from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_unparent import normalize_hierarchy


def main() -> None:
    roots = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not roots:
        return

    updated_roots: set[modo.Item] = set()
    for root in roots:
        updated_root = normalize_hierarchy(root)
        updated_roots.add(updated_root)

    modo.Scene().deselect()
    for root in updated_roots:
        root.select()


h3dd = H3dDebug(enable=False, file=replace_file_ext(modo.Scene().filename, '.log'))
if __name__ == '__main__':
    main()
