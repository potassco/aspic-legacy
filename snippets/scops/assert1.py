#!/usr/bin/env python

import clingo

def om(m):
    print "Model: " + str(m.atoms())

#init
prg=clingo.Control("0")
prg.add("base",[],"{a}. b :- a. #external base_e.")
prg.ground([("base",[])])
prg.assign_external(clingo.Function("base_e"), True)
print prg.solve(om, None)

#assert new_e1
print "?- assert new_e1."
prg.add("ext1",[],"#external new_e1.")
prg.ground([("ext1",[])])
prg.assign_external(clingo.Function("new_e1"), True)
print prg.solve(om, None)

#assert new_e2.
print "?- assert new_e2."
prg.add("ext2",[],"#external new_e2.")
prg.ground([("ext2",[])])
prg.assign_external(clingo.Function("new_e2"), True)
print prg.solve(om, None)

#retract new_1.
print "?- retract new_1."
prg.release_external(clingo.Function("new_e1"))
print prg.solve(om, None)
