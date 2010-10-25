"""Search module with complex query parsing for zinnia"""
from pyparsing import Word
from pyparsing import Group
from pyparsing import Forward
from pyparsing import Combine
from pyparsing import Suppress
from pyparsing import Optional
from pyparsing import alphas
from pyparsing import alphanums
from pyparsing import OneOrMore
from pyparsing import StringEnd
from pyparsing import ZeroOrMore
from pyparsing import removeQuotes
from pyparsing import dblQuotedString
from pyparsing import CaselessLiteral

from django.db.models import Q

from zinnia.models import Entry


# Simple tokens
SIMPLE = Word(alphanums)
QUOTED = dblQuotedString.setParseAction(removeQuotes)
SINGLE = SIMPLE | QUOTED
SPECIAL = Combine(Word(alphas) + ":" + SINGLE | QUOTED)

# Recursive parenthetical groups
TERMS = Forward()
PARENTHETICAL = Suppress("(") + Group(TERMS) + Suppress(")")

# Negative terms
NEGATIVE = Combine("-" + (SPECIAL | SINGLE | PARENTHETICAL))

# Boolean operators
OPERATOR = CaselessLiteral("or") | CaselessLiteral("and")

# Bring it all together
TERM = SPECIAL | SINGLE | PARENTHETICAL | NEGATIVE
TERMS << TERM + ZeroOrMore(Optional(OPERATOR) + TERMS)
QUERY = OneOrMore(TERMS) + StringEnd()


def build_queryset(elements, level=0):
    """Build a queryset based on an grammar"""
    exprs = {}

    for elem in elements:
        if isinstance(elem, basestring):
            if elem in ('and', 'or'):
                continue
            if elem.startswith('category:'):
                pattern = elem.replace('category:', '')
                query_part = Q(categories__title__iexact=pattern) | \
                             Q(categories__slug__iexact=pattern)

            elif elem.startswith('tag:'):
                pattern = elem.replace('tag:', '')
                query_part = Q(tags__icontains=pattern)

            elif elem.startswith('author:'):
                pattern = elem.replace('author:', '')
                query_part = Q(authors__username__iexact=pattern)

            elif elem.startswith('-'):
                pattern = elem.replace('-', '')
                query_part = ~Q(content__icontains=pattern) & \
                             ~Q(excerpt__icontains=pattern) & \
                             ~Q(title__icontains=pattern)
            else:
                query_part = Q(content__icontains=elem) | \
                             Q(excerpt__icontains=elem) | \
                             Q(title__icontains=elem)
            exprs[elem] = query_part
        else:
            query_part = build_queryset(elem, level=level + 1)
            exprs[elem] = query_part

    lookup = None
    for i in range(len(elements)):
        elem = elements[i]
        if elem in exprs:
            query_part = exprs[elem]
        else:
            continue

        if lookup is None:
            lookup = query_part
        elif elements[i - 1] == 'or':
            lookup |= query_part
        else:
            lookup &= query_part

    if not level:
        return Entry.published.filter(lookup).distinct()
    return lookup


def advanced_search(pattern):
    """Parse the grammar of a pattern
    and build a queryset with it"""
    query_parsed = QUERY.parseString(pattern)
    return build_queryset(query_parsed)
