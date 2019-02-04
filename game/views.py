from game.models.game import Game
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from game.serializers import GameSerializer, GameSerializerWithReadOnlyDimensions, MoveSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.


class GameViewSet(viewsets.ModelViewSet):
    """
    API for Games
    """
    queryset = Game.objects.all().order_by('-id')
    serializer_class = GameSerializer

    @action(methods=['post'], detail=True)
    def flag(self, request, pk):
        game = self.get_object()
        serializer = MoveSerializer(data=request.data)
        if not (game.game_state == 'S' or game.game_state == 'C'):
            return Response({'status': 'Cannot update completed game'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            game.flag(serializer.validated_data.get('x'), serializer.validated_data.get('y'))
            game.save()
            return Response(GameSerializer(game).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def reveal(self, request, pk):
        game = self.get_object()
        serializer = MoveSerializer(data=request.data)
        if not (game.game_state == 'S' or game.game_state == 'C'):
            return Response({'status': 'Cannot update completed game'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            game.reveal(serializer.validated_data.get('x'), serializer.validated_data.get('y'))
            game.save()
            return Response(GameSerializer(game).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        print('Get Serializer Class called')
        serializer_class = self.serializer_class

        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = GameSerializerWithReadOnlyDimensions

        return serializer_class

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method == 'POST':
            return [AllowAny()]
        else:
            return [AllowAny()]
