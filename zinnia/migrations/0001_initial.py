import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models

import mptt.fields

import tagging.fields

import zinnia.models_bases.entry
import zinnia.settings


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
            name='Entry',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    max_length=255, verbose_name='title')),
                ('slug', models.SlugField(
                    help_text="Used to build the entry's URL.", max_length=255,
                    verbose_name='slug', unique_for_date='creation_date')),
                ('status', models.IntegerField(
                    default=0, db_index=True, verbose_name='status',
                    choices=[(0, 'draft'), (1, 'hidden'), (2, 'published')])),
                ('start_publication', models.DateTimeField(
                    help_text='Start date of publication.', null=True,
                    verbose_name='start publication',
                    db_index=True, blank=True)),
                ('end_publication', models.DateTimeField(
                    help_text='End date of publication.', null=True,
                    verbose_name='end publication',
                    db_index=True, blank=True)),
                ('creation_date', models.DateTimeField(
                    default=django.utils.timezone.now,
                    help_text="Used to build the entry's URL.",
                    verbose_name='creation date', db_index=True)),
                ('last_update', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name='last update')),
                ('content', models.TextField(
                    verbose_name='content', blank=True)),
                ('comment_enabled', models.BooleanField(
                    default=True, help_text='Allows comments if checked.',
                    verbose_name='comments enabled')),
                ('pingback_enabled', models.BooleanField(
                    default=True, help_text='Allows pingbacks if checked.',
                    verbose_name='pingbacks enabled')),
                ('trackback_enabled', models.BooleanField(
                    default=True, help_text='Allows trackbacks if checked.',
                    verbose_name='trackbacks enabled')),
                ('comment_count', models.IntegerField(
                    default=0, verbose_name='comment count')),
                ('pingback_count', models.IntegerField(
                    default=0, verbose_name='pingback count')),
                ('trackback_count', models.IntegerField(
                    default=0, verbose_name='trackback count')),
                ('excerpt', models.TextField(
                    help_text='Used for SEO purposes.',
                    verbose_name='excerpt', blank=True)),
                ('image', models.ImageField(
                    help_text='Used for illustration.',
                    upload_to=zinnia.models_bases.entry.image_upload_to_dispatcher,  # noqa
                    verbose_name='image', blank=True)),
                ('featured', models.BooleanField(
                    default=False, verbose_name='featured')),
                ('tags', tagging.fields.TagField(
                    max_length=255, verbose_name='tags', blank=True)),
                ('login_required', models.BooleanField(
                    default=False, verbose_name='login required',
                    help_text='Only authenticated users can view the entry.')),
                ('password', models.CharField(
                    help_text='Protects the entry with a password.',
                    max_length=50, verbose_name='password', blank=True)),
                ('content_template', models.CharField(
                    default='zinnia/_entry_detail.html',
                    help_text="Template used to display the entry's content.",
                    max_length=250, verbose_name='content template',
                    choices=[
                        ('zinnia/_entry_detail.html', 'Default template')] + \
                        zinnia.settings.ENTRY_CONTENT_TEMPLATES)),
                ('detail_template', models.CharField(
                    default='entry_detail.html',
                    help_text="Template used to display the entry's detail page.",  # noqa
                    max_length=250, verbose_name='detail template',
                    choices=[
                        ('entry_detail.html', 'Default template')] + \
                        zinnia.settings.ENTRY_DETAIL_TEMPLATES)),
                ('categories', models.ManyToManyField(
                    related_name='entries',
                    verbose_name='categories', to='zinnia.Category',
                    blank=True)),
                ('related', models.ManyToManyField(
                    related_name='related_rel_+',
                    verbose_name='related entries', to='zinnia.Entry',
                    blank=True)),
                ('sites', models.ManyToManyField(
                    help_text='Sites where the entry will be published.',
                    related_name='entries', verbose_name='sites',
                    to='sites.Site')),
            ],
            options={
                'get_latest_by': 'creation_date',
                'ordering': ['-creation_date'],
                'abstract': False,
                'verbose_name_plural': 'entries',
                'verbose_name': 'entry',
                'permissions': (('can_view_all', 'Can view all entries'),
                                ('can_change_status', 'Can change status'),
                                ('can_change_author', 'Can change author(s)')),
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
        migrations.AddField(
            model_name='entry',
            name='authors',
            field=models.ManyToManyField(
                related_name='entries', verbose_name='authors',
                to='zinnia.Author', blank=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='entry',
            index_together=set([('status', 'creation_date',
                                 'start_publication', 'end_publication'),
                                ('slug', 'creation_date')]),
        ),
    ]
