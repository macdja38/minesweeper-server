from game.models import Game
from rest_framework import viewsets, status
from game.serializers import GameSerializer, MoveSerializer
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
        if not game.game_state == 'S':
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
        if not game.game_state == 'S':
            return Response({'status': 'Cannot update completed game'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            game.reveal(serializer.validated_data.get('x'), serializer.validated_data.get('y'))
            game.save()
            return Response(GameSerializer(game).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
