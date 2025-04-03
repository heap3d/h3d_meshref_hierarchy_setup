#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# filter items with zero transforms from selection

import modo
import modo.constants as c

from scripts.select_zero_transform_items import get_zero_items


def main():
    items = get_zero_items(modo.Scene().selectedByType(c.LOCATOR_TYPE, superType=True))

    modo.Scene().deselect()
    for item in items:
        item.select()


if __name__ == '__main__':
    main()
