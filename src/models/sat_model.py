from z3.z3 import Bool, Not, And, Or, Implies, Solver, sat, PbEq, PbGe, PbLe
from math import ceil, log2
import uuid
import numpy as np

def get_next_state(current_value:int, neigbours:int) -> int:
    if current_value == 1:
        if neigbours == 2 or neigbours == 3:
            return 1
        return 0
    else:
        if neigbours == 3:
            return 1
        return 0 


def forward(board:list[list[int]]) -> list[list[int]]:
    neibs = [(-1,  1), (0,  1), (1,  1),
             (-1,  0),          (1,  0),
             (-1, -1), (0, -1), (1, -1)]

    cols = len(board)
    rows = len(board[0])

    new_board = [[0 for _ in range(rows)] for _ in range(cols)]

    for i in range(cols):
        for j in range(rows):
            current_neib = 0
            for (h, w) in neibs:
                if i + h < cols and j + w < rows and i + h > -1 and j + w > -1:
                    current_neib += board[i + h][j + w]
            new_board[i][j] = get_next_state(board[i][j], current_neib)
    return new_board

def at_most_one(bool_vars):
    return at_most_k(bool_vars, 1)

def at_least_one(bool_vars):
    return Or(bool_vars)

def exactly_one(bool_vars):
    return exactly_k(bool_vars, 1)

def at_most_k(bool_vars, k):
    if k >= len(bool_vars):
        return True
    return PbLe(tuple([(b,1) for b in bool_vars]), k)

def at_least_k(bool_vars,k):
    if k >= len(bool_vars):
        return False
    return PbGe(tuple([(b,1) for b in bool_vars]), k)

def exactly_k(bool_vars,k):
    return PbEq(tuple([(b,1) for b in bool_vars]), k)

def neibs(board, i,j):
    m = len(board)
    n = len(board[0])
    c_neibs = []
    for k in range(-1,2):
        for l in range(-1,2):
            if k == 0 and l == 0:
                continue
            if i + k >= 0 and i + k < m and j + l >= 0 and j + l < n:
                c_neibs.append(board[i + k][j + l])      
    return c_neibs

def reverse_gol(current:list,steps:int) -> tuple[list[list[list[int]]], bool]:
    previous = np.array([[[Bool(f'prev({i},{j}-{s})') for j in range(len(current[0]))] for i in range(len(current))] for s in range(steps)])
    s = Solver()
    for i in range(len(current)):
        for j in range(len(current[0])):
            neighbours = neibs(previous[steps - 1], i,j)
            # print(neighbours, i,j, current[i][j] == 1)
            if current[i][j] == 1:
                s.add(Or([
                    And([
                        previous[steps - 1, i, j], 
                        at_least_k(neighbours, 2), 
                        at_most_k(neighbours, 3)
                    ]),
                    And([
                        Not(previous[steps - 1, i, j]), 
                        exactly_k(neighbours, 3)
                    ])
                ]))
            else:
                assert current[i][j] == 0, f'inconsistent value {current[i][j]}'
                s.add(Or([
                    And([
                        previous[steps - 1, i, j], 
                        Or([
                            at_least_k(neighbours, 4), 
                            at_most_one(neighbours)
                        ])
                    ]),
                    And([
                        Not(previous[steps - 1, i, j]), 
                        Not(exactly_k(neighbours, 3))
                    ])
                ]))
            for step in range(steps - 1):
                neighbours = neibs(previous[step], i,j)
                s.add(previous[step + 1, i, j] == Or([
                        And([
                            previous[step, i, j], 
                            at_least_k(neighbours, 2), 
                            at_most_k(neighbours, 3)
                        ]),
                        And([
                            Not(previous[step][i][j]), 
                            exactly_k(neighbours, 3)
                        ])
                    ])
                )
                s.add(Not(previous[step + 1, i, j]) == Or([
                        And([
                            previous[step][i][j], 
                            Or([
                                at_least_k(neighbours, 4), 
                                at_most_one(neighbours)
                            ])
                        ]),
                        And([
                            Not(previous[step][i][j]), 
                            Not(exactly_k(neighbours, 3))
                        ])
                    ])
                )
    if s.check() == sat:
        model = s.model()
        solution = np.zeros_like(previous)
        steps, m, n = solution.shape
        for step in range(steps):
            for i in range(m):
                for j in range(n):
                    if model.evaluate(previous[step,i,j]):
                        solution[step,i,j] = 1
        return solution.tolist(), True
    return [], False

def print_board(board):
    steps, m, _ = np.array(board).shape
    for s in range(steps):
        print(f'{"-"*100}\nstep: {s}')
        for i in range(m):
            print(''.join([str(b) for b in board[s][i]]))

if __name__ == "__main__":
    inst = [[0, 1, 0], 
            [0, 1, 0], 
            [0, 1, 0]]
    sol, _ = reverse_gol(inst, 8)
    print_board(sol)
