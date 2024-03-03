from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Tag, Recipe, Follow, Ingredient, BuyList
from django.contrib.auth.password_validation import validate_password


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

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=4, max_length=150)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], min_length=8)
    email = serializers.EmailField(required=True, max_length=150)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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