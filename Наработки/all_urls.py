from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .all_views import FavoriteRecipeAPIView, SubscriptionsAPIView, SubscribeAPIView, IngredientAPIView, BuyListAPIView, DownloadShoppingCartAPIView, RecipeViewSet


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    # Рецепты
    path('api/', include(router.urls)),
    # Избранные
    path('api/recipes/<int:id>/favorite/', FavoriteRecipeAPIView.as_view(), name='recipe-favorite'),
    # Подписки
    path('api/users/subscriptions/', SubscriptionsAPIView.as_view(), name='user-subscriptions'),
    path('api/users/<int:id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    # Ингридиенты
    path('api/ingredients/', IngredientAPIView.as_view(), name='ingredient-list'),
    path('api/ingredients/<int:id>/', IngredientAPIView.as_view(), name='ingredient-detail'),
    # Список покупок
    path('api/recipes/<int:id>/shopping_cart/', BuyListAPIView.as_view(), name='recipe-favorite'),
    path('api/recipes/download_shopping_cart/', DownloadShoppingCartAPIView.as_view(), name='download-favorite'),
]
