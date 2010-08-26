"""Search module with complex query parsing for zinnia"""
from pyparsing import *

from django.db.models import Q

from zinnia.models import Entry


# Simple tokens
simple = Word(alphanums)
quoted = dblQuotedString.setParseAction(removeQuotes)
single = simple | quoted
special = Combine(Word(alphas) + ":" + single | quoted)

# Recursive parenthetical groups
terms = Forward()
parenthetical = Suppress("(") + Group(terms) + Suppress(")")

# Negative terms
negative = Combine("-" + (special | single | parenthetical))

# Boolean operators
operator = CaselessLiteral("or") | CaselessLiteral("and")

# Bring it all together
term = special | single | parenthetical | negative
terms << term + ZeroOrMore(Optional(operator) + terms)
query = OneOrMore(terms) + StringEnd()

def build_queryset(elements, level=0):
    """Build a queryset based on an grammar"""
    exprs = {}

    for elem in elements:
        if isinstance(elem, basestring):
            if elem in ('and', 'or'):
                continue
            if elem.startswith('category:'):
                p = elem.replace('category:', '')
                q = Q(categories__title__iexact=p) | \
                    Q(categories__slug__iexact=p)

            elif elem.startswith('tag:'):
                p = elem.replace('tag:', '')
                q = Q(tags__icontains=p)

            elif elem.startswith('author:'):
                p = elem.replace('author:', '')
                q = Q(authors__username__iexact=p)

            elif elem.startswith('-'):
                p = elem.replace('-', '')
                q = ~Q(content__icontains=p) & \
                    ~Q(excerpt__icontains=p) & \
                    ~Q(title__icontains=p)
            else:
                q = Q(content__icontains=elem) | \
                    Q(excerpt__icontains=elem) | \
                    Q(title__icontains=elem)
            exprs[elem] = q
        else:
            q = build_queryset(elem, level=level + 1)
            exprs[elem] = q

    lookup = None
    for i in range(len(elements)):
        elem = elements[i]
        if elem in exprs:
            q = exprs[elem]
        else:
            continue

        if lookup is None:
            lookup = q
        elif elements[i - 1] == 'or':
            lookup |= q
        else:
            lookup &= q

    if not level:
        return Entry.published.filter(lookup).distinct()
    return lookup

def advanced_search(pattern):
    """Parse the grammar of a pattern
    and build a queryset with it"""
    query_parsed = query.parseString(pattern)
    return build_queryset(query_parsed)
