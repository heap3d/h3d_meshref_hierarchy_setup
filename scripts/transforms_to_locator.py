#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# scan scene and add locator parent to transformed mesh


import modo
import modo.constants as c
import lx

from typing import Union

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import get_parent_index
import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc


LOCATOR_SUFFIX = ' loc'


def get_transforms(item: modo.Item) -> tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
        ]:
    px = lx.eval(f'transform.channel pos.X ? item:{item.id}')
    py = lx.eval(f'transform.channel pos.Y ? item:{item.id}')
    pz = lx.eval(f'transform.channel pos.Z ? item:{item.id}')
    rx = lx.eval(f'transform.channel rot.X ? item:{item.id}')
    ry = lx.eval(f'transform.channel rot.Y ? item:{item.id}')
    rz = lx.eval(f'transform.channel rot.Z ? item:{item.id}')
    sx = lx.eval(f'transform.channel scl.X ? item:{item.id}')
    sy = lx.eval(f'transform.channel scl.Y ? item:{item.id}')
    sz = lx.eval(f'transform.channel scl.Z ? item:{item.id}')

    return ((px, py, pz), (rx, ry, rz), (sx, sy, sz))  # type: ignore


def is_nonzero_transforms(item: modo.Item) -> bool:
    pos, rot, scl = get_transforms(item)
    if any((*pos, *rot)):
        return True
    if scl[0] != 1.0 or scl[1] != 1.0 or scl[2] != 1.0:
        return True
    return False


def is_transforms_matched(
        transform1: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
        transform2: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
        precision: int = 3,
        ) -> bool:
    flat1 = [val for transform in transform1 for val in transform]
    flat2 = [val for transform in transform2 for val in transform]
    if not all([round(val[0], precision) == round(val[1], precision) for val in zip(flat1, flat2)]):
        return False
    return True


def matched_item(item: modo.Item, items: list[modo.Item]) -> Union[modo.Item, None]:
    item_transforms = get_transforms(item)
    for itemto in items:
        itemto_transforms = get_transforms(itemto)
        if is_transforms_matched(item_transforms, itemto_transforms):
            return itemto

    return None


def match_item(item: modo.Item, itemto: modo.Item):
    lx.eval(f'item.match item pos average:false item:{item.id} itemTo:{itemto.id}')
    lx.eval(f'item.match item rot average:false item:{item.id} itemTo:{itemto.id}')
    lx.eval(f'item.match item scl average:false item:{item.id} itemTo:{itemto.id}')


def parent(item: modo.Item, parent: Union[modo.Item, None] = None, inplace: int = 1, position: int = 0):
    if not parent:
        lx.eval(f'item.parent item:{item.id} parent:{{}} position:{position} inPlace:{inplace}')
        return
    lx.eval(f'item.parent item:{item.id} parent:{parent.id} position:{position} inPlace:{inplace}')


def is_hierarchy_setup_item(item: modo.Item) -> bool:
    if str(item.name).startswith(h3dc.MESH_PREFIX):
        return True
    if str(item.name).startswith(h3dc.ROOT_PREFIX):
        return True
    return False


def convert_transforms(meshes: list[modo.Mesh], locators: list[modo.Item]) -> list[modo.Item]:
    working_locators = locators[:]
    for mesh in meshes:
        printd(f'{mesh.name}, {mesh=}')
        if is_hierarchy_setup_item(mesh):
            printd('is hierarchy setup item. skipped.', 1)
            continue
        if not is_nonzero_transforms(mesh):
            printd('not is_nonzero_transfers. skipped.', 1)
            continue
        printd(f'non-zero transforms detected. {mesh.name=} {mesh=}', 1)
        locator = matched_item(mesh, working_locators)
        if not locator:
            printd("locator doesn't exist. creating...", 1)
            locator = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
            locator.name = mesh.name + LOCATOR_SUFFIX
            match_item(locator, mesh)
            parent(locator, position=get_parent_index(mesh))
            working_locators.append(locator)
        else:
            printd('locator found', 1)
        printd(f'locator: {locator.name} {locator=}', 1)
        parent(mesh, locator)

    return working_locators[len(locators):]


def main():
    meshes = [item for item in modo.Scene().meshes if not item.parent]
    printi(meshes, 'meshes:')
    locators = [item for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=False) if not item.parent]
    printi(locators, 'locators:')

    selected = modo.Scene().selected

    new_locators = convert_transforms(meshes, locators)

    modo.Scene().deselect()
    if new_locators:
        for item in new_locators:
            item.select()
    else:
        for item in selected:
            item.select()


if __name__ == '__main__':
    h3dd = H3dDebug(enable=False, file=modo.Scene().name + '.log')
    printd = h3dd.print_debug
    printi = h3dd.print_items
    main()
