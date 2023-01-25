#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

# Data classes used in parsing

class Identifier:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "Identifier(name=%s)" % self.name

class Function:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return "Function(name=%s, args=%s)" % (self.name, self.args)

class BinOp:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op
    def __repr__(self):
        return "BinOp(left=%s, right=%s, op=%s)" % (self.left, self.right, self.op)

class MapBinOp:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op
    def __repr__(self):
        return "MapBinOp(left=%s, right=%s, op=%s)" % (self.left, self.right, self.op)
        
class IsaExpr:
    def __init__(self, ident, expr):
        self.ident = ident
        self.expr = expr
    def __repr__(self):
        return "IsaExpr(ident=%s, expr=%s)" % (self.ident, self.expr)

class OfExpr:
    def __init__(self, count, ident):
        self.count = count
        self.ident = ident
    def __repr__(self):
        return "OfExpr(count=%d, ident=%s)" % (self.count, self.ident)

class Select:
    def __init__(self, columns, where):
        self.columns = columns
        self.where = where
    def __repr__(self):
        return "Select(columns=%s, where=%s)" % (self.columns, self.where)
