% query({target(C,3,5), C = (red;green)},f,Q)
dim(1..16).
color(red;green;yellow;red).
1 { target(C,X,Y) : color(C), dim(X), dim(Y) } 1.
q :- target(C,3,5), C = (red;green) .
:- not q.
