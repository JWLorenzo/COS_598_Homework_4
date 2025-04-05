# Terrain Enum
# If you want to add more terrain types, start here.
#
# Next jump to the params.py and game_map.py file to see how maps
# are generated.

import enum


class Terrain(enum.Enum):
    Forest = 1
    Desert = 2
    Mountain = 3
    Field = 4
    Hill = 5
    Pasture = 6
