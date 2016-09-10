#!/usr/bin/env python

import clingo

def om(m):
    print "Model: " + str(m.atoms())

#init
prg=clingo.Control("0")
prg.add("base",[],"a.")
prg.ground([("base",[])])
print prg.solve(om, None)

prg.add("foo",[],"b")
prg.add("foo",[],"b.")
prg.ground([("foo",[])])
# print prg.solve(om, None)


