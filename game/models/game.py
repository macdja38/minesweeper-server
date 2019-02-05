import math
import random
import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from game.models.helpers.bitwise_operations import is_hidden, is_flagged, is_bomb, set_hidden, set_flagged, set_bomb
from django.db.models.signals import pre_save
from django.dispatch import receiver


def extract_adjacent(tile):
    return tile & 0b1111


def set_adjacent(value, tile=0):
    if value > 0b1111:
        raise ValueError("tile being set must be a maximum of 4 bits")
    return (value & 0b1111) + (tile & (~0b1111))


def create_tile(hidden, flagged, bomb, number=0):
    return set_hidden(hidden) + set_flagged(flagged) + set_bomb(bomb) + (number & 0b1111)


def mask_hidden_data(tile):
    hidden = is_hidden(tile)
    flagged = is_flagged(tile)
    bomb = is_bomb(tile)
    adjacent = extract_adjacent(tile)

    if hidden:
        return create_tile(hidden, flagged, False, False)
    else:
        return create_tile(hidden, False, bomb, adjacent)


def count_hidden(grid):
    count = 0
    for row in grid:
        for tile in row:
            if is_hidden(tile):
                count += 1

    return count


def generate_game(grid, width, height, clicked_x, clicked_y, density=0.15):
    tiles_total = width * height
    tiles_remaining = tiles_total
    bombs_remaining = math.floor(density * width * height) - 1

    # Place bombs on the grid
    for y in range(0, height):
        row = []
        for x in range(0, width):
            tile = grid[y][x]
            if not (y == clicked_y and x == clicked_x):
                bomb = False
                if random.uniform(0, 1) < bombs_remaining / tiles_remaining:
                    bomb = True
                grid[y][x] = create_tile(True, is_flagged(tile), bomb)
                if bomb:
                    bombs_remaining -= 1
                tiles_remaining -= 1
            else:
                grid[y][x] = create_tile(True, False, False)
        grid.append(row)

    # Count bombs adjacent to each square
    for y in range(0, height):
        for x in range(0, width):
            tile = grid[y][x]
            bomb = is_bomb(tile)
            if not bomb:
                count = 0
                for y_offset in range(-1, 2):
                    y_probe = y + y_offset
                    if 0 <= y_probe < height:
                        for x_offset in range(-1, 2):
                            x_probe = x + x_offset
                            if 0 <= x_probe < width:
                                if is_bomb(grid[y_probe][x_probe]):
                                    count += 1
                grid[y][x] = set_adjacent(count, tile)

    return grid


def generate_empty_game(width, height):
    grid = []

    # Place bombs on the grid
    for y in range(0, height):
        row = []
        for x in range(0, width):
            row.append(create_tile(True, False, False))
        grid.append(row)

    return grid


def propagate_unhide(grid, width, height):
    modified = 0
    for y in range(0, height):
        for x in range(0, width):
            tile = grid[y][x]
            if not is_hidden(tile) and not is_bomb(tile) and extract_adjacent(tile) == 0:
                for y_offset in range(-1, 2):
                    y_probe = y + y_offset
                    if 0 <= y_probe < height:
                        for x_offset in range(-1, 2):
                            x_probe = x + x_offset
                            if 0 <= x_probe < width:
                                tile_probe = grid[y_probe][x_probe]
                                if is_hidden(tile_probe):
                                    grid[y_probe][x_probe] = set_hidden(False, tile_probe)
                                    modified += 1

    if modified > 0:
        return propagate_unhide(grid, width, height)
    return grid


def serialize_game(grid):
    return ','.join([str(item) for sublist in grid for item in sublist])


def deserialize_game(string, width, height):
    flat_tiles = [int(tile) for tile in string.split(',')][::-1]

    client_state = []

    # x is horizontal, y is vertical, top left is 0, 0
    for y in range(0, height):
        row = []
        for x in range(0, width):
            row.append(flat_tiles.pop())
        client_state.append(row)

    return client_state


class Game(models.Model):
    GAME_STATES = (
        ('C', 'Created'),
        ('S', 'Started'),
        ('W', 'Won'),
        ('L', 'Lost'),
    )
    game_state = models.CharField(max_length=1, editable=False, choices=GAME_STATES, default='C')
    start_time = models.DateTimeField(null=True, editable=False)
    end_time = models.DateTimeField(null=True, editable=False)
    # 255 is the largest number a tile can have
    # comma separated values means 4 chars per tile.
    # (This could be cut down to 2 chars with hex, at the cost of complexity)
    # 32 is the max field size, 32 * 32 * 4 = 4096
    state = models.CharField(default="",
                             editable=False,
                             max_length=4096)
    height = models.IntegerField(default=8,
                                 validators=[
                                     MaxValueValidator(32),
                                     MinValueValidator(8)
                                 ])
    width = models.IntegerField(default=8,
                                validators=[
                                    MaxValueValidator(32),
                                    MinValueValidator(8)
                                ])

    def reveal(self, x, y):
        grid = deserialize_game(self.state, self.width, self.height)

        if self.game_state == "C":
            grid = generate_game(grid, self.width, self.height, x, y, 0.15)
            self.start_time = datetime.datetime.utcnow()
            self.game_state = "S"

        tile = grid[y][x]
        bomb = is_bomb(tile)
        hidden = is_hidden(tile)

        if not hidden:
            raise ValueError('Cannot reveal a tile that is not hidden')
        grid[y][x] = set_hidden(False, tile)
        grid = propagate_unhide(grid, self.width, self.height)
        self.state = serialize_game(grid)

        if bomb:
            self.game_state = 'L'
            self.end_time = datetime.datetime.utcnow()
        else:
            if count_hidden(grid) == self.bombs:
                self.game_state = 'W'
                self.end_time = datetime.datetime.utcnow()

    def flag(self, x, y):
        grid = deserialize_game(self.state, self.width, self.height)
        tile = grid[y][x]
        hidden = is_hidden(tile)
        flagged = is_flagged(tile)

        if not hidden:
            raise ValueError('Cannot flag a tile that is not hidden')
        grid[y][x] = set_flagged(not flagged, tile)
        self.state = serialize_game(grid)

    @property
    def bombs(self):
        """
        Returns a representation of the state that is scrubbed of information that the client does not need to know
        :return: array of arrays, first index is vertical, second is horizontal, values are tile values
        """
        # removing from the end of a list is easier / faster in python, so we reverse the list then pop

        flat_tiles = [int(tile) for tile in self.state.split(',')]
        count = 0

        # x is horizontal, y is vertical, top left is 0, 0
        for tile in flat_tiles:
            if is_bomb(tile):
                count += 1

        return count

    @property
    def client_state(self):
        """
        Returns a representation of the state that is scrubbed of information that the client does not need to know
        :return: array of arrays, first index is vertical, second is horizontal, values are tile values
        """
        # removing from the end of a list is easier / faster in python, so we reverse the list then pop

        flat_tiles = [int(tile) for tile in self.state.split(',')][::-1]

        width = self.width
        height = self.height

        client_state = []

        mask_hidden = not (self.game_state == 'W' or self.game_state == 'L')

        # x is horizontal, y is vertical, top left is 0, 0
        for y in range(0, height):
            row = []
            for x in range(0, width):
                if mask_hidden:
                    row.append(mask_hidden_data(flat_tiles.pop()))
                else:
                    row.append(flat_tiles.pop())
            client_state.append(row)

        return client_state


@receiver(pre_save, sender=Game)
def my_callback(sender, instance, *args, **kwargs):
    if instance.state == "":
        instance.state = serialize_game(generate_empty_game(instance.width, instance.height))
