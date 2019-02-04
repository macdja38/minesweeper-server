from functools import partial


def is_set(bit, integer):
    """
    Checks if a specific bit is set in an integer
    :param bit: index of bit to check, 0 for rightmost bit, as number goes higher checks one more bit further left
    :param integer: integer to check the bit of
    :return: bool that's true if the bit is 1
    """
    mask = 1 << bit
    return integer & mask == mask


is_hidden = partial(is_set, 7)


def is_flagged(tile):
    return is_hidden(tile) and is_set(6, tile)


is_bomb = partial(is_set, 5)


def set_bit(bit, value, tile=0):
    mask = 1 << bit
    if value:
        return mask | tile
    return (~mask) & tile


set_hidden = partial(set_bit, 7)
set_flagged = partial(set_bit, 6)
set_bomb = partial(set_bit, 5)
