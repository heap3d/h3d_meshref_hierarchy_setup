#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# select meshref meshes in the scene:
# select_meshref_meshes.py
# or
# select children meshref meshes for selected:
# select_meshref_meshes.py selected

from typing import Iterable

import lx
import modo
import modo.constants as c


ARG_ALL = 'all'
ARG_SELECTED = 'selected'
ARG_CHILDREN = 'children'
ARG_SAME = 'same'


def main():
    selection_options = {
        ARG_ALL: get_all_meshrefs,
        ARG_SELECTED: get_selected_meshrefs,
        ARG_CHILDREN: get_children_meshrefs,
        ARG_SAME: get_same_meshrefs,
    }

    args = lx.args()
    if not args:
        get_meshrefs = get_all_meshrefs
    else:
        get_meshrefs = selection_options.get(args[0], get_all_meshrefs)

    meshref_meshes = get_meshrefs()

    modo.Scene().deselect()
    for mesh in meshref_meshes:
        mesh.select()


def get_all_meshrefs() -> list[modo.Item]:
    items = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    return get_meshrefs_from(items)


def get_selected_meshrefs() -> list[modo.Item]:
    items = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    return get_meshrefs_from(items)


def get_children_meshrefs() -> list[modo.Item]:
    items: list[modo.Item] = []
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    for item in selected:
        items.extend(item.children(recursive=True))

    return get_meshrefs_from(items)


def get_same_meshrefs() -> list[modo.Item]:
    meshrefs_scene_names: set[str] = set()
    same_meshrefs: list[modo.Item] = []

    items = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    for item in items:
        if not is_meshref(item):
            continue
        scene_name = get_meshref_scene_name(item)
        meshrefs_scene_names.add(scene_name)

    for meshref in get_meshrefs_from(get_all_meshrefs()):
        if get_meshref_scene_name(meshref) not in meshrefs_scene_names:
            continue
        same_meshrefs.append(meshref)

    return same_meshrefs


def get_meshrefs_from(items: Iterable[modo.Item]) -> list[modo.Item]:
    if not items:
        return []

    meshref_meshes = []
    for item in items:
        if not is_meshref(item):
            continue
        meshref_meshes.append(item)

    return meshref_meshes


def is_meshref(item: modo.Item) -> bool:
    if not item:
        raise ValueError('No item provided')

    if ':' not in item.id:
        return False

    return True


def get_meshref_scene_name(item: modo.Item) -> str:
    if not is_meshref(item):
        raise ValueError(f'Provided item is not a meshref: <{item.name}> <{item}>')
    return str(item.id).split(':')[0]


if __name__ == '__main__':
    main()
