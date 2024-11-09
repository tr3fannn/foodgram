from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from users.models import User


class UserSerializer(UserSerializer):
    """Сериализатор для получения списка
    пользователей и определенного пользователя"""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя"""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Создание пользователя"""

    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "password",
                  "username",
                  "first_name",
                  "last_name")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }