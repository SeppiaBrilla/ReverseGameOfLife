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

if __name__ == "__main__":
    board = [[0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]]

    for line in forward(board):
        print(line)
