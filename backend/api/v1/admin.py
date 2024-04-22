from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import Ingredient, Recipe, RecipeIngredient, Tag, User


class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'is_staff', 'get_follower_count',
        'get_recipe_count'
    )

    @admin.display(description='Количество подписчиков')
    def follower_count(self, obj):
        return obj.get_follower_count()

    @admin.display(description='Количество рецептов')
    def recipe_count(self, obj):
        return obj.get_recipe_count()


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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'cooking_time',
        'favorites_count', 'ingredient_list',
        'tag_list'
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorites_count=Count('favorites'))
        return queryset

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.admin_order_field = 'favorites_count'

    @admin.display(description='Ингредиенты')
    def ingredient_list(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='Теги')
    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])


admin.site.empty_value_display = 'Не задано'

admin.site.register(User, UserAdmin)
