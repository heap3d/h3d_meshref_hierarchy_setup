#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add a 'processed' mark to items

import lx
import modo
import modo.constants as c

from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reparent import add_processed_mark, is_processed
from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reset import is_mesh_prefix
import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc


def main():
    if not lx.args():
        superlocators = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
        meshes = {i for i in superlocators if is_mesh_prefix(i)}
        for mesh in meshes:
            if not is_processed(mesh):
                add_processed_mark(mesh)
    elif h3dc.CMD_SELECTED:
        superlocators = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
        meshes = {i for i in superlocators if is_mesh_prefix(i)}
        for mesh in meshes:
            if not is_processed(mesh):
                add_processed_mark(mesh)
        modo.Scene().deselect()
        for item in meshes:
            item.select()


if __name__ == '__main__':
    main()
