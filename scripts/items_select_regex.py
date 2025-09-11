#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select items using regex pattern

import modo
import modo.constants as c
import re

from h3d_utilites.scripts.h3d_utils import get_user_value


USERVAL_PATTERN = 'h3d_irr_pattern'


def main():
    pattern = get_user_value(USERVAL_PATTERN)
    if not pattern:
        return
    items = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    matched_items = []
    for item in items:
        name = item.name
        if not name:
            continue
        if re.search(pattern, name):
            matched_items.append(item)

    modo.Scene().deselect()
    for item in matched_items:
        item.select()


if __name__ == '__main__':
    main()
