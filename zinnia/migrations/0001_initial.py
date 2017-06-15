from django.conf import settings
from django.db import migrations
from django.db import models

import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('sites', '0001_initial'),
        (migrations.swappable_dependency(settings.AUTH_USER_MODEL)),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    max_length=255, verbose_name='title')),
                ('slug', models.SlugField(
                    help_text="Used to build the category's URL.", unique=True,
                    max_length=255, verbose_name='slug')),
                ('description', models.TextField(
                    verbose_name='description', blank=True)),
                ('lft', models.PositiveIntegerField(
                    editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(
                    editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(
                    editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(
                    editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(
                    related_name='children', verbose_name='parent category',
                    on_delete=models.CASCADE,
                    blank=True, to='zinnia.Category', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(settings.AUTH_USER_MODEL.lower(), models.Model),
        ),
    ]
