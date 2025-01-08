int: n;    % Number of rows
int: m;    % Number of columns

% The current configuration (1 means live, 0 means dead)
array[1..n, 1..m] of 0..1: current;

% The predecessor configuration to compute (1 means live, 0 means dead)
array[1..n, 1..m] of var 0..1: previous;

% Helper function to count the number of neighbors of a cell that are alive
function var int: live_neighbours_prev(int: i, int: j) =
    let {
        set of int: rows = {i-1, i, i+1} intersect 1..n,
        set of int: cols = {j-1, j, j+1} intersect 1..m
    } in
    sum([previous[r, c] | r in rows, c in cols where r != i \/ c != j]);

function var int: live_neighbours_curr(int: i, int: j) =
    let {
        set of int: rows = {i-1, i, i+1} intersect 1..n,
        set of int: cols = {j-1, j, j+1} intersect 1..m
    } in
    sum([current[r, c] | r in rows, c in cols where r != i \/ c != j]);


% Applying the Conway's Game of Life rules to relate the previous and current states
constraint
    forall(i in 1..n, j in 1..m) (
      (current[i, j] = 1 <-> % if the current cell is alive
      (
        (previous[i, j] == 1  /\ (live_neighbours_prev(i, j) == 2 \/ live_neighbours_prev(i, j) == 3)) \/ %it was alive and with only 2 or 3 live neighbours
        (previous[i, j] == 0  /\ live_neighbours_prev(i, j) == 3) %it was dead and with exactly 3 neighbours
      ))
      /\
      (current[i, j] = 0 <-> % if the current cell is dead
      (
        (previous[i, j] == 1  /\ (live_neighbours_prev(i, j) < 2 \/ live_neighbours_prev(i, j) > 3)) \/  %it was alive but with less than 2 or more than 3 live neighbours
        (previous[i, j] == 0  /\ live_neighbours_prev(i, j) != 3) %it was dead but didn't had 3 neighbours
      ))
    );

constraint
  forall(i in 1..n, j in 1..m) (
    live_neighbours_curr(i, j) == 0 -> previous[i, j] == 0
  );

solve :: restart_luby(100) satisfy;
