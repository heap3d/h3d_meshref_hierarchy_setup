#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# load items info from file

import os

import modo
import modo.constants as c

from scripts.load_selected_item_info import (
    load_items_info, process_items, meshref_transform_to_locator, get_working_items,
    TOLERANCE, FULL_HIERARCHY,
)


def main():
    items: list[modo.Item] = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    if not items:
        return

    try:
        path = os.path.dirname(modo.Scene().filename)
    except TypeError:
        path = ''
    filename = modo.dialogs.fileOpen('text', path=path)
    if isinstance(filename, list):
        raise ValueError('Multiple files selected. Please select one file only.')
    if not filename:
        return

    items_info = load_items_info(filename)
    working_items = get_working_items(items, items_info)
    if not working_items:
        modo.dialogs.alert('Aborted', 'No info for items in the scene found.')
        return

    process_items(working_items, items_info, FULL_HIERARCHY)

    hierarchy_items: list[modo.Item] = items[:]
    for selected_item in items:
        if selected_item.parents:
            hierarchy_items.extend(selected_item.parents)
    meshref_transform_to_locator(hierarchy_items, TOLERANCE)


if __name__ == '__main__':
    main()
