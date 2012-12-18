"""Test cases for Zinnia's MetaWeblog API"""
from xmlrpclib import Binary
from xmlrpclib import Fault
from xmlrpclib import ServerProxy
from tempfile import TemporaryFile

from django.test import TestCase
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED
from zinnia.settings import UPLOAD_TO
from zinnia.tests.utils import datetime
from zinnia.xmlrpc.metaweblog import authenticate
from zinnia.xmlrpc.metaweblog import post_structure
from zinnia.tests.utils import TestTransport


class MetaWeblogTestCase(TestCase):
    """Test cases for MetaWeblog"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        # Create data
        self.webmaster = Author.objects.create_superuser(
            username='webmaster',
            email='webmaster@example.com',
            password='password')
        self.contributor = Author.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='password')
        self.site = Site.objects.get_current()
        self.categories = [
            Category.objects.create(title='Category 1',
                                    slug='category-1'),
            Category.objects.create(title='Category 2',
                                    slug='category-2')]
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'creation_date': datetime(2010, 1, 1, 12),
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.webmaster)
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'creation_date': datetime(2010, 3, 15),
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(self.webmaster)
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.site)
        # Instanciating the server proxy
        self.server = ServerProxy('http://localhost:8000/xmlrpc/',
                                  transport=TestTransport())

    def test_authenticate(self):
        self.assertRaises(Fault, authenticate, 'badcontributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'password')
        self.contributor.is_staff = True
        self.contributor.save()
        self.assertEquals(authenticate('contributor', 'password'),
                          self.contributor)
        self.assertRaises(Fault, authenticate, 'contributor',
                          'password', 'zinnia.change_entry')
        self.assertEquals(authenticate('webmaster', 'password'),
                          self.webmaster)
        self.assertEquals(authenticate('webmaster', 'password',
                                       'zinnia.change_entry'),
                          self.webmaster)

    def test_get_users_blogs(self):
        self.assertRaises(Fault, self.server.blogger.getUsersBlogs,
                          'apikey', 'contributor', 'password')
        self.assertEquals(
            self.server.blogger.getUsersBlogs(
                'apikey', 'webmaster', 'password'),
            [{'url': 'http://example.com/',
              'blogid': 1,
              'blogName': 'example.com'}])

    def test_get_user_info(self):
        self.assertRaises(Fault, self.server.blogger.getUserInfo,
                          'apikey', 'contributor', 'password')
        self.webmaster.first_name = 'John'
        self.webmaster.last_name = 'Doe'
        self.webmaster.save()
        self.assertEquals(self.server.blogger.getUserInfo(
            'apikey', 'webmaster', 'password'),
            {'firstname': 'John', 'lastname': 'Doe',
             'url': 'http://example.com/authors/webmaster/',
             'userid': self.webmaster.pk,
             'nickname': 'webmaster',
             'email': 'webmaster@example.com'})

    def test_get_authors(self):
        self.assertRaises(Fault, self.server.wp.getAuthors,
                          'apikey', 'contributor', 'password')
        self.assertEquals(
            self.server.wp.getAuthors(
                'apikey', 'webmaster', 'password'),
            [{'user_login': 'webmaster',
              'user_id': self.webmaster.pk,
              'user_email': 'webmaster@example.com',
              'display_name': 'webmaster'}])

    def test_get_categories(self):
        self.assertRaises(Fault, self.server.metaWeblog.getCategories,
                          1, 'contributor', 'password')
        self.assertEquals(
            self.server.metaWeblog.getCategories('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/categories/category-1/',
              'description': 'Category 1',
              'htmlUrl': 'http://example.com/categories/category-1/',
              'categoryId': 1, 'parentId': 0,
              'categoryName': 'Category 1',
              'categoryDescription': ''},
             {'rssUrl': 'http://example.com/feeds/categories/category-2/',
              'description': 'Category 2',
              'htmlUrl': 'http://example.com/categories/category-2/',
              'categoryId': 2, 'parentId': 0,
              'categoryName': 'Category 2',
              'categoryDescription': ''}])
        self.categories[1].parent = self.categories[0]
        self.categories[1].description = 'category 2 description'
        self.categories[1].save()
        self.assertEquals(
            self.server.metaWeblog.getCategories('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/categories/category-1/',
              'description': 'Category 1',
              'htmlUrl': 'http://example.com/categories/category-1/',
              'categoryId': 1, 'parentId': 0,
              'categoryName': 'Category 1',
              'categoryDescription': ''},
             {'rssUrl':
              'http://example.com/feeds/categories/category-1/category-2/',
              'description': 'Category 2',
              'htmlUrl':
              'http://example.com/categories/category-1/category-2/',
              'categoryId': 2, 'parentId': 1,
              'categoryName': 'Category 2',
              'categoryDescription': 'category 2 description'}])

    def test_new_category(self):
        category_struct = {'name': 'Category 3', 'slug': 'category-3',
                           'description': 'Category 3 description',
                           'parent_id': self.categories[0].pk}
        self.assertRaises(Fault, self.server.wp.newCategory,
                          1, 'contributor', 'password', category_struct)
        self.assertEquals(Category.objects.count(), 2)
        new_category_id = self.server.wp.newCategory(
            1, 'webmaster', 'password', category_struct)
        self.assertEquals(Category.objects.count(), 3)
        category = Category.objects.get(pk=new_category_id)
        self.assertEquals(category.title, 'Category 3')
        self.assertEquals(category.description, 'Category 3 description')
        self.assertEquals(category.slug, 'category-3')
        self.assertEquals(category.parent.pk, 1)

    def test_get_recent_posts(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRecentPosts,
                          1, 'contributor', 'password', 10)
        self.assertEquals(len(self.server.metaWeblog.getRecentPosts(
            1, 'webmaster', 'password', 10)), 2)

    def test_delete_post(self):
        self.assertRaises(Fault, self.server.blogger.deletePost,
                          'apikey', 1, 'contributor', 'password', 'publish')
        self.assertEquals(Entry.objects.count(), 2)
        self.assertTrue(
            self.server.blogger.deletePost(
                'apikey', self.entry_1.pk, 'webmaster', 'password', 'publish'))
        self.assertEquals(Entry.objects.count(), 1)

    def test_get_post(self):
        self.assertRaises(Fault, self.server.metaWeblog.getPost,
                          1, 'contributor', 'password')
        post = self.server.metaWeblog.getPost(
            self.entry_1.pk, 'webmaster', 'password')
        self.assertEquals(post['title'], self.entry_1.title)
        self.assertEquals(post['description'], '<p>My content 1</p>')
        self.assertEquals(post['categories'], ['Category 1', 'Category 2'])
        self.assertTrue('2010-01-01T12:00:00' in post['dateCreated'].value)
        self.assertEquals(post['link'],
                          'http://example.com/2010/01/01/my-entry-1/')
        self.assertEquals(post['permaLink'],
                          'http://example.com/2010/01/01/my-entry-1/')
        self.assertEquals(post['postid'], self.entry_1.pk)
        self.assertEquals(post['userid'], 'webmaster')
        self.assertEquals(post['mt_excerpt'], '')
        self.assertEquals(post['mt_allow_comments'], 1)
        self.assertEquals(post['mt_allow_pings'], 1)
        self.assertEquals(post['mt_keywords'], self.entry_1.tags)
        self.assertEquals(post['wp_author'], 'webmaster')
        self.assertEquals(post['wp_author_id'], self.webmaster.pk)
        self.assertEquals(post['wp_author_display_name'], 'webmaster')
        self.assertEquals(post['wp_password'], '')
        self.assertEquals(post['wp_slug'], self.entry_1.slug)

    def test_new_post(self):
        post = post_structure(self.entry_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.newPost,
                          1, 'contributor', 'password', post, 1)
        self.assertEquals(Entry.objects.count(), 2)
        self.assertEquals(Entry.published.count(), 1)
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 1)
        self.assertEquals(Entry.objects.count(), 3)
        self.assertEquals(Entry.published.count(), 2)
        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)
        self.assertEquals(Entry.objects.count(), 4)
        self.assertEquals(Entry.published.count(), 2)

    def test_edit_post(self):
        post = post_structure(self.entry_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.editPost,
                          1, 'contributor', 'password', post, 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)

        entry = Entry.objects.get(pk=new_post_id)
        self.assertEquals(entry.title, self.entry_2.title)
        self.assertEquals(entry.content, self.entry_2.html_content)
        self.assertEquals(entry.excerpt, self.entry_2.excerpt)
        self.assertEquals(entry.slug, self.entry_2.slug)
        self.assertEquals(entry.status, DRAFT)
        self.assertEquals(entry.password, self.entry_2.password)
        self.assertEquals(entry.comment_enabled, True)
        self.assertEquals(entry.pingback_enabled, True)
        self.assertEquals(entry.categories.count(), 1)
        self.assertEquals(entry.authors.count(), 1)
        self.assertEquals(entry.authors.all()[0], self.webmaster)
        self.assertEquals(entry.creation_date, self.entry_2.creation_date)

        entry.title = 'Title edited'
        entry.creation_date = datetime(2000, 1, 1)
        post = post_structure(entry, self.site)
        post['categories'] = ''
        post['description'] = 'Content edited'
        post['mt_excerpt'] = 'Content edited'
        post['wp_slug'] = 'slug-edited'
        post['wp_password'] = 'password'
        post['mt_allow_comments'] = 2
        post['mt_allow_pings'] = 0

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        self.assertEquals(response, True)
        entry = Entry.objects.get(pk=new_post_id)
        self.assertEquals(entry.title, post['title'])
        self.assertEquals(entry.content, post['description'])
        self.assertEquals(entry.excerpt, post['mt_excerpt'])
        self.assertEquals(entry.slug, 'slug-edited')
        self.assertEquals(entry.status, PUBLISHED)
        self.assertEquals(entry.password, 'password')
        self.assertEquals(entry.comment_enabled, False)
        self.assertEquals(entry.pingback_enabled, False)
        self.assertEquals(entry.categories.count(), 0)
        self.assertEquals(entry.creation_date, datetime(2000, 1, 1))

        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        entry = Entry.objects.get(pk=new_post_id)
        self.assertEquals(entry.authors.count(), 1)
        self.assertEquals(entry.authors.all()[0], self.contributor)
        self.assertEquals(entry.creation_date, datetime(2000, 1, 1))

    def test_new_media_object(self):
        file_ = TemporaryFile()
        file_.write('My test content')
        file_.seek(0)
        media = {'name': 'zinnia_test_file.txt',
                 'type': 'text/plain',
                 'bits': Binary(file_.read())}
        file_.close()

        self.assertRaises(Fault, self.server.metaWeblog.newMediaObject,
                          1, 'contributor', 'password', media)
        new_media = self.server.metaWeblog.newMediaObject(
            1, 'webmaster', 'password', media)
        self.assertTrue('/zinnia_test_file' in new_media['url'])
        default_storage.delete('/'.join([
            UPLOAD_TO, new_media['url'].split('/')[-1]]))
