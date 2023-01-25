#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

import os
import itertools
import z3
import numpy as np

from dclasses import *

LitSort = z3.DeclareSort('LitSort')

LBFunc = z3.Function('lbtbl', z3.StringSort(), z3.StringSort(), z3.RealSort())

RadioRecord = z3.Datatype('RadioRecord')
RadioRecord.declare('make',
                    ('name', z3.StringSort()),
                    ('classtype', z3.StringSort()),
                    ('devtype', z3.StringSort()),
                    ('minfreq', z3.RealSort()),
                    ('maxfreq', z3.RealSort()),
                    ('maxbw', z3.RealSort()))
RadioRecord = RadioRecord.create()

GLOBAL_RADIO_VARS = ["bandwidth", "frequency"]

class FOLxFormer:
    def __init__(self):
        self.tsufcnts = {}
        self.idtable = {}
        self.assignments = {}
        self.user_clauses = []
        self.radios = {}
        self.lbdata = {}
        self.lbtable = []

    def get_bw_freq(self):
        bw = 0
        freq = 0
        if "bandwidth" in self.assignments:
            bw = self.assignments['bandwidth']
        if "frequency" in self.assignments:
            freq = self.assignments['frequency']
        return (bw, freq)
        
    # FIX: Frequency constraints w/o bandwidth.
    def global_radio_clauses(self, rad, bw, freq):
        clauses = []
        if bw > 0:
            clauses.append(RadioRecord.maxbw(rad) >= bw)
            if freq > 0:
                clauses.append(RadioRecord.minfreq(rad) <= freq - bw/2)
                clauses.append(RadioRecord.maxfreq(rad) >= freq + bw/2)
        return clauses
        
    def emit_solver(self):
        s = z3.Solver()
        bw, freq = self.get_bw_freq()
        for tname, cnt in self.tsufcnts.items():
            for vname, decls in self.idtable.items():
                if vname.startswith(tname):
                    s.add(z3.Distinct(decls))
                    for rval in decls:
                        rclauses = [rval == r for r in self.radios.values()]
                        if rclauses:
                            s.add(z3.Or(rclauses))
                        s.add(self.global_radio_clauses(rval, bw, freq))
        if bw and freq:
            self.calc_lbtable((freq - bw/2) * 1e6, (freq + bw/2) * 1e6)
            s.add(self.lbtable)
        s.add(self.user_clauses)
        return s
        
    def process_select(self, sel):
        for ofexp in sel.columns:
            self.process_ofexp(ofexp)
        for clause in sel.where:
            res = self.process_clause(clause)
            if res:
                self.user_clauses += res

    def process_ofexp(self, ofexp):
        iname = tname = ofexp.ident.name
        if not tname in self.tsufcnts:
            self.tsufcnts[tname] = 1
        else:
            self.tsufcnts[tname] += 1
            iname += "_%d" % self.tsufcnts[tname]
        vlist = []
        if tname in self.idtable and ofexp.count > len(self.idtable[tname]):
                raise RuntimeError("Count in 'of' expression larger than initially declared.")
        else:
            for i in range(1, ofexp.count+1):
                vn = "%s_%d" % (iname, i)
                vlist.append(RadioRecord.make(z3.String(vn), z3.String("%s_ct" % vn), z3.String("%s_dt" % vn), z3.Real("%s_mn" % vn), z3.Real("%s_mx" % vn), z3.Real("%s_bw" % vn)))
            self.idtable[iname] = vlist
        return [vlist]

    def process_clause(self, clause):
        compound_clauses = {
            IsaExpr: self.process_isa,
            BinOp: self.process_binop,
            Function: self.process_function,
            OfExpr: self.process_ofexp,
        }
        ctype = type(clause)
        ret = None
        if ctype in compound_clauses:
            ret = compound_clauses[ctype](clause)
        elif ctype == str:
            ret = [z3.StringVal(clause)]
        elif ctype == int:
            ret = [z3.IntVal(clause)]
        elif ctype == float:
            ret = [z3.RealVal(clause)]
        elif ctype == Identifier:
            if not clause.name in self.idtable:
                self.idtable[clause.name] = z3.Const(clause.name, LitSort)
            ret = [self.idtable[clause.name]]
        else:
            raise RuntimeError("Unhandled clause: %s" % clause)
        return ret

    # FIX: Need to propagate classification constraints to variables
    # instantiated later via OfExprs.
    def process_isa(self, isa):
        tvar = isa.ident.name
        ctype = self.process_clause(isa.expr)[0]
        rlist = []
        if tvar not in self.idtable:
            raise RuntimeError("Type variable not declared: %s" % tvar)
        for rec in self.idtable[tvar]:
            rlist.append(z3.Or(RadioRecord.classtype(rec) == ctype,
                               RadioRecord.devtype(rec) == ctype))
        return rlist

    def resolve_binop_argsort(self, lhs, rhs, op):
        LITSORTS = {
            z3.IntSort(): z3.Int,
            z3.RealSort(): z3.Real,
            z3.StringSort(): z3.String,
        }
        for first, s1, s2 in (("left", lhs, rhs), ("right", rhs, lhs)):
            argsort = s1[0].sort()
            if argsort in LITSORTS.keys():
                args = []
                for arg in s2:
                    if z3.is_const(arg) and arg.sort() == LitSort:
                        name = repr(arg)
                        arg = LITSORTS[argsort](name)
                        self.idtable[name] = arg
                        if op == '=':
                            if argsort in (z3.IntSort(), z3.RealSort()):
                                self.assignments[name] = s1[0].as_long()
                            else:
                                self.assignments[name] = s1[0].as_string()
                    args.append(arg)
                s2 = args
                return (s1, s2) if first == "left" else (s2, s1)
        raise RuntimeError("At least one argument to binary operators must resolve to a single integer, float, or string: %s/%s" % (lhs, rhs))

    def process_binop(self, binop):
        argsort = None
        lhs = self.process_clause(binop.left)
        rhs = self.process_clause(binop.right)
        op = binop.op
        lhs, rhs = self.resolve_binop_argsort(lhs, rhs, op)
        if op == '=':
            op = '=='
        ret = []
        for terms in itertools.product(lhs, rhs):
            ret.append(eval("terms[0] %s terms[1]" % op))
        return ret

    def process_function(self, fexpr):
        fname = fexpr.name.name
        if fname in self.FUNCS:
            func = self.FUNCS[fname]
        else:
            raise RuntimError("Unknown function called: %s" % fname)
        args = fexpr.args
        if type(args) == MapBinOp:
            args = self.process_mapbinop(args)
        else:
            nargs = []
            for arg in args:
                nargs.append(self.process_clause(arg)[0])
            args = nargs
        return func(self, args)

    # FIX: OfExprs not quite right.  Issue is with subsets vs. full set.
    def process_mapbinop(self, mbop):
        lhs = self.process_clause(mbop.left)[0]
        rhs = self.process_clause(mbop.right)[0]
        prod = None
        if mbop.op == "->":
            prod = list(itertools.product(lhs, rhs))
        elif mbop.op == "<-":
            prod = list(itertools.product(rhs, lhs))
        elif mbop.op == "<->":
            prod = list(itertools.product(lhs, rhs))
            prod += list(itertools.product(rhs, lhs))
        for pair in prod:
            # FIX: Rethink this...
            self.user_clauses.append(pair[0] != pair[1])
        return list(prod)

    def dummy_func(self, args):
        return args

    def link_budget_func(self, args):
        clauses = []
        for pair in args:
            clauses.append(LBFunc(RadioRecord.name(pair[0]),
                                  RadioRecord.name(pair[1])))
        return clauses

    def load_radio_records(self, records):
        for rec in records:
            self.radios[rec['name']] = \
                RadioRecord.make(
                    z3.StringVal(rec['name']), z3.StringVal(rec['cls']),
                    z3.StringVal(rec['type']), z3.RealVal(rec['minfreq']),
                    z3.RealVal(rec['maxfreq']), z3.RealVal(rec['bw']))

    def load_lbdata(self, data):
        self.lbdata = data

    def calc_lbtable(self, flo, fhi):
        lbfilt = {}
        for id1, rows in self.lbdata.items():
            if not id1 in lbfilt:
                lbfilt[id1] = {}
            for id2, lbrow in rows.items():
                if not id2 in lbfilt[id1]:
                    lbfilt[id1][id2] = []
                #print("[%s, %s] -> %s" % (id1, id2, lbrow))
                # FIX: This does not consider data gaps in the range!
                lbfilt[id1][id2] += [x[0] for x in lbrow if x[1] >= flo and x[1] <= fhi]
        for id1, rows in lbfilt.items():
            for id2, lbrow in rows.items():
                if not lbrow: continue
                lbval = np.mean(lbrow)
                decl = LBFunc(z3.StringVal(id1),
                              z3.StringVal(id2)) == \
                              z3.RealVal(lbval)
                self.lbtable.append(decl)
        for r1, r2 in  itertools.product(self.radios.keys(), self.radios.keys()):
            if not r1 in lbfilt or not r2 in lbfilt[r1]:
                self.lbtable.append(LBFunc(z3.StringVal(r1),
                                           z3.StringVal(r2)) == -100)

    FUNCS = {
        'Dummy': dummy_func,
        'LB': link_budget_func,
    }
