#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy unparent tool to prepare current file
# to use as meshref without destroying hierarchy
# - saves locators hierarchy into a new modo scene
# - flattens mesh items hierarchy and saves it to a new modo scene
# usage:
# 1. remove unnecessary elements from hierarchy
# 2. select hierarchy root item
# 3. run unparent hierarchy command


import modo
import modo.constants as c


def normalize_hierarchy(root: modo.Item) -> modo.Item:
    ...


def unparent_hierarchy(root: modo.Item) -> set[modo.Item]:
    ...


def main() -> None:
    items: set[modo.Item] = set(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))
    roots: set[modo.Item] = {i for i in items if not i.parents}
    hierarchies: set[modo.Item] = {i for i in roots if i.children}

    normalized_hierarchies: set[modo.Item] = set()
    for hierarchy in hierarchies:
        normalized_hierarchies.add(normalize_hierarchy(hierarchy))

    flattened_hierarchy_items: set[modo.Item] = set()
    for normalized_hierarchy in normalized_hierarchies:
        flattened_hierarchy_items.union(unparent_hierarchy(normalized_hierarchy))

    # todo save normalized hierarchies to hierarchy scene
    # todo rescan root items and add items without children to flattened hierarchy items collection
    # todo flattened hierarchy items save to flattened scene


if __name__ == "__main__":
    main()
