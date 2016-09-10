#!/usr/bin/env python
import sys
import os

import queryasp.session
import queryasp.scops
import queryasp.queries

session = queryasp.session.Session(sys.stdout,
                                   [os.path.dirname(os.path.abspath('__file__')) + '/../tests/session/test1.lp'], ['0'])

def on_model(model):
    print "Model:" + model

def test1():
    prg = session.state.prg
    prg.ground([("base",[])])
    #prg.solve(on_model=on_model)
    with prg.solve_iter() as it:
        print
        for m in it:
            print "Model:"
            print m

def test2():
    lc = queryasp.scops.Load(session, sys.stdout)
    lc.command_data = {}
    lc.command_data ['bla']= 'blub'
    print lc.command_data

def test3():
    session2 = queryasp.session.Session(sys.stdout,
                                        [os.path.dirname(os.path.abspath('__file__')) + '/../tests/session/test1.lp'],
                                        ['0'])
    o1 = queryasp.scops.Assert(session, sys.stdout)
    o2 = queryasp.scops.Assert(session2, sys.stdout)
    print session, session2
    print o1, o2

test3()
