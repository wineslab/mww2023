#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# Parser for RF link matchmaking queries
#

import parsy

from dclasses import *

# Parsy definitions follow

SELECT = parsy.string('SELECT') | parsy.string('select')
OF = parsy.string('OF') | parsy.string('of')
ISA = parsy.regex(r'[iI][sS]\s+[aA][nN]?')
WHERE = parsy.string('WHERE') | parsy.string('where')

space = parsy.regex(r'\s+')
oparen = parsy.regex(r'\(\s*')
cparen = parsy.regex(r'\s*\)')
comma = parsy.regex(r'\s*,\s*')
semicolon = parsy.regex(r'\s*;\s*')

intLit = parsy.regex(r'(0|[1-9][0-9]*)').map(int).desc("integer")

floatLit = parsy.regex(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?').map(float).desc("floating point number")

singleQuoteString = parsy.regex(r"'[^']*'").map(lambda s: s[1:-1])
doubleQuoteString = parsy.regex(r'"[^"]*"').map(lambda s: s[1:-1])
strLit = (singleQuoteString | doubleQuoteString).desc("string")

identifier = parsy.regex(r'[a-zA-Z][a-zA-Z0-9_]*').map(Identifier).desc("identifier (variable)")

operator = parsy.string_from('=', '!=', '<', '>', '<=', '>=')

mapoper = parsy.string_from('->', '<-', '<->')

@parsy.generate
def function():
    fname = yield identifier
    yield oparen
    args = yield (mapping_binop | basic_expr.sep_by(comma))
    yield cparen
    return Function(fname, args)

function.desc("function call")

basic_expr = strLit | floatLit | function | identifier

isa_expr = parsy.seq(
    ident = identifier,
    _isastr = space + ISA + space,
    expr = strLit | function | identifier
).combine_dict(IsaExpr).desc("'IS A' binding")

binop_expr = parsy.seq(
    left = basic_expr,
    op = space.optional() >> operator << space.optional(),
    right = basic_expr
).combine_dict(BinOp).desc("operator expression")

of_expr = parsy.seq(
    count = intLit,
    _ofstr = space + OF + space,
    ident = identifier
).combine_dict(OfExpr).desc("'OF' quantifier")

map_expr = of_expr | function | identifier

mapping_binop = parsy.seq(
    left = map_expr,
    op = space.optional() >> mapoper << space.optional(),
    right = map_expr
).combine_dict(MapBinOp).desc("mapping expression")

where_expr = (isa_expr | binop_expr | basic_expr).sep_by(comma, min=1)

select = parsy.seq(
    _selectstr = space.optional() >> SELECT << space,
    columns = of_expr.sep_by(comma, min=1),
    _wherestr = space + WHERE + space,
    where = where_expr,
    _end = semicolon
).combine_dict(Select)
