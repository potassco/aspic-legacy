#!/usr/bin/env python

import clingo

def om(m):
    print "Model: " + str(m.atoms())

#init
prg=clingo.Control("0")
#prg.add("base",[],"")
prg.ground([("base",[])])
print prg.solve(om, None)

step = "3"
enc_name = step + "_assertion"
#ext = "_ext"
ext = "_ext_{0}".format(step)
prg.add(enc_name, [], "atom :- {0}. #external {0}.".format(ext))
prg.ground([(enc_name, [])])
prg.assign_external(clingo.Function(ext), True)
print prg.solve(om, None)

prg.release_external(clingo.Function(ext))
print prg.solve(om, None)
prg.release_external(clingo.Function(ext))
print prg.solve(om, None)
