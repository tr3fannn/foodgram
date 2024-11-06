from api.pagination import CustomPagination
from api.serializers import FollowSerializer
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSet(UserViewSet):
    """ViewSet пользователя
    Получение списка пользователей /
    Получение определенного пользователя /
    Создание, обновление /
    удаление определенного пользователя /
    изменение пароля /
    получение текущего пользователя/
    просмотр подписок пользователя
    """

    pagination_class = CustomPagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Просмотр подписок пользователя"""
        queryset = self.request.user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={"request": request})
        return self.get_paginated_response(serializer.data)