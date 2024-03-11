from django.contrib.auth import get_user_model

from django.db import models



'''Юзер'''
User = get_user_model()


'''Модель тега'''
class Tag(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    slug = models.SlugField(max_length=16)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
'''Модель ингредиента'''
class Ingredient(models.Model):
    name = models.TextField(max_length=64)
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name
'''Модель рецепта'''
class Recipe(models.Model):
    author = models.ForeignKey(User, related_name='HHH', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to='cats/images/', null=True, default=None) #HHH
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag, through='RecipeTag', related_name='recipes')
    cooking_time = models.IntegerField()
    created = models.DateField(auto_now_add=True, verbose_name='Дата и время публикации рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipeingredient_set', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()



'''Many to Many Рецепт-Тэг'''
class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name


'''Many to Many Рецепт-Юзер'''
class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


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