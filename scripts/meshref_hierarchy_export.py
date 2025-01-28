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


HIERARCHY_SUFFIX = '_Hierarchy'
MESH_SUFFIX = '_MeshRef'
BACKUP_SUFFIX = '_Backup_'


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

    hierarchy_filename, hierarchy_backupname = generate_filename_backup_hierarchy(filename)
    if file_exist(hierarchy_filename):
        file_rename(hierarchy_filename, hierarchy_backupname)
    lx.eval(f'!layer.import {hierarchy_scene_id} {{}} childs:true shaders:false move:true position:0')
    lx.eval(f'scene.saveAs "{hierarchy_filename}" $LXOB false')

    meshref_filename, meshref_backupname = generate_filename_backup_meshref(filename)
    if file_exist(meshref_filename):
        file_rename(meshref_filename, meshref_backupname)
    lx.eval(f'scene.set {current_scene_id}')
    lx.eval(f'scene.saveAs "{meshref_filename}" $LXOB false')


def generate_filename_backup_hierarchy(name: str) -> list[str]:
    basename, = name.split('.')[:1]
    nosuffix = basename.removesuffix(MESH_SUFFIX)
    namesuffix = f'{nosuffix}{HIERARCHY_SUFFIX}'
    fileindex = get_fileindex(f'{namesuffix}{BACKUP_SUFFIX}.lxo')

    backupname = f'{namesuffix}{BACKUP_SUFFIX}{fileindex}.lxo'
    fullname = f'{namesuffix}.lxo'

    return [fullname, backupname]


def generate_filename_backup_meshref(name: str) -> list[str]:
    basename, = name.split('.')[:1]
    nosuffix = basename.removesuffix(MESH_SUFFIX)
    namesuffix = f'{nosuffix}{MESH_SUFFIX}'
    fileindex = get_fileindex(f'{namesuffix}{BACKUP_SUFFIX}.lxo')

    backupname = f'{namesuffix}{BACKUP_SUFFIX}{fileindex}.lxo'
    fullname = f'{namesuffix}.lxo'

    return [fullname, backupname]


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

    return f'{lastindex+1:04}'


def file_exist(path: str) -> bool:
    try:
        with open(path, 'r') as _:
            print(f'file <{path}> already exist.')

            return True

    except FileNotFoundError:

        return False


def file_rename(source: str, destination: str):
    print(f'renaming file <{source}> to the <{destination}>...')
    os.rename(source, destination)
    print('file successfully renamed.')


if __name__ == '__main__':
    main()
