#!/usr/bin/env python

import clingo

def om(m):
    print "Model: " + str(m.atoms())

#init
prg=clingo.Control("0")
#prg.add("base",[],"")
prg.ground([("base",[])])
print prg.solve(om, None)

# prg.add("p1", [], "atom :- ext. #external ext.")
prg.add("p1", [], "{atom}. :- atom, not ext.  #external ext.")
prg.ground([("p1", [])])
prg.assign_external(clingo.Function("ext"), True)
print prg.solve(om, None)

prg.release_external(clingo.Function("ext"))
print prg.solve(om, None)

#prg.add("p2", [], "atom :- atom2. atom2 :- ext2. #external ext2.")
prg.add("p2", [], ":- atom, not ext2. #external ext2.")
prg.ground([("p2", [])])
prg.assign_external(clingo.Function("ext2"), True)
print prg.solve(om, None)

# prg.add("p3", [], ":- not atom.")
# prg.ground([("p3", [])])
# print prg.solve(om, None)

