from collections import defaultdict

from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import (BuyList, Favorite, Follow, Recipe, RecipeIngredient, Tag,
                     User)
from .paginators import RecipePaginator
from .serializers import (BuyListSerializer, FavoriteSerializer,
                          FollowSerializer, RecipeReadSerializer,
                          TagSerializer, UserSerializer)


def post_method(request, recipe_id, model, model_serializer):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            {'errors': 'Рецепт уже в списке покупок или в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)

    serializer = model_serializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_method(request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=id)

    favorite = model.objects.filter(user=user, recipe=recipe)
    if favorite.exists():
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(
            {'errors': 'Рецепт не найден'},
            status=status.HTTP_404_NOT_FOUND
        )


class TagViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class UserViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        data = request.data
        new_password = data.get('new_password')
        current_password = data.get('current_password')

        # Проверяем, соответствует ли текущий пароль введенному паролю
        if not check_password(current_password, user.password):
            return Response(
                "Текущий пароль неверен",
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            "Пароль успешно изменен",
            status=status.HTTP_204_NO_CONTENT
        )


class FavoriteRecipeAPIView(APIView):

    def post(self, request, id):
        return post_method(model=Favorite, model_serializer=FavoriteSerializer)

    def delete(self, request, id):
        return delete_method(model=Favorite)


# ПОДПИСКИ
class SubscriptionsAPIView(APIView):
    def get(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscribeAPIView(APIView):

    def post(self, request, user_id):
        user = request.user
        following = User.objects.get(pk=user_id)
        if Follow.objects.filter(user=user, following=following).exists():
            raise ValidationError('Уже подписаны.')

        Follow.objects.create(user=user, following=following)
        return Response(
            {'detail': 'Подписка успешно создана.'},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, user_id):
        user = request.user
        following = User.objects.get(pk=user_id)
        subscription = Follow.objects.filter(user=user, following=following)
        if subscription.exists():
            subscription.delete()
            return Response(
                {'detail': 'Подписка удалена.'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )


# СПИСОК ИЛИ КОНКРЕТНЫЙ ИНГРИДИЕНТ
class IngredientAPIView(ModelViewSet):
    permission_classes = [AllowAny]
    filter_class = IngredientFilter


# СПИСОК ПОКУПОК
class BuyListAPIView(APIView):

    def post(self, request, id):
        return post_method(model=BuyList, model_serializer=BuyListSerializer)

    def delete(self, request, id):
        return delete_method(model=BuyList)


# ЛИСТ ПОКУПОК
class DownloadShoppingCartAPIView(APIView):

    def get(self, request):
        user = request.user
        shopping_cart = BuyList.objects.filter(
            user=user
        ).select_related('recipe')
        ingredients_sum = defaultdict(float)

        for item in shopping_cart:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=item.recipe
            ).select_related('ingredient')
            for ingredient in recipe_ingredients:
                ingredients_sum[
                    ingredient.ingredient.name
                ] += ingredient.amount

        filename = "shopping_list.txt"
        content = "\n".join(
            [f"{key}: {amount}" for key, amount in ingredients_sum.items()]
        )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    filter_class = RecipeFilter
    pagination_class = RecipePaginator
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        queryset = Recipe.objects.all()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(
            page, many=True, context={'request': request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response
