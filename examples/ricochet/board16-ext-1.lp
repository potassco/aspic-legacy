% Plan horizon
%#const horizon=5.

% External target selection
%% #external goal(1).  % red moon:        9
%% #external goal(2).  % red triangle:   10
%% #external goal(3).  % green triangle:  9
%% #external goal(4).  % blue star:       8
%% #external goal(5).  % yellow star:    11
%% #external goal(6).  % blue saturn:     8
%% #external goal(7).  % green moon:      3
%% #external goal(8).  % yellow saturn:  13
%% #external goal(9).  % yellow moon:     2
%% #external goal(10). % green star:     11
%% #external goal(11). % red star:        9
%% #external goal(12). % green saturn:   11
%% #external goal(13). % yellow star:     9
%% #external goal(14). % blue star:       6
%% #external goal(15). % red saturn:      6 [5]
%% #external goal(16). % blue moon:      12

% External robot starting positions
#external pos((r;g;b;y),1..16,1..16).
col(red,r;green,g;blue,b;yellow,y).
position(C,X,Y) :- pos(CS,X,Y), col(C,CS), X = 1..16, Y=1..16.
