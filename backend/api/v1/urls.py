from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartAPIView, FavoriteRecipeAPIView,
                    IngredientAPIView, RecipeViewSet, TagViewSet, UserViewSet)

router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientAPIView, basename='ingredients')


urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteRecipeAPIView.as_view(),
        name='recipe-favorite'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartAPIView.as_view(),
        name='download-favorite'
    ),
    path('', include(router.urls)),
]
