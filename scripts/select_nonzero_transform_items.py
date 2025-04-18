#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# select items with nonzero transforms

from typing import Iterable

import modo
import modo.constants as c

from scripts.load_selected_item_info import is_zero_transforms, TOLERANCE


def main():
    items = get_nonzero_items(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))

    modo.Scene().deselect()
    for item in items:
        item.select()


def get_nonzero_items(items: Iterable[modo.Item]) -> list[modo.Item]:
    return [
        item
        for item in items
        if not is_zero_transforms(item, TOLERANCE)
    ]


if __name__ == '__main__':
    main()
