from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from game.models.helpers.bitwise_operations import is_hidden, is_flagged, is_bomb, set_hidden, set_flagged, set_bomb
import math
import random


def extract_adjacent(tile):
    return tile & 0b1111


def set_adjacent(value, tile=0):
    if value > 0b1111:
        raise ValueError("tile being set must be a maximum of 4 bits")
    return (value & 0b1111) + (tile & (~0b1111))


def create_tile(hidden, flagged, bomb, number=0):
    return set_hidden(hidden) + set_flagged(flagged) + set_bomb(bomb) + number


# Create your models here.


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


def generate_game(width, height, density=0.15):
    grid = []
    tiles_total = width * height
    tiles_remaining = tiles_total
    bombs_remaining = math.floor(density * width * height)

    # Place bombs on the grid
    for y in range(0, height):
        row = []
        for x in range(0, width):
            bomb = False
            if random.uniform(0, 1) < bombs_remaining / tiles_remaining:
                bomb = True
            row.append(create_tile(True, False, bomb))
            if bomb:
                bombs_remaining -= 1
            tiles_remaining -= 1
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


def generate_serialized_game_with_defaults():
    # making this a  lambda causes django's migrations to fail
    return serialize_game(generate_game(8, 8, 0.15))


class Game(models.Model):
    GAME_STATES = (
        ('S', 'Started'),
        ('W', 'Won'),
        ('L', 'Lost'),
    )
    game_state = models.CharField(max_length=1, choices=GAME_STATES, default='S')
    start_time = models.DateTimeField(auto_now_add=True, editable=False)
    # 255 is the largest number a tile can have
    # comma separated values means 4 chars per tile.
    # (This could be cut down to 2 chars with hex, at the cost of complexity)
    # 32 is the max field size, 32 * 32 * 4 = 4096
    state = models.CharField(default=generate_serialized_game_with_defaults,
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

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["height", "category", "state", "start_time", "id"]
        else:
            return ["start_time", "state", "id"]

    def reveal(self, x, y):
        grid = deserialize_game(self.state, self.width, self.height)
        tile = grid[y][x]
        bomb = is_bomb(tile)
        hidden = is_hidden(tile)

        if not hidden:
            raise ValueError('Cannot reveal a tile that is not hidden')
        grid[y][x] = set_hidden(False, tile)
        self.state = serialize_game(grid)

        if bomb:
            self.game_state = 'L'
        else:
            if count_hidden(grid) == self.bombs:
                self.game_state = 'W'

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

        # x is horizontal, y is vertical, top left is 0, 0
        for y in range(0, height):
            row = []
            for x in range(0, width):
                row.append(mask_hidden_data(flat_tiles.pop()))
            client_state.append(row)

        return client_state
