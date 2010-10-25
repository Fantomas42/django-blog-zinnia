"""XML-RPC methods for Zinnia"""


ZINNIA_XMLRPC_PINGBACK = [
    ('zinnia.xmlrpc.pingback.pingback_ping',
     'pingback.ping'),
    ('zinnia.xmlrpc.pingback.pingback_extensions_get_pingbacks',
     'pingback.extensions.getPingbacks')]

ZINNIA_XMLRPC_METAWEBLOG = [
    ('zinnia.xmlrpc.metaweblog.get_users_blogs',
     'blogger.getUsersBlogs'),
    ('zinnia.xmlrpc.metaweblog.get_user_info',
     'blogger.getUserInfo'),
    ('zinnia.xmlrpc.metaweblog.delete_post',
     'blogger.deletePost'),
    ('zinnia.xmlrpc.metaweblog.get_authors',
     'wp.getAuthors'),
    ('zinnia.xmlrpc.metaweblog.get_categories',
     'metaWeblog.getCategories'),
    ('zinnia.xmlrpc.metaweblog.new_category',
     'wp.newCategory'),
    ('zinnia.xmlrpc.metaweblog.get_recent_posts',
     'metaWeblog.getRecentPosts'),
    ('zinnia.xmlrpc.metaweblog.get_post',
     'metaWeblog.getPost'),
    ('zinnia.xmlrpc.metaweblog.new_post',
     'metaWeblog.newPost'),
    ('zinnia.xmlrpc.metaweblog.edit_post',
     'metaWeblog.editPost'),
    ('zinnia.xmlrpc.metaweblog.new_media_object',
     'metaWeblog.newMediaObject')]

ZINNIA_XMLRPC_METHODS = ZINNIA_XMLRPC_PINGBACK + ZINNIA_XMLRPC_METAWEBLOG
