int: n;    % Number of rows
int: m;    % Number of columns
int: steps; %number of backward steps to take

% The current configuration (1 means live, 0 means dead)
array[1..n, 1..m] of 0..1: current;

% The predecessor configurations to compute (1 means live, 0 means dead)
array[1..steps, 1..n, 1..m] of var 0..1: previous;

% Helper functions to count the number of neighbours of a cell that are alive
function var int: live_neighbours_prev(int: i, int: j, int: s) =
    let {
        set of int: rows = {i-1, i, i+1} intersect 1..n,
        set of int: cols = {j-1, j, j+1} intersect 1..m
    } in
    sum([previous[s, r, c] | r in rows, c in cols where r != i \/ c != j]);

function var int: live_neighbours_curr(int: i, int: j) =
    let {
        set of int: rows = {i-1, i, i+1} intersect 1..n,
        set of int: cols = {j-1, j, j+1} intersect 1..m
    } in
    sum([current[r, c] | r in rows, c in cols where r != i \/ c != j]);


constraint
    forall(i in 1..n, j in 1..m) (
      (current[i, j] == 1 <-> % if the current cell is alive
      (
        (previous[steps, i, j] == 1  /\ (live_neighbours_prev(i, j, steps) == 2 \/ live_neighbours_prev(i, j, steps) == 3)) \/ %it was alive and with only 2 or 3 live neighbours
        (previous[steps, i, j] == 0  /\ live_neighbours_prev(i, j, steps) == 3) %it was dead and with exactly 3 neighbours
      ))
     /\
     (current[i, j] == 0 <-> % if the current cell is dead
     (
        (previous[steps, i, j] == 1  /\ (live_neighbours_prev(i, j, steps) < 2 \/ live_neighbours_prev(i, j, steps) > 3)) \/  %it was alive but with less than 2 or more than 3 live neighbours
        (previous[steps, i, j] == 0  /\ live_neighbours_prev(i, j, steps) != 3) %it was dead but didn't had 3 neighbours
     ))
    );

% Applying Conway's Game of Life rules to relate the previous states
constraint
    forall(i in 1..n, j in 1..m, s in 1..steps-1) (
      (previous[s+1, i, j] == 1 <-> % if the current cell is alive
      (
        (previous[s, i, j] == 1  /\ (live_neighbours_prev(i, j, s) == 2 \/ live_neighbours_prev(i, j, s) == 3)) \/ %it was alive and with only 2 or 3 live neighbours
        (previous[s, i, j] == 0  /\ live_neighbours_prev(i, j, s) == 3) %it was dead and with exactly 3 neighbours
      ))
     /\
     (previous[s+1, i, j] == 0 <-> % if the current cell is dead
     (
        (previous[s, i, j] == 1  /\ (live_neighbours_prev(i, j, s) < 2 \/ live_neighbours_prev(i, j, s) > 3)) \/  %it was alive but with less than 2 or more than 3 live neighbours
        (previous[s, i, j] == 0  /\ live_neighbours_prev(i, j, s) != 3) %it was dead but didn't had 3 neighbours
     ))
    );

constraint %constraint to avoid setting alive cells that we don't care about
  forall(i in 1..n, j in 1..m) (
    live_neighbours_curr(i, j) == 0 -> previous[steps, i, j] == 0 
    /\
    forall(s in 1..steps-1) (
      live_neighbours_prev(i, j, s+1) == 0 -> previous[s, i, j] == 0
    )
  );
constraint 
  forall(s in 1..steps)(
    sum(previous[s, 1..n, 1..m]) > 0
  );

solve :: restart_luby(100) satisfy;
