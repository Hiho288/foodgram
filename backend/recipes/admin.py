from django.contrib import admin
from django.db.models import Count

from .models import (BuyList, Favorite, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, Tag)


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


class RecipeTagInLine(admin.TabularInline):
    model = RecipeTag
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
    inlines = (RecipeIngredientInline, RecipeTagInLine)

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


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(BuyList)
class BuyListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.empty_value_display = 'Не задано'
