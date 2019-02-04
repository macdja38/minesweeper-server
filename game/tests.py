from django.test import TestCase
from game.models.game import Game
from game.models.helpers.bitwise_operations import is_hidden, is_flagged, is_bomb, set_hidden, set_flagged, set_bomb


class TestBitwise(TestCase):
    def test_setting_flags(self):
        """Bitwise flag manipulation"""
        tile = 0
        tile = set_hidden(True, tile)
        self.assertEqual(tile, 128)
        tile = set_hidden(False, tile)
        self.assertEqual(tile, 0)
        tile = set_bomb(True, tile)
        self.assertEqual(tile, 32)
        tile = set_hidden(True, tile)
        self.assertEqual(tile, 160)
        tile = set_hidden(False, tile)
        self.assertEqual(tile, 32)
        tile = set_bomb(False, tile)
        self.assertEqual(tile, 0)

    def test_set_flagged(self):
        self.assertEqual(set_flagged(True, 0), 64)
        self.assertEqual(set_flagged(False, 255), 191)
        self.assertEqual(set_flagged(True, 255), 255)
        self.assertEqual(set_flagged(False, 0), 0)

    def test_is_hidden(self):
        self.assertEqual(is_hidden(255), True)
        self.assertEqual(is_hidden(128), True)
        self.assertEqual(is_hidden(127), False)
        self.assertEqual(is_hidden(0), False)

    def test_is_flagged(self):
        self.assertEqual(is_flagged(255), True)
        self.assertEqual(is_flagged(64), False)  # Notable exception, must be hidden to have a flag
        self.assertEqual(is_flagged(192), True)
        self.assertEqual(is_flagged(191), False)
        self.assertEqual(is_flagged(0), False)
        
    def test_is_bomb(self):
        self.assertEqual(is_bomb(255), True)
        self.assertEqual(is_bomb(32), True)
        self.assertEqual(is_bomb(223), False)
        self.assertEqual(is_bomb(0), False)


class GameTestCase(TestCase):
    def setUp(self):
        Game.objects.create(id=1)

    def test_game_has_bombs(self):
        """Animals that can speak are correctly identified"""
        game = Game.objects.get(id=1)
        self.assertEqual(game.bombs, 9)

    def test_client_data_starts_hidden(self):
        """Animals that can speak are correctly identified"""
        game = Game.objects.get(id=1)

        tiles = 0
        for row in game.client_state:
            for tile in row:
                self.assertEqual(tile, 128)
                tiles += 1

        self.assertEqual(tiles, 64)
