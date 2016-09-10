% query({target(C,1,2), C = (red;green)},f,Q)
dim(1..16).
color(red;green;yellow;red).
1 { target(C,X,Y) : color(C), dim(X), dim(Y) } 1.
q :- target(C,1,2), C = (red;green) .
:- not q.
