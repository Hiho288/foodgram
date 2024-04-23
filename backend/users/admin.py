from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


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


admin.site.empty_value_display = 'Не задано'

admin.site.register(User, UserAdmin)
