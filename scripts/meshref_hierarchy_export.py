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

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out

HIERARCHY_SUFFIX = '_Hierarchy'
MESH_SUFFIX = '_MeshRef'
BACKUP_SUFFIX = '_Backup'


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
    fn_in(f'{name=}')
    basename, = name.split('.')[:1]
    prints(basename)
    nosuffix = basename.removesuffix(MESH_SUFFIX)
    prints(nosuffix)
    namesuffix = f'{nosuffix}{HIERARCHY_SUFFIX}'
    prints(namesuffix)
    fileindex = get_fileindex(f'{namesuffix}{BACKUP_SUFFIX}_.lxo')
    prints(fileindex)

    backupname = f'{namesuffix}{BACKUP_SUFFIX}{fileindex}.lxo'
    prints(backupname)
    fullname = f'{namesuffix}.lxo'
    prints(fullname)
    fn_out()

    return [fullname, backupname]


def generate_filename_backup_meshref(name: str) -> list[str]:
    fn_in(f'{name=}')
    basename, = name.split('.')[:1]
    prints(basename)
    nosuffix = basename.removesuffix(MESH_SUFFIX)
    prints(nosuffix)
    namesuffix = f'{nosuffix}{MESH_SUFFIX}'
    prints(namesuffix)
    fileindex = get_fileindex(f'{namesuffix}{BACKUP_SUFFIX}_.lxo')
    prints(fileindex)

    backupname = f'{namesuffix}{BACKUP_SUFFIX}{fileindex}.lxo'
    prints(backupname)
    fullname = f'{namesuffix}.lxo'
    prints(fullname)
    fn_out()

    return [fullname, backupname]


def get_fileindex(filepath: str) -> str:
    fn_in(f'{filepath=}')
    if not os.path.isfile(filepath):
        fn_out('empty string')
        return ''

    dir, scenename = os.path.split(filepath)
    prints(dir)
    prints(scenename)
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    prints(files)

    basename = os.path.splitext(scenename)[0]
    prints(basename)
    indexedfiles = sorted([f for f in files if f.startswith(basename)])
    prints(indexedfiles)
    pattern = r'(\d+).lxo$'
    try:
        lastindex = int(re.findall(pattern, indexedfiles[-1])[0])
        prints(lastindex)
    except IndexError:
        lastindex = 0
        prints('lastindex set to 0')
    fn_out(f'_{lastindex+1:04}')
    return f'_{lastindex+1:04}'


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
    h3dd.enable_debug_output(False)
    main()
