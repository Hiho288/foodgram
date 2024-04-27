from collections import defaultdict

from django.contrib.auth.hashers import check_password
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (BuyList, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .paginators import RecipePaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (BuyListSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeShortSerializer,
                          RecipeWriteSerializer, SubscribeSerializer,
                          TagSerializer, UserRegistrationSerializer,
                          UserSerializer)


def post_method(request, recipe_id, model, model_serializer):
    user = request.user

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
    except Recipe.DoesNotExist:
        return Response(
            {'errors': 'Рецепт не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            {'errors': 'Рецепт уже в списке покупок или в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)

    serializer = model_serializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_method(request, recipe_id, model):
    user = request.user
    try:
        recipe = Recipe.objects.get(pk=recipe_id)
    except Recipe.DoesNotExist:
        return Response(
            {'errors': 'Рецепт не существует'},
            status=status.HTTP_404_NOT_FOUND
        )
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

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserSerializer
        return UserRegistrationSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        following_id = self.kwargs.get('pk')
        following = get_object_or_404(User, id=following_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                following, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = Follow.objects.get(
                    user=user, following=following
                )
            except Follow.DoesNotExist:
                return Response(
                    {'errors': 'Пользователь не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = (User.objects
                    .filter(following__user=user)
                    .annotate(recipes_count=Count('recipes')))
        limit = request.query_params.get('limit', None)
        if limit is not None:
            self.paginator.default_limit = int(limit)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class FavoriteRecipeAPIView(APIView):

    def post(self, request, recipe_id):
        return post_method(
            request,
            recipe_id=recipe_id,
            model=Favorite,
            model_serializer=FavoriteSerializer
        )

    def delete(self, request, recipe_id):
        return delete_method(request, recipe_id=recipe_id, model=Favorite)


# ПОДПИСКИ
class SubscriptionsAPIView(APIView):
    def get(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = FollowSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# СПИСОК ИЛИ КОНКРЕТНЫЙ ИНГРИДИЕНТ
class IngredientAPIView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


# СПИСОК ПОКУПОК
class BuyListAPIView(APIView):
    def post(self, request, recipe_id):
        serializer = BuyListSerializer(
            data={'recipe_id': recipe_id, 'user_id': request.user.id}
        )
        if serializer.is_valid():
            serializer.save()
            recipe = Recipe.objects.get(id=recipe_id)
            serialized_recipe = RecipeShortSerializer(recipe)
            return Response(
                serialized_recipe.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


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
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = RecipePaginator
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self.filter_class(
            self.request.GET, queryset=queryset, request=self.request
        ).qs
        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, *args, **kwargs):
        user = self.request.user
        if self.request.method == 'POST':
            recipe_id = self.kwargs['pk']
            if BuyList.objects.filter(recipe_id=recipe_id, user=user).exists():
                return Response(
                    {'errors': 'Рецепт уже был добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                recipe = Recipe.objects.get(id=recipe_id)
                BuyList.objects.create(recipe=recipe, user=user)
                serializer = RecipeShortSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except Recipe.DoesNotExist:
                return Response(
                    {'error': 'Рецепт не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        obj = BuyList.objects.filter(recipe_id=self.kwargs['pk'], user=user)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт не существует или был удален'},
            status=status.HTTP_404_NOT_FOUND
        )
