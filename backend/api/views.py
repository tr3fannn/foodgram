import drf_yasg.utils
from api.filters import IngredientSearchFilter, RecipesFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (FollowSerializer,
                             IngredientSerializer,
                             RecipeFavoritesSerializer,
                             RecipeSerializer,
                             ShoppingListSerializer,
                             TagSerializer
                             )
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from recipes.models import (CustomUser,
                            Follow,
                            Ingredient,
                            IngredientRecipes,
                            Recipe,
                            RecipeFavorites,
                            ShoppingList,
                            Tag
                            )
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Тег
    Получение списка тегов /
    конкретного тега
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet Ингредиенты
    Получение списка ингредиентов /
    конкретного ингредиента
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [IngredientSearchFilter]
    search_fields = ["^name"]


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_description="""
    #### Пример создания рецепта
    ```
    {
        "ingredients": [
            {
                "id": 1123,
                "amount": 10
            },
            {
                "id": 1124,
                "amount": 20
            }
        ],
        "tags": [
            1,
            2
        ],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg
        MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4
        bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
        "name": "string",
        "text": "string",
        "cooking_time": 1
    }
    ```
    """
    ),
)
class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet Рецепт
    Получение списка рецептов /
    конкретного рецепта /
    создание, редактирование /
    удаление рецепта
    """

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipesFilter
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["GET"], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        shopping_result = {}
        ingredients = IngredientRecipes.objects.filter(
            recipes__shoppinglist__user=request.user
        ).values_list("ingredients__name",
                      "ingredients__measurement_unit",
                      "amount")

        for ingredient in ingredients:
            name = ingredient[0]
            if name not in shopping_result:
                shopping_result[name] = {
                    "measurement_unit": ingredient[1],
                    "amount": ingredient[2],
                }
            else:
                shopping_result[name]["amount"] += ingredient[2]

        shopping_itog = (
            f"{name} - {value['amount']} " f"{value['measurement_unit']}\n"
            for name, value in shopping_result.items()
        )
        response = HttpResponse(shopping_itog, content_type="text/plain")
        response["Content-Disposition"] = \
            'attachment; filename="shoppinglist.txt"'
        return response


class RecipeFavoritesViewSet(viewsets.ModelViewSet):
    """ViewSet Списки избранных рецептов
    Добавление /
    удаление из списка
    """

    serializer_class = RecipeFavoritesSerializer
    queryset = RecipeFavorites.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=drf_yasg.utils.no_body)
    def create(self, request, *args, **kwargs):
        """Добавление рецепта
        в список избранного
        """
        recipes_id = self.kwargs["id"]
        recipes = get_object_or_404(Recipe, id=recipes_id)
        RecipeFavorites.objects.create(user=request.user, recipes=recipes)
        serializer = RecipeFavoritesSerializer()
        return Response(
            serializer.to_representation(instance=recipes),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта
        из списка избранного
        """
        recipes_id = self.kwargs["id"]
        user_id = request.user.id
        RecipeFavorites.objects.filter(
            user__id=user_id, recipes__id=recipes_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet Подписки
    Cоздание подписки /
    удаление подписки
    """

    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=drf_yasg.utils.no_body)
    def create(self, request, *args, **kwargs):
        """Создание подписки"""
        user_id = self.kwargs["id"]
        user = get_object_or_404(CustomUser, id=user_id)
        subscribe = Follow.objects.create(user=request.user, author=user)
        serializer = FollowSerializer(subscribe, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаление подписки"""
        author_id = self.kwargs["id"]
        user_id = request.user.id
        Follow.objects.filter(user_id, author_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingViewSet(viewsets.ModelViewSet):
    """ViewSet Список покупок
    Добавление рецепта в список покупок /
    удаление рецепта из списка покупок /
    скачивание списка покупок
    """

    serializer_class = ShoppingListSerializer
    pagination_class = CustomPagination
    queryset = ShoppingList.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=drf_yasg.utils.no_body)
    def create(self, request, *args, **kwargs):
        """Добавление рецепта в
        список покупок
        """
        recipe_id = self.kwargs["id"]
        recipes = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.create(user=request.user, recipes=recipes)
        serializer = ShoppingListSerializer()
        return Response(
            serializer.to_representation(instance=recipes),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта из
        списка покупок
        """
        recipe_id = self.kwargs["id"]
        user_id = request.user.id
        ShoppingList.objects.filter(user__id=user_id,
                                    recipes__id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
