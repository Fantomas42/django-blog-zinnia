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

# Django imports.
from django.core.management.base import LabelCommand, CommandError
from django.template.defaultfilters import slugify
from django.db import IntegrityError

# Import Django models.
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.comments import get_model as get_comment_model
Comment = get_comment_model()

# Import Zinnia models.
from zinnia.models import Author
from zinnia.models import Category
from zinnia.models import Entry
from zinnia.managers import PUBLISHED

# For preventing pingbacks during the import.
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals

#########################################
# Helper functions for argument parsing #
#########################################

def create_mappingaction(argument_name):
    """
    Wrapper function for generating a MappingAction that will store the parsed
    data under specified argument_name under parser's options.

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
    This class implements support for importing Drupal blog content into Zinnia.
    """

    def __init__(self, engine, node_type = "blog", users = dict(), threaded_comments = False):
        """
        Initialises the importer class.

        Arguments:
            engine - SQL Alchemy engine that can be used for making the sessions
            and obtaining declarative bases.

            node_type - String specifying the node type that is assigned to blog
            entries. Defaults to "blog".

            users - Dictionary specifying which users should be imported from
            Drupal, and how to map them to Zinnia authorts. Keys are Drupal
            usernames, and associated values are Zinnia usernames. Default
            (empty dictionary) means all users will be processed.

            threaded_comments - Specifies whether the comments should be
            imported as threaded or not. Default is False.
        """

        # Disconnect the signals so pingbacks etc won't get called.
        disconnect_entry_signals()
        disconnect_discussion_signals()

        self.initialise_alchemy(engine)
        self.node_type = node_type
        self.threaded_comments = threaded_comments
        self.users = users
        self.author_mapping = {}

        # Extract general information from Zinnia.
        self.site = Site.objects.get_current()

        # Create a dictionary of all tag terms.
        self.tag_mapping = {}
        for vocabulary in self.session.query(self.Vocabulary).filter(self.Vocabulary.tags==1).all():
            terms = self.session.query(self.TermData).filter(self.TermData.vid==vocabulary.vid).all()
            for term in terms:
                # The term name is not allowed to contain slashes.
                self.tag_mapping[term.tid] = term.name.replace("/", "-")


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

        # Fetch the users that should be imported.
        drupal_users = self.session.query(self.Users).filter(self.Users.name!="")

        # Determine if only a subset of users should be imported or not.
        if self.users:
            drupal_users = drupal_users.filter(self.Users.name.in_(self.users.keys()))

        print "Starting import of users."

        # Set-up some counters.
        import_count = {}
        import_count["drupal_total"] = drupal_users.count()
        import_count["new"] = 0
        import_count["existing"] = 0

        # Process each Drupal user.
        for drupal_user in drupal_users:
            # Apply mapping if it was provided.
            if self.users:
                username = self.users[drupal_user.name]
            else:
                username = drupal_user.name

            # Create the user if it exists, or fetch the existing entry.
            try:
                User.objects.filter(username=username).exists()
                user = User.objects.create_user(username, drupal_user.mail,
                                                getattr(drupal_user, "pass"))
                user.save()
                print "Added user: %s" % username
                import_count["new"] += 1
            except IntegrityError:
                user = User.objects.get(username=username)
                print "User already exists: %s" % username
                import_count["existing"] += 1

            author = Author.objects.get(username=username)

            self.author_mapping[drupal_user.uid] = user
            print "Drupal user '%s' mapped to Zinnia author '%s'" % (drupal_user.name, username)

        print "Total number of users in Drupal: %d" % import_count["drupal_total"]
        print "Imported users: %d" % import_count["new"]
        print "Skipped existing users: %d" % import_count["existing"]

    def import_content(self):
        """
        Imports the blog entry content from Drupal into Zinnia.
        """

        # Get a list of all blogs, sorted by creation date.
        nodes = self.session.query(self.Node).filter(self.Node.type == self.node_type,
                                                     self.Node.uid.in_(self.author_mapping.keys())).order_by(self.Node.created)

        # Set-up some counters.
        import_count = {}
        import_count["drupal_total"] = nodes.count()
        import_count["new"] = 0
        import_count["existing"] = 0

        print "Starting import of blog entries."

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
            if not Entry.objects.filter(title=title, creation_date=created, last_update=modified).exists():
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

                import_count["new"] += 1
                print "Imported entry '%s'" % title
            else:
                import_count["existing"] += 1
                print "Skipping existing entry '%s'" % title
        
        print "Total number of blog entries in Drupal: %d" % import_count["drupal_total"]
        print "Imported blog entries: %d" % import_count["new"]
        print "Skipped existing entries: %d" % import_count["existing"]

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

        version_categories_query = self.session.query(self.TermNode).filter(self.TermNode.nid==version.nid, self.TermNode.vid==version.vid)
        version_categories = [v.tid for v in version_categories_query if v.tid in self.zinnia_category_mapping]

        return Category.objects.filter(pk__in=[self.zinnia_category_mapping[tid] for tid in version_categories])

    def import_categories(self):
        """
        Imports the categories from Drupal into Zinnia. This includes full
        information about the category hierarchy.

        The method will set-up a number of required properties that are used
        later on for assigning blog entries to correct categories.
        """

        # Holds mapping between term IDs in Drupal and Zinnia Category IDs. This
        # allows for proper processing of identically-named categories across
        # multiple category hierarchy trees. Pairs are stored as (tid,
        # Category.id).
        self.zinnia_category_mapping = {}

        # Holds information about parent/child relatinships of Drupal categories
        # as (tid, tid) key/value pair.
        category_parents = {}

        # Fetch all category vocabularies.
        vocabularies = self.session.query(self.Vocabulary).filter(self.Vocabulary.tags!=1)

        # Set-up some counters.
        import_count = {}
        import_count["drupal_total"] = 0
        import_count["new"] = 0

        print "Starting import of categories."

        # Iterate over Drupal vocabularies. This will map into Zinnia
        # categories.
        for vocabulary in vocabularies:
            # Look-up the terms that belong to the vocabulary.
            term_query = self.session.query(self.TermData).filter(self.TermData.vid==vocabulary.vid)
            import_count["drupal_total"] += term_query.count()
            # Process each term item.
            for term in term_query:
                drupal_parent_id = self.session.query(self.TermHierarchy).filter(self.TermHierarchy.tid==term.tid).first().parent 

                # Construct a unique slug.
                slug_base = slugify(term.name)
                slug_number = 0
                slug = slug_base
                while Category.objects.filter(slug=slug).exists():
                    number += 1
                    slug = "%s%d" % (slug_base, number)

                # Create the category.
                category = Category(title=term.name, description=term.description, slug = slug)
                category.save()

                print "Added category '%s' with slug '%s'" % (term.name, slug)
                import_count["new"] += 1

                self.zinnia_category_mapping[term.tid] = category.pk
                category_parents[term.tid] = drupal_parent_id

        # Set-up Zinnia's category hierarchy.
        for tid, tid_parent in category_parents.iteritems():
            if tid_parent != 0:
                category = Category.objects.get(pk=self.zinnia_category_mapping[tid])
                category.parent = Category.objects.get(pk=self.zinnia_category_mapping[tid_parent])
                category.save()

        print "Total number of categories in Drupal: %d" % import_count["drupal_total"]
        print "Imported categories: %d" % import_count["new"]

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

        # Holds mapping between comment IDs in Drupal and Zinnia Comment
        # IDs. This is used later on if setting-up threaded comment parents.
        zinnia_comment_mapping = {}

        # Holds information about parent/child relatinships of Drupal comments
        # as (cid, cid) key/value pair.
        comment_parents = {}

        drupal_comments = self.session.query(self.Comments).filter(self.Comments.nid==drupal_node.nid).order_by(self.Comments.timestamp)

        # Set-up some counters.
        import_count = {}
        import_count["drupal_total"] = drupal_comments.count()
        import_count["new"] = 0

        print "Staring import of comments for '%s'" % drupal_node.title

        # Process all of the node's comments.
        for drupal_comment in drupal_comments:
            comment = Comment(comment=drupal_comment.comment,
                              ip_address=drupal_comment.hostname,
                              submit_date = datetime.fromtimestamp(drupal_comment.timestamp, pytz.UTC),
                              #@TODO: Add import of comment status?
                              #status
                              name=drupal_comment.name,
                              email=drupal_comment.mail,
                              user_url=drupal_comment.homepage,
                              content_object = zinnia_entry,
                              site_id = self.site.pk)
            comment.save()

            import_count["new"] += 1

            # Store parent/child information for threaded comments.
            zinnia_comment_mapping[drupal_comment.cid] = comment.pk
            comment_parents[drupal_comment.cid] = drupal_comment.pid

        # Update comment parent/child relationships if threaded comments were
        # enabled.
        if self.threaded_comments:
            for cid, cid_parent in comment_parents.iteritems():
                if cid_parent != 0:
                    comment = Comment.objects.get(pk=zinnia_comment_mapping[cid])
                    comment.parent = Comment.objects.get(pk=zinnia_comment_mapping[cid_parent])
                    comment.save()
            
        # Update the entry so that comment count and visibility will be fixed.
        zinnia_entry.comment_count = zinnia_entry.comments.count()
        zinnia_entry.pingback_count = zinnia_entry.pingbacks.count()
        zinnia_entry.trackback_count = zinnia_entry.trackbacks.count()
        zinnia_entry.save(force_update=True)

        print "Total number of comments in Drupal: %d" % import_count["drupal_total"]
        print "Imported comments: %d" % import_count["new"]


###########
# Command #
###########
class Command(LabelCommand):
    """
    Implements a custom Django management command used for importing Drupal blog
    into Zinnia.
    """

    help = """
Import a Drupal blog into Zinnia.

The command will import the following:

    - User information (username and mail only).

Currenlty the script has the following limitations:

    - No conversion of additional user information is performed.
    - No conversion of formatting is performed. Content is copied as-is.
    - Supports only MySQL-compatible database.
    - Revision history is not preserved (Django Blog Zinnia does not support
      revision history).
"""

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
                    help="List of Drupal users that should be imported, including their mapping to Zinnia users. Default is to import all user blogs with preserved usernames."),
        make_option("-t", "--threaded-comments", action="store_true",
                    default=False, dest="threaded_comments",
                    help="Import comments while preserving threading information. Requires zinnia-threaded-comments application."),
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

        importer = DrupalToZinnia(engine, options['node_type'], options['users'], options['threaded_comments'])
        importer.import_users()
        importer.import_categories()
        importer.import_content()

