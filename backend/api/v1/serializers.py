import base64

import webcolors
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import (BuyList, Favorites, Follow, Ingredient, Recipe,
                     RecipeIngredient, RecipeTag, Tag)

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
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' недопустимо"
            )
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
    username_validator = RegexValidator(
        regex=r'^\w[\w.@+-]*$',
        message="Имя должно соответствовать регулярному выражению")
    username = serializers.CharField(
        required=True, min_length=4, max_length=150,
        validators=[username_validator]
    )
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password], min_length=8
    )
    email = serializers.EmailField(required=True, max_length=150)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует."
            )
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


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous and request.user != obj:
            return Follow.objects.filter(
                user=request.user, following=obj
            ).exists()
        return False


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
        fields = ['id', 'amount', 'name']


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
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = serializers.IntegerField()

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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = RecipeTag
        fields = ('id', )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientDetailSerializer(
        source='recipeingredient_set', many=True, required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(
        max_length=None, use_url=True, required=False, allow_null=True
    )
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'tags', 'ingredients',
            'author', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        # Проверяем, есть ли рецепт в избранных у текущего пользователя
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorites.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        # Проверяем, есть ли рецепт в списке покупок у текущего пользователя
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return BuyList.objects.filter(recipe=obj, user=user).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id is not None and 'amount' in ingredient_data:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=ingredient_data['amount']
                )
            else:
                raise serializers.ValidationError(
                    "Each ingredient must have an id and an amount."
                )
        recipe.tags.set(tags_data)

        return recipe

    def to_representation(self, instance):
        """Переопределяем метод для кастомизации вывода данных."""
        representation = super().to_representation(instance)

        ingredients_representation = []
        for recipe_ingredient in instance.recipeingredient_set.all():
            ingredient = {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': (
                    recipe_ingredient.ingredient.measurement_unit
                ),
                'amount': recipe_ingredient.amount
            }
            ingredients_representation.append(ingredient)
        representation['ingredients'] = ingredients_representation

        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data

        return representation

    def update(self, instance, validated_data):
        if instance.author != self.context['request'].user:
            raise PermissionDenied(
                "You do not have permission to update this recipe."
            )

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if 'recipeingredient_set' in validated_data:
            ingredients_data = validated_data.pop('recipeingredient_set')
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id', None)
                if ingredient_id:
                    # ingredient, created =
                    # RecipeIngredient.objects.update_or_create(
                    RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        defaults={'amount': ingredient_data.get('amount', 0)}
                    )

        if 'tags' in validated_data:
            tag_ids = [tag.id for tag in validated_data['tags']]
            instance.tags.set(tag_ids)

        instance.save()
        return instance

    def validate(self, attrs):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {"error": "Field 'ingredients' is required."}
            )

        if not self.initial_data['ingredients']:
            raise serializers.ValidationError(
                {"error": "At least one ingredient is required."}
            )

        ingredient_ids = [
            ingredient['id'] for ingredient in self.initial_data['ingredients']
        ]
        if not Ingredient.objects.filter(pk__in=ingredient_ids).exists():
            raise serializers.ValidationError(
                {"error": "One or more ingredients do not exist."}
            )

        for ingredient in self.initial_data['ingredients']:
            if int(ingredient.get('amount', 0)) < 1:
                raise serializers.ValidationError(
                    {"error": "Amount of each ingredient must be at least 1."}
                )

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"error": "Duplicate ingredients are not allowed."}
            )

        # Проверка наличия поля 'tags'
        if 'tags' not in attrs:
            raise serializers.ValidationError(
                {"error": "Field 'tags' is required."}
            )

        # Проверка наличия тегов
        if not attrs['tags']:
            raise serializers.ValidationError(
                {"error": "Field 'tags' cannot be empty."}
            )

        # Проверка дублирования тегов
        tags_ids = [tag.id for tag in attrs['tags']]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(
                {"error": "Duplicate tags are not allowed."}
            )

        # Проверка наличия поля 'cooking_time'
        if 'cooking_time' not in attrs:
            raise serializers.ValidationError(
                {"error": "Field 'cooking_time' is required."}
            )

        # Проверка времени готовки
        cooking_time = attrs['cooking_time']
        if cooking_time == "":
            raise serializers.ValidationError(
                {"error": "Cooking time must be specified."}
            )
        if cooking_time < 1:
            raise serializers.ValidationError(
                {"error": "Cooking time cannot be less than 1 minute."}
            )

        if 'image' not in attrs:
            raise serializers.ValidationError(
                {"error": "Field 'image' is required."}
            )

        return attrs
