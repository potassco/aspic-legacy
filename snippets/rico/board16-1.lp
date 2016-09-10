% Authentic board from Ricochet Robots (Rasende Roboter) by Alex Randolph

dim(1..16).

% the board
barrier( 2, 1, 1,0).
barrier(10, 1, 1,0).
barrier( 4, 2, 1,0).
barrier(14, 2, 1,0).
barrier( 2, 3, 1,0).
barrier(11, 3, 1,0).
barrier( 7, 4, 1,0).
barrier( 3, 7, 1,0).
barrier(14, 7, 1,0).
barrier( 7, 8, 1,0). % middle
barrier(10, 8,-1,0). % middle
barrier(11, 8, 1,0).
barrier( 7, 9, 1,0). % middle
barrier(10, 9,-1,0). % middle
barrier( 4,10, 1,0).
barrier( 2,11, 1,0).
barrier( 8,11, 1,0).
barrier(13,11, 1,0).
barrier(11,12, 1,0).
barrier(14,13, 1,0).
barrier( 6,14, 1,0).
barrier( 3,15, 1,0).
barrier(10,15, 1,0).
barrier( 4,16, 1,0).
barrier(12,16, 1,0).

barrier( 5, 1,0, 1).
barrier(15, 1,0, 1).
barrier( 2, 2,0, 1).
barrier(12, 3,0, 1).
barrier( 7, 4,0, 1).
barrier(16, 4,0, 1).
barrier( 1, 6,0, 1).
barrier( 4, 7,0, 1).
barrier( 8, 7,0, 1). % middle
barrier( 9, 7,0, 1). % middle
barrier(11, 7,0, 1).
barrier(14, 7,0, 1).
barrier(16, 9,0, 1).
barrier( 2,10,0, 1).
barrier( 5,10,0, 1).
barrier( 8,10,0,-1). % middle
barrier( 9,10,0,-1). % middle
barrier( 9,10,0, 1).
barrier(14,10,0, 1).
barrier( 1,12,0, 1).
barrier(11,12,0, 1).
barrier( 7,13,0, 1).
barrier(15,13,0, 1).
barrier(10,14,0, 1).
barrier( 3,15,0, 1).

% available targets
target(red,    5, 2) :- goal(1).  % red moon:        9
target(red,   15, 2) :- goal(2).  % red triangle:   10
target(green,  2, 3) :- goal(3).  % green triangle:  9
target(blue,  12, 3) :- goal(4).  % blue star:       8
target(yellow, 7, 4) :- goal(5).  % yellow star:    11
target(blue,   4, 7) :- goal(6).  % blue saturn:     8
target(green, 14, 7) :- goal(7).  % green moon:      3
target(yellow,11, 8) :- goal(8).  % yellow saturn:  13
target(yellow, 5,10) :- goal(9).  % yellow moon:     2
target(green,  2,11) :- goal(10). % green star:     11
target(red,   14,11) :- goal(11). % red star:        9
target(green, 11,12) :- goal(12). % green saturn:   11
target(yellow,15,13) :- goal(13). % yellow star:     9
target(blue,   7,14) :- goal(14). % blue star:       6
target(red,    3,15) :- goal(15). % red saturn:      6 [5]
target(blue,  10,15) :- goal(16). % blue moon:      12

{goal(1..16)} 1.

% available robots
robot(red;green;blue;yellow).

