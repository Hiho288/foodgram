from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from foodgram_backend.constants import MAX_REGISTRATION_LENGTH
from recipes.models import (BuyList, Favorite, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag)
from users.models import Follow, User

from .fields import Base64ImageField, Hex2NameColor


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'password', 'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        required_fields = [
            'username', 'email',
            'password', 'first_name',
            'last_name'
        ]
        if not all(field in data for field in required_fields):
            raise serializers.ValidationError(
                "Все поля обязательны к заполнению"
            )
        return data

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' недопустимо"
            )
        return value

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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.following.filter(user=user).exists()
        return False


class UserRegistrationSerializer(serializers.ModelSerializer):
    username_validator = RegexValidator(
        regex=r'^\w[\w.@+-]*$',
        message="Имя должно соответствовать регулярному выражению")
    username = serializers.CharField(
        required=True, max_length=MAX_REGISTRATION_LENGTH,
        validators=[username_validator]
    )
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password],
        max_length=MAX_REGISTRATION_LENGTH
    )
    email = serializers.EmailField(
        required=True, max_length=MAX_REGISTRATION_LENGTH
    )
    first_name = serializers.CharField(
        required=True, max_length=MAX_REGISTRATION_LENGTH
    )
    last_name = serializers.CharField(
        required=True, max_length=MAX_REGISTRATION_LENGTH
    )

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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.following.filter(user=user).exists()
        return False


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
        return obj.following.filter(user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    following_username = serializers.ReadOnlyField(source='following.username')

    class Meta:
        model = Follow
        fields = ('user', 'following', 'following_username')


class BuyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tag'
    )

    class Meta:
        model = RecipeTag
        fields = ('id', )


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = IngredientDetailSerializer(
        source='recipeingredient_set', many=True
    )
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'tags', 'ingredients',
            'author', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and Favorite.objects.filter(
            recipe=obj, user=user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and BuyList.objects.filter(
            recipe=obj, user=user
        ).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        return representation


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(
        max_length=None, use_url=True, required=False, allow_null=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'tags', 'ingredients',
            'text', 'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients_data):
        ingredient_instances = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredient_instances)

    def set_tags(self, recipe, tags_data):
        # Логика для установки тегов для рецепта
        recipe.tags.set(tags_data)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )

        self.create_ingredients(recipe, ingredients_data)
        self.set_tags(recipe, tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        ingredients_data = validated_data.pop('recipeingredient_set', [])
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients_data)

        tags_data = validated_data.get('tags', [])
        self.set_tags(instance, tags_data)

        instance.save()
        return instance

    def validate(self, attrs):
        self.validate_required_fields(attrs, ['tags', 'cooking_time', 'image'])
        return attrs

    def validate_ingredients(self, ingredients):
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"error": "Duplicate ingredients are not allowed."}
            )

    def validate_tags(self, tags):
        if tags is None:
            raise serializers.ValidationError(
                {"error": "Field 'tags' is required."}
            )

        if not tags:
            raise serializers.ValidationError(
                {"error": "Field 'tags' cannot be empty."}
            )

        tags_ids = [tag.id for tag in tags]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(
                {"error": "Duplicate tags are not allowed."}
            )

    def validate_required_fields(self, attrs, required_fields):
        for field in required_fields:
            if field not in attrs:
                raise serializers.ValidationError(
                    {"error": f"Field '{field}' is required."}
                )


class SubscribeSerializer(serializers.ModelSerializer):
    following_id = serializers.IntegerField()

    def validate_following_id(self, value):
        user = self.context['request'].user
        if user.pk == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя или отписаться от себя.'
            )
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Пользователь не найден.')
        return value
