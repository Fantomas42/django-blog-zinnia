"""XML-RPC methods of Zinnia metaWeblog API"""
import os
from datetime import datetime
from xmlrpclib import Fault
from xmlrpclib import DateTime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.settings import UPLOAD_TO
from zinnia.managers import DRAFT, PUBLISHED
from django_xmlrpc.decorators import xmlrpc_func


# http://docs.nucleuscms.org/blog/12#errorcodes
LOGIN_ERROR = 801
PERMISSION_DENIED = 803

def authenticate(username, password, permission=None):
    """Authenticate staff_user with permission"""
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        raise Fault(LOGIN_ERROR, _('Username is incorrect.'))
    if not user.check_password(password):
        raise Fault(LOGIN_ERROR, _('Password is invalid.'))
    if not user.is_staff or not user.is_active:
        raise Fault(PERMISSION_DENIED, _('User account unavailable.'))
    if permission:
        if not user.has_perm(permission):
            raise Fault(PERMISSION_DENIED, _('User cannot %s.') % permission)
    return user

def blog_structure(site):
    """A blog structure"""
    return {'url': 'http://%s%s' % (
        site.domain, reverse('zinnia_entry_archive_index')),
            'blogid': settings.SITE_ID,
            'blogName': site.name}

def user_structure(user, site):
    """An user structure"""
    return {'userid': user.pk,
            'email': user.email,
            'nickname': user.username,
            'lastname': user.last_name,
            'firstname': user.first_name,
            'url': 'http://%s%s' % (
                site.domain, reverse('zinnia_author_detail', args=[user.username]))}

def category_structure(category, site):
    """A category structure"""
    return {'description': category.title,
            'htmlUrl': 'http://%s%s' % (
                site.domain, category.get_absolute_url()),
            'rssUrl': 'http://%s%s' % (
                site.domain, reverse('zinnia_category_feed', args=[category.slug]))}

def post_structure(entry, site):
    """A post structure with extensions"""
    return {'title': entry.title,
            'description': unicode(entry.html_content),
            'link': 'http://%s%s' % (site.domain, entry.get_absolute_url()),
            # Basic Extensions
            'permaLink': 'http://%s%s' % (site.domain, entry.get_absolute_url()),
            'categories': [cat.title for cat in entry.categories.all()],
            'dateCreated': DateTime(entry.creation_date.isoformat()),
            'postid': entry.pk,
            'userid': entry.authors.all()[0].username,
            # Usefull Movable Type Extensions
            'mt_excerpt': entry.excerpt,
            'mt_allow_comments': int(entry.comment_enabled),
            'mt_allow_pings': int(entry.pingback_enabled),
            'mt_keywords': entry.tags,
            # Usefull Wordpress Extensions
            'wp_slug': entry.slug}

@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_users_blogs(apikey, username, password):
    """blogger.getUsersBlogs(api_key, username, password)
    => blog structure[]"""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [blog_structure(site),]

@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_user_info(apikey, username, password):
    """blogger.getUserInfo(api_key, username, password)
    => user structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return user_structure(user, site)

@xmlrpc_func(returns='boolean', args=['string', 'string', 'string', 'string', 'string'])
def delete_post(apikey, post_id, username, password, publish):
    """blogger.deletePost(api_key, post_id, username, password, 'publish')
    => boolean"""
    user = authenticate(username, password, 'zinnia.delete_entry')
    entry = Entry.objects.get(id=post_id, authors=user)
    entry.delete()
    return True

@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_post(post_id, username, password):
    """metaWeblog.getPost(post_id, username, password)
    => post structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return post_structure(Entry.objects.get(id=post_id, authors=user), site)

@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string', 'integer'])
def get_recent_posts(blog_id, username, password, number):
    """metaWeblog.getRecentPosts(blog_id, username, password, number)
    => post structure[]"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return [post_structure(entry, site) \
            for entry in Entry.objects.filter(authors=user)[:number]]

@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_categories(blog_id, username, password):
    """metaWeblog.getCategories(blog_id, username, password)
    => category structure[]"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return [category_structure(category, site) \
            for category in Category.objects.all()]

@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'struct', 'boolean'])
def new_post(blog_id, username, password, post, publish):
    """metaWeblog.newPost(blog_id, username, password, post, publish)
    => post_id"""
    user = authenticate(username, password, 'zinnia.add_entry')
    if post.get('dateCreated'):
        creation_date = datetime.strptime(post['dateCreated'].value.replace('Z', '').replace('-', ''),
                                          '%Y%m%dT%H:%M:%S')
    else:
        creation_date = datetime.now()

    entry_dict = {'title': post['title'],
                  'content': post['description'],
                  'excerpt': post.get('mt_excerpt', truncate_words(strip_tags(post['description']), 50)),
                  'creation_date': creation_date,
                  'last_update': creation_date,
                  'comment_enabled': post.get('mt_allow_comments', 1) == 1,
                  'pingback_enabled': post.get('mt_allow_pings', 1) == 1,
                  'tags': post.has_key('mt_keywords') and post['mt_keywords'] or '',
                  'slug': post.has_key('wp_slug') and post['wp_slug'] or slugify(post['title']),
                  'status': publish and PUBLISHED or DRAFT}
    entry = Entry.objects.create(**entry_dict)
    entry.authors.add(user)
    entry.sites.add(Site.objects.get_current())
    if post.has_key('categories'):
        entry.categories.add(*[Category.objects.get_or_create(title=cat, slug=slugify(cat))[0]
                               for cat in post['categories']])

    return entry.pk


@xmlrpc_func(returns='boolean', args=['string', 'string', 'string', 'struct', 'boolean'])
def edit_post(post_id, username, password, post, publish):
    """metaWeblog.editPost(post_id, username, password, post, publish)
    => boolean"""
    user = authenticate(username, password, 'zinnia.change_entry')
    entry = Entry.objects.get(id=post_id, authors=user)
    if post.get('dateCreated'):
        creation_date = datetime.strptime(post['dateCreated'].value.replace('Z', '').replace('-', ''),
                                          '%Y%m%dT%H:%M:%S')
    else:
        creation_date = entry.creation_date

    entry.title = post['title']
    entry.content = post['description']
    entry.excerpt = post.get('mt_excerpt', truncate_words(strip_tags(post['description']), 50))
    entry.creation_date = creation_date
    entry.last_update = datetime.now()
    entry.comment_enabled = post.get('mt_allow_comments', 1) == 1
    entry.pingback_enabled = post.get('mt_allow_pings', 1) == 1
    entry.tags = post.has_key('mt_keywords') and post['mt_keywords'] or ''
    entry.slug = post.has_key('wp_slug') and post['wp_slug'] or slugify(post['title'])
    entry.status = publish and PUBLISHED or DRAFT
    entry.save()
    if post.has_key('categories'):
        entry.categories.clear()
        entry.categories.add(*[Category.objects.get_or_create(title=cat, slug=slugify(cat))[0]
                               for cat in post['categories']])
    return True

@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'struct'])
def new_media_object(blog_id, username, password, media):
    """metaWeblog.newMediaObject(blog_id, username, password, media)
    => media structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()

    path = default_storage.save(os.path.join(UPLOAD_TO, media['name']),
                                ContentFile(media['bits'].data))
    return {'url': default_storage.url(path)}

