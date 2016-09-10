% Graph coloring

col(r;g;b).

1 {color(X,C) : col(C) } 1 :- node(X).
:- edge(X,Y), color(X,C), color(Y,C).

% User can determine color of a node
#external icolor(X,C) : node(X), col(C).
:- not color (X,C), icolor(X,C).

% User can add new edges to graph
#external edge(X,Y) : node (X), node(Y).

%#show color/2.
