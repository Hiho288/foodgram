from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from foodgram_backend.constants import (MAX_COOKING_TIME,
                                        MAX_INGREDIENT_AMOUNT,
                                        MAX_MEASUREMENT_UNIT_LENGTH,
                                        MAX_NAME_LENGTH, MIN_COOKING_TIME,
                                        MIN_INGREDIENT_AMOUNT)
from users.models import User


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    color = ColorField(format="hexa", default='#0a0a0a')
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.TextField(max_length=MAX_NAME_LENGTH)
    measurement_unit = models.CharField(max_length=MAX_MEASUREMENT_UNIT_LENGTH)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    created = models.DateField(
        auto_now_add=True,
        verbose_name='Дата и время публикации рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name='recipeingredient_set', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ]
    )


class RecipeTag(models.Model):
    """Many to Many Рецепт-Тэг"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name


class Favorite(models.Model):
    """Many to Many Рецепт-Юзер"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique__recipe',
            ),
        )


class BuyList(models.Model):
    """Many to Many Рецепт-Юзер"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_list'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Карточка покупок'
        verbose_name_plural = 'Карточки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique__recipe_buylist',
            ),
        )
