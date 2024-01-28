#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d
# exports hierarchy items as hierarchy scene and other items as meshref scene

import modo
import modo.constants as c
import lx

from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reset import is_root_prefix


def main() -> None:
    superlocators = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    hierarchies = {i for i in superlocators if (not i.parent and is_root_prefix(i))}

    filename = modo.Scene().filename
    current_scene_id = lx.eval('scene.set ?')
    lx.eval('scene.new')
    hierarchy_scene_id = lx.eval('scene.set ?')
    modo.Scene().removeItems(modo.Scene().item('Mesh'))
    modo.Scene().removeItems(modo.Scene().item('Camera'))
    modo.Scene().removeItems(modo.Scene().item('Directional Light'))

    lx.eval(f'scene.set {current_scene_id}')
    modo.Scene().deselect()
    for hierarchy in hierarchies:
        hierarchy.select()

    lx.eval(f'!layer.import {hierarchy_scene_id} {{}} childs:true shaders:false move:true position:0')
    hierarchy_filename = str(filename).rsplit('.lxo')[0] + '_Hierarchy.lxo'
    lx.eval(f'scene.saveAs "{hierarchy_filename}" $LXOB false')

    lx.eval(f'scene.set {current_scene_id}')
    meshref_filename = str(filename).rsplit('.lxo')[0] + '_MeshRef.lxo'
    lx.eval(f'scene.saveAs "{meshref_filename}" $LXOB false')


if __name__ == '__main__':
    main()
