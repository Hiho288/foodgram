from collections import defaultdict

from django.contrib.auth.hashers import check_password
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet

from .models import BuyList, Favorites, Follow, Ingredient, Recipe, Tag, User
from .serializers import (BuyListSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          UserRegistrationSerializer, UserSerializer)


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
        required_fields = [
            'username', 'email',
            'password', 'first_name',
            'last_name'
        ]
        data = request.data

        # user = User.objects.get(username=request.data.username)
        if not all(field in data for field in required_fields):
            return Response(
                {"error": "Все поля обязательны к заполнению"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "email": user.email,
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        return Response({
            "email": user.email,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_subscribed": False
        })

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
        user = request.user
        recipe = get_object_or_404(Recipe, pk=id)

        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorites.objects.create(user=user, recipe=recipe)

        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=id)

        favorite = Favorites.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'errors': 'Рецепт не найден в избранном'},
                status=status.HTTP_404_NOT_FOUND
            )


# ПОДПИСКИ
class SubscriptionsAPIView(APIView):
    def get(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscribeAPIView(APIView):

    def post(self, request, id):
        user = request.user
        try:
            following = User.objects.get(pk=id)
            if user == following:
                return Response(
                    {'error': 'Нельзя подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            _, created = Follow.objects.get_or_create(
                user=user, following=following
            )
            if created:
                return Response(
                    {'status': 'subscribed'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'Уже подписаны.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, id):
        user = request.user
        try:
            following = User.objects.get(pk=id)
            subscription = Follow.objects.filter(
                user=user, following=following
            )
            if subscription.exists():
                subscription.delete()
                return Response(
                    {'status': 'unsubscribed'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error': 'Подписка не найдена.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )


# СПИСОК ИЛИ КОНКРЕТНЫЙ ИНГРИДИЕНТ
class IngredientAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id=None):
        if id:
            # Получение деталей ингредиента по ID
            ingredient = get_object_or_404(Ingredient, pk=id)
            serializer = IngredientSerializer(ingredient)
        else:
            # Получение списка всех ингредиентов с возможной фильтрацией
            name_start = request.query_params.get('name', None)
            ingredients = Ingredient.objects.all()
            if name_start is not None:
                ingredients = ingredients.filter(name__startswith=name_start)
            serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)


# СПИСОК ПОКУПОК
class BuyListAPIView(APIView):

    def post(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=id)

        if BuyList.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        BuyList.objects.create(user=user, recipe=recipe)

        serializer = BuyListSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=id)

        favorite = BuyList.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'errors': 'Рецепт не найден в списке покупок'},
                status=status.HTTP_404_NOT_FOUND
            )


# ЛИСТ ПОКУПОК
class DownloadShoppingCartAPIView(APIView):

    def get(self, request):
        user = request.user
        shopping_cart = BuyList.objects.filter(user=user)
        ingredients_sum = defaultdict(float)

        for item in shopping_cart:
            recipe_ingredients = Ingredient.objects.filter(recipe=item.recipe)
            for ri in recipe_ingredients:
                key = f"{ri.ingredient.name}({ri.ingredient.measurement_unit})"
                ingredients_sum[key] += ri.amount

        filename = "shopping_list.txt"
        content = "\n".join(
            [f"{key}: {amount}" for key, amount in ingredients_sum.items()]
        )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class RecipeViewSet(ViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        queryset = Recipe.objects.all()
        page_size = 6  # 6 рецептов на странице

        # kword limit
        limit = request.query_params.get('limit')
        if limit:
            try:
                page_size = int(limit)
            except ValueError:
                return Response(
                    {"error": "Limit must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # kword author
        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        # kword tags
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags)

        paginator = self.pagination_class()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(queryset, request)
        serializer = RecipeSerializer(
            page, many=True, context={'request': request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return Response({
            'count': paginator.page.paginator.count,
            'next': paginated_response.data.get('next'),
            'previous': paginated_response.data.get('previous'),
            'results': paginated_response.data.get('results')
        })

    def create(self, request):
        serializer = RecipeSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        queryset = Recipe.objects.all()
        recipe = get_object_or_404(queryset, pk=pk)
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        # print(recipe.author == request.user)
        if recipe.author != request.user:
            raise PermissionDenied(
                "You do not have permission to update this recipe."
            )

        serializer = RecipeSerializer(
            recipe, data=request.data,
            partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeSerializer(
            recipe, data=request.data,
            partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
