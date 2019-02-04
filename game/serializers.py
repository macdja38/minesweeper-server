from game.models.game import Game
from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.permissions import IsAdminUser, AllowAny


class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'height', 'width', 'start_time', 'end_time', 'client_state', 'game_state', 'bombs')


class GameSerializerWithReadOnlyDimensions(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'height', 'width', 'start_time', 'end_time', 'client_state', 'game_state', 'bombs')
    width = serializers.IntegerField(
        read_only=True,
        default=serializers.CreateOnlyDefault(8)
    )
    height = serializers.IntegerField(
        read_only=True,
        default=serializers.CreateOnlyDefault(8)
    )


class MoveSerializer(serializers.Serializer):
    x = serializers.IntegerField(validators=[
        MaxValueValidator(32),
        MinValueValidator(0)
    ])
    y = serializers.IntegerField(validators=[
        MaxValueValidator(32),
        MinValueValidator(0)
    ])
