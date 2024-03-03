from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag, Favorites, Follow, BuyList

# class RecipeTagInline(admin.StackedInline):
#     model = RecipeTag
#     extra = 0

User = get_user_model()

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     pass

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'created')
    list_filter = ('author', 'name') #'tags'
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (RecipeIngredientInline, RecipeTagInline)

@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user__username', 'following__username')

@admin.register(BuyList)
class BuyListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')





# class RecipeAdmin(admin.ModelAdmin):
#     inlines = (
#         RecipeTagInline,
#     )

#     list_display = (
#             'author',
#             'name',
#             'image',
#             'text',
#             # 'ingredients',
#             # 'tag',
#             'cooking_time',
#             'created',
#         )
#     # filter_horizontal = ('tag',)



admin.site.empty_value_display = 'Не задано'

# admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
# admin.site.register(Ingredient, IngredientAdmin)