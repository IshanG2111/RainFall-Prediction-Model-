def get_neighbors(grid_id: int, n_cols: int = 120):
    neighbors = []
    row = (grid_id - 1) // n_cols
    col = (grid_id - 1) % n_cols

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if r >= 0 and c >= 0:
                neighbors.append(r * n_cols + c + 1)

    return neighbors