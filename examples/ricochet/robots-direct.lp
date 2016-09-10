time(1..horizon).

dir(-1,0;1,0;0,-1;0,1).

stop( DX, DY,X,   Y   ) :- barrier(X,Y,DX,DY), dim(X), dim(Y), dim(X+DX), dim(Y+DY).
stop(-DX,-DY,X+DX,Y+DY) :- stop(DX,DY,X,Y).

position(R,X,Y,0) :- position(R,X,Y).

1 { move(R,DX,DY,T) : robot(R), dir(DX,DY) } 1 :- time(T).

halt(R,DX,DY,X,Y,T) :- robot(R), stop(DX,DY,X,Y), time(T).
halt(R,DX,DY,X,Y,T) :- robot(R), dir(DX,DY), position(RR,X+DX,Y+DY,T), R != RR, dim(X), dim(Y), dim(X+DX), dim(Y+DY).

goto(R,DX,DY,X+DX,Y+DY,T) :- position(R,X,Y,T-1), not halt(R,DX,DY,X,Y,T), dir(DX,DY), time(T), dim(X+DX), dim(Y+DY).
goto(R,DX,DY,X+DX,Y+DY,T) :- goto(R,DX,DY,X,Y,T), not halt(R,DX,DY,X,Y,T), dim(X+DX), dim(Y+DY).

stay(R,T) :- { move(R,DX,DY,T) : dir(DX,DY) } 0, robot(R), time(T).
stay(R,T) :- move(R,DX,DY,T), position(R,X,Y,T-1), not goto(R,DX,DY,X+DX,Y+DY,T).

position(R,X,Y,T) :- move(R,DX,DY,T), goto(R,DX,DY,X,Y,T), not goto(R,DX,DY,X+DX,Y+DY,T).
position(R,X,Y,T) :- position(R,X,Y,T-1), stay(R,T), time(T).

goon(T) :- target(R,X,Y), T = 0..horizon, not position(R,X,Y,T).
:- goon(horizon).

move(R,DX,DY,T) :- move(R,DX,DY,T-1), time(T), not goon(T-1).


#show move/4.
#show target/3.
%#show goon/1.
%#show goal/1.
%#show position/4.
