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

import modo
import modo.constants as c

import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc
from h3d_utilites.scripts.h3d_utils import (
    parent_items_to,
    replace_file_ext,
    itype_int,
    set_description_tag,
    get_description_tag,
)
from h3d_utilites.scripts.h3d_debug import H3dDebug


def normalize_hierarchy(root: modo.Item) -> modo.Item:
    """Replace mesh items with children by locators, parent original meshes to locators

    Args:
        root (modo.Item): root of existing hierarchy

    Returns:
        modo.Item: root of updated hierarchy
    """
    mesh_candidates = {
        i for i in root.children(recursive=True, itemType=c.MESH_TYPE) if i.children()
    }
    meshinst_candidates = {
        i for i in root.children(recursive=True, itemType=c.MESHINST_TYPE) if i.children()
    }
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
        parent_items_to([locator], mesh.parent)
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
    if not str(item.name).startswith(prefix):
        item.name = prefix + item.name


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

    Args:
        item (modo.Item): mesh item to store info about
    """
    if not item.parent:
        return

    hierarchy_id = get_description_tag(item.parent)
    set_description_tag(item=item, text=hierarchy_id)
    add_prefix_to_name(item=item, prefix=h3dc.MESH_PREFIX)


def unparent_hierarchy(root: modo.Item) -> None:
    """Unparent all meshes from hierarchy and store information about them

    Args:
        root (modo.Item): root of hierarchy
    """
    meshes = [
        i for i in root.children(recursive=True)
        if (itype_int(i.type) == c.MESH_TYPE or itype_int(i.type) == c.MESHINST_TYPE)
    ]
    if not meshes:
        return

    parents: set[modo.Item] = {root}
    for mesh in meshes:
        if not mesh.parent:
            continue
        parents.add(mesh.parent)

    for parent in parents:
        store_parent_info(parent)

    for mesh in meshes:
        store_mesh_info(mesh)

    flattened_meshes = {i for i in meshes if i.parent}
    if flattened_meshes:
        parent_items_to(meshes, None)


def main() -> None:
    items: set[modo.Item] = set(
        modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    )
    roots: set[modo.Item] = {i for i in items if not i.parents}
    hierarchies: set[modo.Item] = {i for i in roots if i.children()}

    normalized_hierarchies: set[modo.Item] = set()
    for hierarchy in hierarchies:
        if not hierarchy.name.startswith(h3dc.ROOT_PREFIX):
            normalized_hierarchy = normalize_hierarchy(hierarchy)
        else:
            normalized_hierarchy = hierarchy
        normalized_hierarchies.add(normalized_hierarchy)

    for normalized_hierarchy in normalized_hierarchies:
        unparent_hierarchy(normalized_hierarchy)


scenename = replace_file_ext(modo.Scene().filename, ".log")
h3dd = H3dDebug(enable=False, file=scenename)

if __name__ == "__main__":
    main()
