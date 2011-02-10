"""Search module with complex query parsing for Zinnia"""

from pyparsing import Word, Optional, WordEnd, quotedString, printables, \
        CaselessLiteral, Combine, operatorPrecedence, opAssoc, OneOrMore, \
        StringEnd, removeQuotes, alphas, ParseResults

from django.db.models import Q
from zinnia.models import Entry


def createQ(token):
    "Creates the Q() object"

    meta = getattr(token, 'meta', None)
    query = getattr(token, 'query', '')
    wildcards = None

    # unicode -> Quoted string
    if isinstance(query, basestring):
        search = query

    # list -> No quoted string (possible wildcards)
    else:
        if len(query) == 1:
            search = query[0]
        elif len(query) == 3:
            wildcards = "BOTH"
            search = query[1]
        elif len(query) == 2:
            if query[0] == "*":
                wildcards = "START"
                search = query[1]
            else:
                wildcards = "END"
                search = query[0]

    if meta == "category":
        if wildcards == "BOTH":
            return Q(categories__title__icontains=search) | \
                    Q(categories__slug__icontains=search)
        elif wildcards == "START":
            return Q(categories__title__iendswith=search) | \
                    Q(categories__slug__iendswith=search)
        elif wildcards == "END":
            return Q(categories__title__istartswith=search) | \
                    Q(categories__slug__istartswith=search)
        else:
            return Q(categories__title__iexact=search) | \
                    Q(categories__slug__iexact=search)

    elif meta == "tag":  # TODO: tags ignore wildcards
        if wildcards == "BOTH":
            return Q(tags__icontains=search)
        elif wildcards == "START":
            return Q(tags__icontains=search)
        elif wildcards == "END":
            return Q(tags__icontains=search)
        else:
            return Q(tags__icontains=search)

    elif meta == "author":
        if wildcards == "BOTH":
            return Q(authors__username__icontains=search)
        elif wildcards == "START":
            return Q(authors__username__iendswith=search)
        elif wildcards == "END":
            return Q(authors__username__istartswith=search)
        else:
            return Q(authors__username__iexact=search)

    else:
        return Q(content__icontains=search) | \
                Q(excerpt__icontains=search) | \
                Q(title__icontains=search)


def unionQ(token):
    "Appends all the Q() objects"
    query = Q()
    operation = "and"
    negation = False

    for t in token:
        # See tokens recursively
        if type(t) is ParseResults:
            query &= unionQ(t)
        else:
            # Set the new op and go to next token
            if t in ("or", "and"):
                operation = t
            # Next tokens needs to be negated
            elif t == "-":
                negation = True
            # Append to query the token
            else:
                if negation:
                    t = ~t

                if operation == "or":
                    query |= t
                else:
                    query &= t

    return query


#
# Grammar
#

NO_BRTS = printables.replace("(", "").replace(")", "")
SINGLE = Word(NO_BRTS.replace("*", ""))
WILDCARDS = Optional("*") + SINGLE + Optional("*") + WordEnd(wordChars=NO_BRTS)
QUOTED = quotedString.setParseAction(removeQuotes)

OPER_AND = CaselessLiteral("and")
OPER_OR = CaselessLiteral("or")
OPER_NOT = "-"

TERM = Combine(Optional(Word(alphas).setResultsName("meta") + ":") + \
        (QUOTED.setResultsName("query") | WILDCARDS.setResultsName("query")))
TERM.setParseAction(createQ)

EXPRESSION = operatorPrecedence(TERM,
    [
        (OPER_NOT, 1, opAssoc.RIGHT),
        (OPER_OR, 2, opAssoc.LEFT),
        (Optional(OPER_AND, default="and"), 2, opAssoc.LEFT),
    ])
EXPRESSION.setParseAction(unionQ)

QUERY = OneOrMore(EXPRESSION) + StringEnd()
QUERY.setParseAction(unionQ)


def advanced_search(pattern):
    """Parse the grammar of a pattern
    and build a queryset with it"""
    query_parsed = QUERY.parseString(pattern)
    return Entry.published.filter(query_parsed[0]).distinct()
