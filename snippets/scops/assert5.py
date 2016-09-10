#!/usr/bin/env python

import clingo

def om(m):
    print "Model: " + str(m.atoms())

#init
prg=clingo.Control("0")
#prg.add("base",[],"")
prg.ground([("base",[])])
print prg.solve(om, None)

prg.add("p1", [], "atom :- ext. #external ext.")
prg.ground([("p1", [])])

prg.assign_external(clingo.Function("ext"), True)
print prg.solve(om, None)

prg.assign_external(clingo.Function("ext"), True)
print prg.solve(om, None)

prg.assign_external(clingo.Function("ext"), False)
print prg.solve(om, None)

prg.assign_external(clingo.Function("ext"), True)
print prg.solve(om, None)

