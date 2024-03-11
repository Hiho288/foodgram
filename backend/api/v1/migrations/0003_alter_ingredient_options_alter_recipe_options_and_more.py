# Generated by Django 5.0.2 on 2024-03-09 10:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0002_rename_tag_recipe_tags_alter_recipe_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='created',
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=1, upload_to='recipes/images/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='v1.tag'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(),
        ),
    ]
