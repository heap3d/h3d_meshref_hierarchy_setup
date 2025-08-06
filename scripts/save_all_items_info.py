#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# save transform info for all meshref items to file

import modo
import modo.constants as c

from scripts.save_item_info import save_items_info


def main():
    items: list[modo.Item] = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)

    save_items_info(items)


if __name__ == '__main__':
    main()
