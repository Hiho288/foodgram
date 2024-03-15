from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag, Favorites, Follow, BuyList, User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

# User = get_user_model()
# Предполагаем, что модели и get_user_model уже импортированы

# Раскомментируйте и настройте класс UserAdmin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0

# Нет необходимости в RecipeTagInline, если у вас нет отдельной модели для связи рецептов и тегов
# и если используется ManyToManyField в модели Recipe

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorites_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorites_count=Count('favorites'))
        return queryset

    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.admin_order_field = 'favorites_count'
    favorites_count.short_description = 'В избранном'

# Остальные классы Admin для Favorites, Follow, BuyList уже соответствуют требованиям

admin.site.empty_value_display = 'Не задано'
