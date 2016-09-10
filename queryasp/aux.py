# -*- coding: utf-8 -*-

from __future__ import print_function
import re
from functools import partial
from importlib import import_module

#TODO:
# - Introduce most general commands class
# - Make all commands here and all scops, queries

DEBUG = False

def debug(msg, desc=''):
    if DEBUG:
        print("DEBUG({0}): {1}".format(desc, msg))


def _on_model(model, show_preds, output_on_model):
    stratomlist = []
    for ggfun in model.symbols(True):
        if not len(show_preds) or _match_to_show(str(ggfun), show_preds): # considers predicates to show if given
            if DEBUG:
                stratomlist.append(str(ggfun))
            elif not str(ggfun).startswith('_'): # omitting atoms with underscore suffix
                stratomlist.append(str(ggfun))
    stratomlist.sort()
    debug("Model: [" + ", ".join(stratomlist)+ "]", '_on_model')
    output_on_model.append("Model: [" + ", ".join(stratomlist)+ "]")
    if len(model.cost):
        output_on_model.append("  Optimization cost: {0}".format(str(model.cost)))


def _match_to_show(atom, show_preds): #TODO arity ignored atm
    """Match atom to predicate signatures to show."""
    RE_RELSIG = re.compile(r'(\w+)(/(\d+))?')
    for relsig in show_preds:
        name = RE_RELSIG.match(relsig).group(1)
        arity = RE_RELSIG.match(relsig).group(3)
        # print (name)
        # print (arity)
        re_atom = re.compile(name + r'(\(.*\))?$')
        if re_atom.match(atom):
            return True
    return False


def on_model(show_preds, output_on_model):
    """Session-dependent on_model function for clingo.Control.solve()."""
    return partial(_on_model, show_preds=show_preds, output_on_model=output_on_model)

def on_finish(result):
    print(result)
#    print(cancelled)

def args2cmd_confs(args):
    """Wraps argparser args related to aspic commands into custom_cmd_confs dict."""
    cmd_confs = {}
    #TODO: implement if needed for later cl args
    return cmd_confs
