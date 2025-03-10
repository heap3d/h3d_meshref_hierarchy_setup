#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add a 'processed' mark to items

import modo
import re

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_utilites.scripts.h3d_debug import h3dd, prints


USERVAL_PATTERN = 'h3d_irr_pattern'
USERVAL_REPLACEMENT = 'h3d_irr_replacement'


def main():
    pattern = get_user_value(USERVAL_PATTERN)
    prints(pattern)
    if not pattern:
        return
    replace_str = get_user_value(USERVAL_REPLACEMENT)
    prints(replace_str)
    items = modo.Scene().selected
    for item in items:
        name = item.name
        if not name:
            continue
        new_name = re.sub(pattern, replace_str, name)
        item.name = new_name
        prints(new_name)


if __name__ == '__main__':
    h3dd.enable_debug_output(False)
    main()
