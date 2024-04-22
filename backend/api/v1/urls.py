from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BuyListAPIView, DownloadShoppingCartAPIView,
                    FavoriteRecipeAPIView, IngredientAPIView, RecipeViewSet,
                    SubscribeAPIView, SubscriptionsAPIView, TagViewSet,
                    UserViewSet)

router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    # Избранные
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteRecipeAPIView.as_view(),
        name='recipe-favorite'
    ),
    # Подписки
    path(
        'users/subscriptions/',
        SubscriptionsAPIView.as_view(),
        name='user-subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeAPIView.as_view(),
        name='subscribe'
    ),
    # Ингридиенты
    path('ingredients/', IngredientAPIView, name='ingredient-list'),
    path(
        'ingredients/<int:ingredient_id>/',
        IngredientAPIView,
        name='ingredient-detail'
    ),
    # Список покупок
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        BuyListAPIView.as_view(),
        name='recipe-favorite'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartAPIView.as_view(),
        name='download-favorite'
    ),
    # Рецепты
    # Пользователи
    path('', include(router.urls)),
]
