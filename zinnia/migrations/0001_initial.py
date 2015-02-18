from django.db import models
from django.db import migrations
import django.utils.timezone

import mptt.fields
import tagging.fields

import zinnia.models_bases.entry
from . import user_model_label

from ..models import Entry
from ..models_bases.entry import CoreEntry, ContentEntry, \
    DiscussionsEntry, RelatedEntry, ExcerptEntry, ImageEntry, FeaturedEntry, \
    AuthorsEntry, CategoriesEntry, TagsEntry, LoginRequiredEntry, \
    PasswordRequiredEntry, ContentTemplateEntry, DetailTemplateEntry


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
                blank=True, to='zinnia.Category', null=True))],
        options={
            'ordering': ['title'],
            'verbose_name': 'category',
            'verbose_name_plural': 'categories',},
        bases=(models.Model,),),
    migrations.CreateModel(
        name='Author',
        fields=[],
        options={'proxy': True, },
        bases=(user_model_label, models.Model)),
    migrations.CreateModel(
        name='Entry',
        fields=[('id', models.AutoField(
            verbose_name='ID', serialize=False,
            auto_created=True, primary_key=True)),],
            options={'abstract': False, }),
]

if issubclass(Entry, CoreEntry):
    operations += [
        migrations.AddField(
            model_name='Entry',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title')),
        migrations.AddField(
            model_name='Entry',
            name='slug',
            field=models.SlugField(
                help_text="Used to build the entry's URL.", max_length=255,
                verbose_name='slug', unique_for_date='creation_date')),
        migrations.AddField(
            model_name='Entry',
            name='status',
            field=models.IntegerField(
                default=0, db_index=True, verbose_name='status',
                choices=CoreEntry.STATUS_CHOICES)),
        migrations.AddField(
            model_name='Entry',
            name='start_publication',
            field=models.DateTimeField(
                help_text='Start date of publication.', null=True,
                verbose_name='start publication',
                db_index=True, blank=True)),
        migrations.AddField(
            model_name='Entry',
            name='end_publication',
            field=models.DateTimeField(
                help_text='End date of publication.', null=True,
                verbose_name='end publication',
                db_index=True, blank=True)),
        migrations.AddField(
            model_name='Entry',
            name='sites',
            field=models.ManyToManyField(
                help_text='Sites where the entry will be published.',
                related_name='entries', verbose_name='sites',
                to='sites.Site')),
        migrations.AddField(
            model_name='Entry',
            name='creation_date',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Used to build the entry's URL.",
                verbose_name='creation date', db_index=True)),
        migrations.AddField(
            model_name='Entry',
            name='last_update',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name='last update')),
        migrations.AlterModelOptions(
            name='Entry',
            options={
                'get_latest_by': 'creation_date',
                'ordering': ['-creation_date'],
                'verbose_name_plural': 'entries',
                'verbose_name': 'entry',
                'permissions': (('can_view_all', 'Can view all entries'),
                                ('can_change_status', 'Can change status'),
                                ('can_change_author', 'Can change author(s)')), },
        ),
        migrations.AlterIndexTogether(
            name='Entry',
            index_together={
                ('status', 'creation_date', 'start_publication', 'end_publication'),
                ('slug', 'creation_date')}),
    ]

if issubclass(Entry, ContentEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='content',
        field=models.TextField(verbose_name='content', blank=True),))

if issubclass(Entry, DiscussionsEntry):
    operations += [
        migrations.AddField(
            model_name='Entry',
            name='comment_enabled',
            field=models.BooleanField(
                default=True, help_text='Allows comments if checked.',
                verbose_name='comments enabled')),
        migrations.AddField(
            model_name='Entry',
            name='pingback_enabled',
            field=models.BooleanField(
                default=True, help_text='Allows pingbacks if checked.',
                verbose_name='pingbacks enabled')),
        migrations.AddField(
            model_name='Entry',
            name='trackback_enabled',
            field=models.BooleanField(
                default=True, help_text='Allows trackbacks if checked.',
                verbose_name='trackbacks enabled')),
        migrations.AddField(
            model_name='Entry',
            name='comment_count',
            field=models.IntegerField(default=0, verbose_name='comment count')),
        migrations.AddField(
            model_name='Entry',
            name='pingback_count',
            field=models.IntegerField(
                default=0, verbose_name='pingback count')),
        migrations.AddField(
            model_name='Entry',
            name='trackback_count',
            field=models.IntegerField(
                default=0, verbose_name='trackback count')),
    ]

if issubclass(Entry, RelatedEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='related',
        field=models.ManyToManyField(
            related_name='related_rel_+', null=True,
            verbose_name='related entries', to='zinnia.Entry',
            blank=True)))

if issubclass(Entry, ExcerptEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='excerpt',
        field=models.TextField(
            help_text='Used for search and SEO.',
            verbose_name='excerpt', blank=True)))

if issubclass(Entry, ImageEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='image',
        field=models.ImageField(
            help_text='Used for illustration.',
            upload_to=zinnia.models_bases.entry.image_upload_to_dispatcher,
            verbose_name='image', blank=True)))

if issubclass(Entry, FeaturedEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='featured',
        field=models.BooleanField(default=False, verbose_name='featured')))

if issubclass(Entry, AuthorsEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='authors',
        field=models.ManyToManyField(
            related_name='entries', verbose_name='authors',
            to='zinnia.Author', blank=True),
        preserve_default=True))

if issubclass(Entry, CategoriesEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='categories',
        field=models.ManyToManyField(
            related_name='entries', null=True,
            verbose_name='categories', to='zinnia.Category',
            blank=True)))

if issubclass(Entry, TagsEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='tags',
        field=tagging.fields.TagField(
            max_length=255, verbose_name='tags', blank=True)))

if issubclass(Entry, LoginRequiredEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='login_required',
        field=models.BooleanField(
            default=False, verbose_name='login required',
            help_text='Only authenticated users can view the entry.')))

if issubclass(Entry, PasswordRequiredEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='password',
        field=models.CharField(
            help_text='Protects the entry with a password.',
            max_length=50, verbose_name='password', blank=True)))

if issubclass(Entry, ContentTemplateEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='content_template',
        field=models.CharField(
            default='zinnia/_entry_detail.html',
            help_text="Template used to display the entry's content.",
            max_length=250, verbose_name='content template',
            choices=[('zinnia/_entry_detail.html', 'Default template')])))

if issubclass(Entry, DetailTemplateEntry):
    operations.append(migrations.AddField(
        model_name='Entry',
        name='detail_template',
        field=models.CharField(
            default='entry_detail.html',
            help_text="Template used to display the entry's detail page.",
            max_length=250, verbose_name='detail template',
            choices=[('entry_detail.html', 'Default template')])))


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
        ('sites', '0001_initial'),
    ]

    operations = operations
