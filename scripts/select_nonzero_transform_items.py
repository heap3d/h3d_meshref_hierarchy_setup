#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# select items with nonzero transforms

import modo
import modo.constants as c

from scripts.load_selected_item_info import is_zero_transforms, TOLERANCE


def main():
    nonzero_items = get_nonzero_items(modo.Scene())
    if not nonzero_items:
        return

    modo.Scene().deselect()
    for item in nonzero_items:
        item.select()


def get_nonzero_items(scene: modo.Scene) -> list[modo.Item]:
    return [
        item
        for item in scene.items(itype=c.LOCATOR_TYPE, superType=True)
        if not is_zero_transforms(item, TOLERANCE)
    ]


if __name__ == '__main__':
    main()
