#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# filter items with nonzero transforms from selection

import modo
import modo.constants as c

from scripts.select_nonzero_transform_items import get_nonzero_items


def main():
    items = get_nonzero_items(modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True))

    modo.Scene().deselect()
    for item in items:
        item.select()


if __name__ == '__main__':
    main()
