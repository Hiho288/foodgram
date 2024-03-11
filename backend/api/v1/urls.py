from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteRecipeAPIView, SubscriptionsAPIView, SubscribeAPIView, IngredientAPIView, BuyListAPIView, DownloadShoppingCartAPIView, RecipeViewSet, UserViewSet, TagViewSet


router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    # Избранные
    path('recipes/<int:id>/favorite/', FavoriteRecipeAPIView.as_view(), name='recipe-favorite'),
    # Подписки
    path('users/subscriptions/', SubscriptionsAPIView.as_view(), name='user-subscriptions'),
    path('users/<int:id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    # Ингридиенты
    path('ingredients/', IngredientAPIView.as_view(), name='ingredient-list'),
    path('ingredients/<int:id>/', IngredientAPIView.as_view(), name='ingredient-detail'),
    # Список покупок
    path('recipes/<int:id>/shopping_cart/', BuyListAPIView.as_view(), name='recipe-favorite'),
    path('recipes/download_shopping_cart/', DownloadShoppingCartAPIView.as_view(), name='download-favorite'),
    # Рецепты
    # Пользователи
    path('', include(router.urls)),
]