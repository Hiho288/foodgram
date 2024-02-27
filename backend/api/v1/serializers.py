from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Tag, Recipe, Follow, Ingredient, BuyList

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        # Проверяем, что имя пользователя не является "me"
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя пользователя 'me' недопустимо")
        return value

    def validate(self, data):
        # Вы можете добавить дополнительные проверки полей здесь
        return data

    def create(self, validated_data):
        # Создание нового пользователя
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Обновление данных пользователя
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        new_password = validated_data.get('password')
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    following_username = serializers.ReadOnlyField(source='following.username')

    class Meta:
        model = Follow
        fields = ['user', 'following', 'following_username']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class BuyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'