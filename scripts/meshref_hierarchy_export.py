#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# exports hierarchy items as hierarchy scene and other items as meshref scene

import os
import re

import modo
import modo.constants as c
import lx

from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reset import is_root_prefix

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import replace_file_ext


def get_fileindex(filepath: str) -> str:
    if not os.path.isfile(filepath):
        return ''
    dir, scenename = os.path.split(filepath)
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    basename = os.path.splitext(scenename)[0]
    indexedfiles = sorted([f for f in files if f.startswith(basename)])
    pattern = r'(\d+).lxo$'
    try:
        lastindex = int(re.findall(pattern, indexedfiles[-1])[0])
    except IndexError:
        lastindex = 0

    return f'_{lastindex+1:04}'


def generate_filename(name: str, is_hierarchy: bool, h_sfx: str = '_Hierarchy', m_sfx: str = '_MeshRef') -> str:
    name, = name.rsplit('.')[:1]
    name = name.removesuffix(m_sfx)
    name = name.removesuffix(h_sfx)

    if not is_hierarchy:
        name = name + m_sfx
        return f'{name}.lxo'

    name = name + h_sfx
    fileindex = get_fileindex(f'{name}.lxo')

    return f'{name}{fileindex}.lxo'


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

    hierarchy_filename = generate_filename(filename, is_hierarchy=True)
    lx.eval(f'!layer.import {hierarchy_scene_id} {{}} childs:true shaders:false move:true position:0')
    lx.eval(f'scene.saveAs "{hierarchy_filename}" $LXOB false')

    meshref_filename = generate_filename(filename, is_hierarchy=False)
    lx.eval(f'scene.set {current_scene_id}')
    lx.eval(f'scene.saveAs "{meshref_filename}" $LXOB false')


h3dd = H3dDebug(enable=False, file=replace_file_ext(modo.Scene().name, ext='.log'))

if __name__ == '__main__':
    main()
