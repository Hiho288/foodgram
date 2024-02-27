from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from django.db import models



'''Юзер'''
User = get_user_model()



'''Модель тега'''
class Tag(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    slug = models.SlugField(max_length=16)


'''Модель ингредиента'''
class Ingredient(models.Model):
    class Unit(models.TextChoices):
        GRAMM = "г"
        PIECE = "шт"
        # , choices=Unit.choices) #default=Unit.USER
    name = models.CharField(max_length=16)
    amount = models.IntegerField()
    unit = models.CharField(max_length=16)

    def __str__(self):
        return self.name




'''Модель рецепта'''
class Recipe(models.Model):
    author = models.ForeignKey(User, related_name='HHH', on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    image = models.ImageField(upload_to='cats/images/', null=True, default=None) #HHH
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tag = models.ManyToManyField(Tag, through='RecipeTag')
    cooking_time = models.IntegerField()
    created = models.DateField(auto_now_add=True, verbose_name='Дата и время публикации рецепта')




#???????????????????
# '''Модель пользователя - Надо ли?'''
# class CustomUser(AbstractUser):
#     class Role(models.TextChoices):
#         USER = "user"
#         ADMIN = "admin"

#     username = models.CharField(
#         max_length=150,
#         unique=True,
#         validators=([RegexValidator(regex=r'^[\w.@+-]+\Z')])
#     )
#     role = models.CharField(
#         max_length=16,
#         choices=Role.choices,
#         default=Role.USER
#     )

#     @property
#     def is_admin(self):
#         return self.role == self.Role.ADMIN





'''Many to Many Рецепт-Ингридиенты'''
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


'''Many to Many Рецепт-Тэг'''
class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


'''Many to Many Рецепт-Юзер'''
class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


'''Many to Many Подписки'''
class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Подписан на',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique__following',
            )
        ]

    def __str__(self):
        return f'{self.user.username} follows {self.following.username}'


'''Many to Many Рецепт-Юзер'''
class BuyList(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)