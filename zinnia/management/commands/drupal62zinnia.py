# Argument parsing.
from optparse import make_option
import getpass

# For timestamp and date processing.
from datetime import datetime
import pytz

# For accessing the Drupal database.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# Django imports
from django.core.management.base import LabelCommand, CommandError
from django.template.defaultfilters import slugify

# Import Django models.
from django.contrib.sites.models import Site
from django.contrib.comments import get_model as get_comment_model
Comment = get_comment_model()

# Import the Zinnia models.
from zinnia.models import Author
from zinnia.models import Category
from zinnia.models import Entry
from zinnia.managers import PUBLISHED

# Disconnect the Zinnia signals so pingbacks wouldn't get called during import.
#from zinnia.signals import disconnect_entry_signals
#from zinnia.signals import disconnect_discussion_signals

#######################################
# Helper classes for argument parsing #
#######################################

def create_mappingaction(argument_name):
    """
    Wrapper function for generating a MappingAction that will store the parsed
    data under specified argument_name in argparse's namespace.

    Arguments:
        - argument_name - Name of the argument where the parsed data will be
          stored.

    Returns:
        A mappingaction function.
    """

    def mappingaction(option, option_string, value, parser, argument_name=argument_name):
        """
        Custom optparse action for processing arguments of format:

        arg1[=maparg1]:arg2[=maparg2]:...:argN[=mapargN]

        The action can be used for adding a dictionary to the specified
        namespace where the keys are arg1, arg2, ..., argN, and values are
        maparg1, maparg2, ..., mapargN.

        Specifying the maparg mapping is optional. When not specified, the
        action will use the value of key.
        """

        if not getattr(parser.values, argument_name):
            setattr(parser.values, argument_name, dict())
        for mapping in value.split(":"):
            if "=" in mapping:
                key, value = mapping.split("=", 1)
                getattr(parser.values, argument_name)[key] = value
            else:
                getattr(parser.values, argument_name)[mapping] = mapping

    return mappingaction


###############
# Import code #
###############
class DrupalToZinnia(object):
    """
    Class for import Drupal blog content into Zinnia.
    """

    def __init__(self, engine, node_type = "blog", users = dict()):
        """
        Initialised the importer class.

        Arguments:
            session - SQL Alchemy engine that can be used for making the
            sessions and obtaining declarative bases.

            node_type - String specifying the node type that is assigned to blog
            entries. Defaults to "blog".

            users - Dictionary specifying which users should be imported from
            Drupal, and how to map them to Zinnia authorts. Keys are Drupal
            usernames, and associated values are Zinnia usernames. Default
            (empty dictionary) means all users will be processed).
        """

        self.initialise_alchemy(engine)
        self.node_type = node_type

        # Extract general information from Zinnia.
        self.site = Site.objects.get_current()

        # Get a list of all users for which the blogs should be migrated.
        if users:
            drupal_users = self.session.query(self.Users).filter(self.Users.name.in_(users.keys())).all()
        else:
            drupal_users = self.session.query(self.Users).all()

        # Create mapping of Drupal uid's to Zinnia authors.
        self.author_mapping = {}
        for user in drupal_users:
            try:
                author = Author.objects.get(username=users.get(user.name, user.name))
            except Author.DoesNotExist:
                # If the specified author does not exist, simply default to
                # first one found in Zinnia.
                author = Author.objects.get()
            print "Mapping Drupal user '%s' to '%s'" % (user.name, author.username)
            self.author_mapping[user.uid] = author

        # Create a dictionary of all tag terms.
        self.tag_mapping = {}
        for vocabulary in self.session.query(self.Vocabulary).filter(self.Vocabulary.tags==1).all():
            terms = self.session.query(self.TermData).filter(self.TermData.vid==vocabulary.vid).all()
            for term in terms:
                # The term name is not allowed to contain slashes.
                self.tag_mapping[term.tid] = term.name.replace("/", "-")

        # Create a dictinoary of all category terms.
        self.category_mapping = {}
        for vocabulary in self.session.query(self.Vocabulary).filter(self.Vocabulary.tags==0).all():
            terms = self.session.query(self.TermData).filter(self.TermData.vid==vocabulary.vid).all()
            for term in terms:
                # The term name is not allowed to contain slashes.
                self.category_mapping[term.tid] = term.name


    def initialise_alchemy(self, engine):
        """
        Initialises SQLAlchemy handlers and table mappings using the provided
        engine.

        Arguments:
            engine - SQLAlchemy engine.
        """

        self.engine = engine
        self.session = sessionmaker(bind=self.engine)()
        Base = declarative_base(self.engine)

        class Node(Base):
            """
            For accessing Drupal's "node" table. This table contains mainly metadata
            about a node.
            """
            
            __tablename__ = 'node'
            __table_args__ = {'autoload': True}


        class NodeRevisions(Base):
            """
            For accessing Drupal's "node_revisions" table. This table contains the
            actual content of nodes.
            """

            __tablename__ = 'node_revisions'
            __table_args__ = {'autoload': True}


        class Users(Base):
            """
            For accessing Drupal's "users" table. This table contains information about
            users.
            """
            
            __tablename__ = 'users'
            __table_args__ = {'autoload': True}
            

        class Vocabulary(Base):
            """
            For accessing Drupal's "vocabulary" table. This table contains information
            about Drupal vocabularies (tags and categories).
            """

            __tablename__ = 'vocabulary'
            __table_args__ = {'autoload': True}


        class TermNode(Base):
            """
            For accessing Drupal's "term_node" table. This table contains information about
            mapping of terms from vocabulaires to nodes.
            """

            __tablename__ = 'term_node'
            __table_args__ = {'autoload': True}


        class TermData(Base):
            """
            For accessing Drupal's "term_data" table. This table contains data about
            terms.
            """

            __tablename__ = 'term_data'
            __table_args__ = {'autoload': True}


        class TermHierarchy(Base):
            """
            For accessing Drupal's "term_hierarchy" table. This table contains data
            about term hierarchies (used for importing categories).
            """

            __tablename__ = 'term_hierarchy'
            __table_args__ = {'autoload': True}


        class Comments(Base):
            """
            For accessing Drupal's "comments" table. This table contains comment data.
            """

            __tablename__ = 'comments'
            __table_args__ = {'autoload': True}

        
        self.Node = Node
        self.NodeRevisions = NodeRevisions
        self.Users = Users
        self.Vocabulary = Vocabulary
        self.TermNode = TermNode
        self.TermData = TermData
        self.TermHierarchy = TermHierarchy
        self.Comments = Comments


    def import_users(self):
        """
        Run the import of users.
        """
        pass

    def import_content(self):
        """
        Run the import of blog content.
        """

        # Get a list of all blogs, sorted by creation date.
        nodes = self.session.query(self.Node).filter(self.Node.type == self.node_type,
                                                     self.Node.uid.in_(self.author_mapping.keys())).order_by(self.Node.created)

        # Process each blog entry.
        for node in nodes:
            # Extract the last revision of the blog.
            revisions = self.session.query(self.NodeRevisions).filter(self.NodeRevisions.nid == node.nid)
        
            # Extract blog data.
            last = revisions.order_by(self.NodeRevisions.vid.desc()).first()
            body = last.body
            title = last.title
            modified = datetime.fromtimestamp(last.timestamp, pytz.UTC)
            created = datetime.fromtimestamp(node.created, pytz.UTC)
            user = self.author_mapping[node.uid]
        
            # Create the entry if it doesn't exist already.
            if not Entry.objects.filter(title=title).exists():
                zinnia_entry = Entry(content=body, creation_date=created,
                                     last_update=modified, title=title,
                                     status=PUBLISHED, slug=slugify(title))
                zinnia_entry.save()
        
                # Add relations (authors etc).
                zinnia_entry.authors.add(user)
                zinnia_entry.sites.add(self.site)
                zinnia_entry.save()

                # Import tags.
                zinnia_entry.tags = self.get_tags(last)
                zinnia_entry.save()

                # Set-up categories for entry.
                zinnia_entry.categories.add(*[c.id for c in self.get_categories(last)])
                zinnia_entry.save()

                # Import comment for an entry.
                self.import_comments(node, zinnia_entry)
        
                print "Imported entry '%s'" % title
            else:
                print "Skipping existing entry '%s'" % title
        
    def get_tags(self, version):
        """
        Retrives tags for Drupal node revision. The slash character ('/') in a
        tag will be automatically replaced by a dash ('-'). This is limitation
        of Django/Zinnia.

        Arguments:
            version - Version of a Drupal node. In most cases this should be the
            last one available.

        Returns:
            Comma-delimited tags.
        """

        version_terms = self.session.query(self.TermNode).filter(self.TermNode.nid==version.nid, self.TermNode.vid==version.vid).all()

        tags = ",".join([self.tag_mapping[t.tid] for t in version_terms if t.tid in self.tag_mapping])

        return tags

    def get_categories(self, version):
        """
        Retrives a list of categories from Zinnia corresponding to the provided
        Drupal node version. Categories have to be imported before performing
        this step.

        Arguments:
            version - Version of a Drupal node. In most cases this should be the
            last one available.

        Returns:
            List of Zinnia categories.
        """

        version_categories = self.session.query(self.TermNode).filter(self.TermNode.nid==version.nid, self.TermNode.vid==version.vid).all()
        version_categories = [v for v in version_categories if v.tid in self.category_mapping]

        return Category.objects.filter(title__in=[self.category_mapping[v.tid] for v in version_categories])

    def import_categories(self):
        """
        Runs the import of categories.
        """

        # Mapping of term IDs (tid) from Drupal to Zinnia Category IDs. Provides
        # safer way to identify correct category in case of identically named
        # categories in different category trees.
        zinnia_category_mapping = {}

        # Category hierarchy information, stored as tid, tid key/value pairs.
        category_parents = {}

        # Iterate over non-tag Drupal vocabularies.
        for vocabulary in self.session.query(self.Vocabulary).filter(self.Vocabulary.tags!=1).all():
            # Look-up the terms that belong to the vocabulary.
            for term in self.session.query(self.TermData).filter(self.TermData.vid==vocabulary.vid).all():
                if not Category.objects.filter(title=term.name).exists():
                    parent_id = self.session.query(self.TermHierarchy).filter(self.TermHierarchy.tid==term.tid).first().parent

                    category = Category(title=term.name, description=term.description, slug = slugify(term.name))
                    category.save()

                    zinnia_category_mapping[term.tid] = category.pk
                    category_parents[term.tid] = parent_id

        # Set-up category hierarchy.
        for tid, parent_id in category_parents.iteritems():
            if parent_id != 0:
                category = Category.objects.get(pk=zinnia_category_mapping[tid])
                category.parent = Category.objects.get(pk=zinnia_category_mapping[parent_id])
                category.save()

    def import_comments(self, drupal_node, zinnia_entry):
        """
        Imports comments for a node from sepcified Drupal node into Zinnia
        entry.

        Arguments:
            drupal_node - Drupal node object from which the comments should be
            imported.
            zinnia_entry - Zinna entry to which the commments should be
            attached.
        """

        drupal_comments = self.session.query(self.Comments).filter(self.Comments.nid==drupal_node.nid).order_by(self.Comments.timestamp)
        for drupal_comment in drupal_comments:
            comment = Comment(#title=drupal_comment.subject,
                              comment=drupal_comment.comment,
                              ip_address=drupal_comment.hostname,
                              submit_date = datetime.fromtimestamp(drupal_comment.timestamp, pytz.UTC),
                              #status
                              name=drupal_comment.name,
                              email=drupal_comment.mail,
                              user_url=drupal_comment.homepage,
                              content_object = zinnia_entry,
                              site_id = self.site.pk)
            comment.save()
            #print drupal_comment.nid
            #print unicode(comment.comment).encode("utf-8")


###########
# Command #
###########
class Command(LabelCommand):
    option_list = LabelCommand.option_list + (
        make_option("-H", "--database-hostname", type="string", default="localhost",
                    help="Hostname of database server providing the Drupal database."),
        make_option("-p", "--database-port", type="int", default=3306,
                    help="TCP port at which the database server is listening."),
        make_option("-u", "--database-username", type="string", default="root",
                    help="Username that should be used for connecting to database server."),
        make_option("-P", "--database-password", type="string", default=None,
                    dest="database_password_file",
                    help="Password for the database username specified. Read interactively if not set"),
        make_option("-n", "--node-type", type="string", default="blog",
                    help="Drupal Node type that should be processed."),
        make_option("-U", "--users", type="string", action="callback",
                    callback=create_mappingaction("users"), default=dict(),
                    help="List of Drupal users that should be imported, including their mapping to Zinnia users. Default is to import all user blogs with preserved usernames.")
        
        )
    
    def handle_label(self, database_name, **options):
        # Read the password for Drupal database if it wasn't provided within a file.
        if options['database_password_file']:
            options['database_password'] = open(options['database_password_file'], "r").read().rstrip().lstrip()
        else:
            options['database_password'] = getpass.getpass("Database password for '%s'@'%s': " % (options['database_username'], database_name))

        # Set-up SQLAlchemy.
        database_connection_url = "mysql://%s:%s@%s/%s" % (urllib.quote(options['database_username']),
                                                           urllib.quote(options['database_password']),
                                                           urllib.quote(options['database_hostname']),
                                                           urllib.quote(database_name))
        engine = create_engine(database_connection_url)

        importer = DrupalToZinnia(engine, options['node_type'], options['users'])
        importer.import_categories()
        importer.import_content()

