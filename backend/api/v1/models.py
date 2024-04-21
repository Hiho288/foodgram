from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_INGREDIENT_AMOUNT = 1
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 480


class User(AbstractUser):
    """Юзер"""
    def get_follower_count(self):
        return self.followers.count()

    def get_recipe_count(self):
        return self.recipes.count()


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField()
    color = ColorField(format="hexa", default='#0a0a0a')
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.TextField(max_length=64)
    measurement_unit = models.CharField(max_length=16)

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
    name = models.CharField(max_length=64)
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', required=True
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
            ),
        )


class Follow(models.Model):
    """Many to Many Подписки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписан на',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique__following',
            ),
            models.CheckConstraint(
                check=models.ExpressionWrapper(
                    models.F('user') != models.F('following'),
                    output_field=models.BooleanField()
                ),
                name='user_cannot_follow_self'
            )
        ]

    def __str__(self):
        return f'{self.user.username} follows {self.following.username}'


class BuyList(models.Model):
    """Many to Many Рецепт-Юзер"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Карточка покупок'
        verbose_name_plural = 'Карточки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
            ),
        )
