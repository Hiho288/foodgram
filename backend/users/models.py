from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Юзер"""
    def get_follower_count(self):
        return self.followers.count()

    def get_recipe_count(self):
        return self.recipes.count()


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
                name='uniq__following',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user == self.following:
            raise ValidationError(
                "Пользователь не может подписаться на самого себя."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} follows {self.following.username}'
