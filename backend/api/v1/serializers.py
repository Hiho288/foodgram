from rest_framework import serializers

import base64
import webcolors

from django.contrib.auth import get_user_model

from .models import Tag, Recipe, Follow, Ingredient, BuyList, RecipeIngredient, RecipeTag
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile

User = get_user_model()

class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # Find the start of the base64 string
            header, base64_data = data.split(';base64,')
            # Decode the base64 string
            decoded_file = base64.b64decode(base64_data)
            # Create a Django ContentFile
            file_name = 'uploaded_image.jpg'  # You might want to generate a unique name for each file
            data = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя пользователя 'me' недопустимо")
        return value

    def validate(self, data):
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
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

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
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

class BuyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'name'] #


User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class IngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField()
    ingredient = IngredientDetailSerializer(read_only=True)


    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'ingredient')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient_representation = representation.pop('ingredient')
        for key, value in ingredient_representation.items():
            representation[key] = value
        return representation

class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeTag
        fields = ('id', )

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientDetailSerializer(source='recipeingredient_set', many=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None, use_url=True, required=False, allow_null=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'tags', 'ingredients', 'author', 'text', 'cooking_time', 'created']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data, author=self.context['request'].user)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id is not None and 'amount' in ingredient_data:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=ingredient_data['amount']
                )
            else:
                raise serializers.ValidationError("Each ingredient must have an id and an amount.")
        recipe.tags.set(tags_data)

        return recipe
    
    def to_representation(self, instance):
        """Переопределяем метод для кастомизации вывода данных."""
        ret = super().to_representation(instance)
        ret['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return ret
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        if 'recipeingredient_set' in validated_data:
            ingredients_data = validated_data.pop('recipeingredient_set')
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id', None)
                if ingredient_id:
                    ingredient, created = RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        defaults={'amount': ingredient_data.get('amount', 0)}
                    )

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags', [])
            instance.tags.set(Tag.objects.filter(id__in=[tag['id'] for tag in tags_data]))

        instance.save()
        return instance