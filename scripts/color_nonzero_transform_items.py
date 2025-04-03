#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# color items with nonzero transforms

import lx

import scripts.select_nonzero_transform_items as select_nonzero_items


COLOR = 'yellow'


def main():
    select_nonzero_items.main()
    lx.eval(f'item.editorColor {COLOR}')


if __name__ == '__main__':
    main()
