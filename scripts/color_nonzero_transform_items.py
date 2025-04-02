#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# color items with nonzero transforms

import lx
import modo

from scripts.select_nonzero_transform_items import get_nonzero_items


COLOR = 'yellow'


def main():
    nonzero_items = get_nonzero_items(modo.Scene())
    if not nonzero_items:
        return

    modo.Scene().deselect()
    for item in nonzero_items:
        item.select()

    lx.eval(f'item.editorColor {COLOR}')


if __name__ == '__main__':
    main()
