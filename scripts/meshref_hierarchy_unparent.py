#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy unparent tool stores hierarchy info and flattens mesh items hierarchy
# usage:
# 1. remove unnecessary elements from hierarchy
# 2. run Unparent Meshes command

from typing import Iterable

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_parent_index

import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc
from h3d_utilites.scripts.h3d_utils import (
    parent_items_to,
    itype_int,
    set_description_tag,
    get_description_tag,
)


def normalize_hierarchy(root: modo.Item) -> modo.Item:
    """Replace mesh items with children by locators, parent original meshes to locators

    Args:
        root (modo.Item): root of existing hierarchy

    Returns:
        modo.Item: root of updated hierarchy
    """
    mesh_candidates = {i for i in root.children(recursive=True, itemType=c.MESH_TYPE) if i.children()}
    meshinst_candidates = {i for i in root.children(recursive=True, itemType=c.MESHINST_TYPE) if i.children()}
    replace_candidates = mesh_candidates.union(meshinst_candidates)

    root_is_mesh = itype_int(root.type) == c.MESH_TYPE or itype_int(root.type) == c.MESHINST_TYPE
    root_has_children = bool(root.children())
    if root_is_mesh and root_has_children:
        replace_candidates.add(root)

    if not replace_candidates:
        return root

    for mesh in replace_candidates:
        locator = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
        locator.name = mesh.name + " loc"

        for item in mesh.children():
            item.setParent(locator)

        locator.setParent(mesh)
        parent_items_to([locator], mesh.parent)  # type: ignore
        parent_items_to([mesh], locator)

    updated_root = root.parent
    if not updated_root:
        return root

    return updated_root


def add_prefix_to_name(item: modo.Item, prefix: str) -> None:
    """Adds given prefix to the specified item name

    Args:
        item (modo.Item): item to change the name
        prefix (str): prefix to add to the item name
    """
    try:
        if not str(item.name).startswith(prefix):
            item.name = prefix + item.name
    except RuntimeError:
        print(f'{item.name} : Failed to change item name.')


def store_parent_info(item: modo.Item) -> None:
    """Store hierarchy info about specified item as parent:
        - parent prefix in the item name
        - unique hierarchy id in the description tag

    Args:
        item (modo.Item): parent item to store info about
    """
    scenename = modo.Scene().name
    if not scenename:
        hierarchy_id = item.name
    else:
        hierarchy_id = scenename + "/" + item.name

    set_description_tag(item=item, text=hierarchy_id)
    add_prefix_to_name(item=item, prefix=h3dc.ROOT_PREFIX)


def store_mesh_info(item: modo.Item) -> None:
    """Store hierarchy info about specified mesh item as child:
        - child prefix in the mesh name
        - hierarchy id pointed to the corresponding parent item
        - [px py pz]: position values
        - [rx ry rz]: rotation values
        - [sx sy sz]: scale values

    Args:
        item (modo.Item): mesh item to store info about
    """
    if not item.parent:
        return
    hierarchy_id = get_description_tag(item.parent)
    px = lx.eval(f'transform.channel pos.X ? item:{{{item.id}}}')
    py = lx.eval(f'transform.channel pos.Y ? item:{{{item.id}}}')
    pz = lx.eval(f'transform.channel pos.Z ? item:{{{item.id}}}')
    rx = lx.eval(f'transform.channel rot.X ? item:{{{item.id}}}')
    ry = lx.eval(f'transform.channel rot.Y ? item:{{{item.id}}}')
    rz = lx.eval(f'transform.channel rot.Z ? item:{{{item.id}}}')
    sx = lx.eval(f'transform.channel scl.X ? item:{{{item.id}}}')
    sy = lx.eval(f'transform.channel scl.Y ? item:{{{item.id}}}')
    sz = lx.eval(f'transform.channel scl.Z ? item:{{{item.id}}}')
    pos_values = f'{px} {py} {pz}'
    rot_values = f'{rx} {ry} {rz}'
    scl_values = f'{sx} {sy} {sz}'

    description = f'{hierarchy_id}\n{pos_values}\n{rot_values}\n{scl_values}'
    set_description_tag(item=item, text=description)
    add_prefix_to_name(item=item, prefix=h3dc.MESH_PREFIX)


def unparent_hierarchy(root: modo.Item) -> None:
    """Unparent all meshes from hierarchy and store information about them

    Args:
        root (modo.Item): root of hierarchy
    """
    meshes = [
        i
        for i in root.children(recursive=True)
        if (itype_int(i.type) == c.MESH_TYPE or itype_int(i.type) == c.MESHINST_TYPE)
    ]
    if not meshes:
        return

    parents: set[modo.Item] = {root, }
    for mesh in meshes:
        if not mesh.parent:
            continue
        parents.add(mesh.parent)

    for parent in parents:
        store_parent_info(parent)

    for mesh in meshes:
        store_mesh_info(mesh)

    flattened_meshes: set[modo.Item] = {i for i in meshes if i.parent}
    if flattened_meshes:
        for flatten_mesh in flattened_meshes:
            index = get_parent_index(flatten_mesh)
            parent_items_to(items=flattened_meshes, parent=None, index=index)


def get_normalized_hierarchies(roots: Iterable[modo.Item]) -> set[modo.Item]:
    hierarchies: set[modo.Item] = {i for i in roots if i.children()}
    normalized_hierarchies: set[modo.Item] = set()
    for hierarchy in hierarchies:
        if not hierarchy.name.startswith(h3dc.ROOT_PREFIX):
            normalized_hierarchy = normalize_hierarchy(hierarchy)
        else:
            normalized_hierarchy = hierarchy
        normalized_hierarchies.add(normalized_hierarchy)

    return normalized_hierarchies


def default_action():
    items: set[modo.Item] = set(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))
    roots: set[modo.Item] = {i for i in items if not i.parents}
    normalized_hierarchies = get_normalized_hierarchies(roots)

    for normalized_hierarchy in normalized_hierarchies:
        unparent_hierarchy(normalized_hierarchy)


def hierarchy_action():
    items: set[modo.Item] = set(modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True))
    children: set[modo.Item] = set()
    for item in items:
        children.update(item.children(recursive=True, itemType=c.MESH_TYPE))
        children.update(item.children(recursive=True, itemType=c.MESHINST_TYPE))
    items.update(children)
    roots: set[modo.Item] = {i.parent for i in items if i.parent}  # type: ignore
    normalized_hierarchies = get_normalized_hierarchies(roots)

    for normalized_hierarchy in normalized_hierarchies:
        unparent_hierarchy(normalized_hierarchy)


def main() -> None:
    arg = ''
    if lx.args():
        arg = lx.args()[0]  # type: ignore

    actions = {
        h3dc.CMD_HIERARCHY: hierarchy_action,
    }

    action = actions.get(arg, default_action)
    action()


if __name__ == "__main__":
    main()
