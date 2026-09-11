"""
Risk-aware A* pathfinding algorithm for marine navigation.
Adapted from the ORCA navigation engine with NetworkX graph traversal.
"""

import math
from typing import Any, Dict, List
import networkx as nx


def find_safe_route(
    grid: List[List[dict]],
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> Dict[str, Any]:
    """Find optimal safe route using risk-aware A* pathfinding on a marine grid.

    Parameters:
    - grid: 2D list of grid cells with 'row', 'col', 'risk_score', and 'blocked'
    - start_row, start_col: Starting cell coordinates
    - end_row, end_col: Destination cell coordinates

    Returns:
    Dictionary containing path list, total_cost, and average_risk.
    """
    if not grid or not isinstance(grid, list) or not isinstance(grid[0], list):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": "Invalid grid structure provided.",
        }

    rows = len(grid)
    cols = len(grid[0])

    # 1. Bounds checking
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": f"Start position ({start_row}, {start_col}) is outside grid bounds.",
        }

    if not (0 <= end_row < rows and 0 <= end_col < cols):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": f"Destination position ({end_row}, {end_col}) is outside grid bounds.",
        }

    # 2. Blocked status checks for start and destination
    if grid[start_row][start_col].get("blocked", False):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": "Start position intersects a restricted marine zone or shoreline obstacle.",
        }

    if grid[end_row][end_col].get("blocked", False):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": "Destination position intersects a restricted marine zone or shallow reef.",
        }

    # Edge case: start == destination
    if start_row == end_row and start_col == end_col:
        risk = float(grid[start_row][start_col].get("risk_score", 0.0))
        return {
            "path": [{"row": start_row, "col": start_col}],
            "total_cost": 0.0,
            "average_risk": round(risk, 2),
        }

    # 3. Build directed graph using NetworkX
    G = nx.DiGraph()

    # 8-connected neighbor offsets (cardinal and diagonal navigation)
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ]

    for r in range(rows):
        for c in range(cols):
            current_cell = grid[r][c]
            if current_cell.get("blocked", False):
                continue

            u = (r, c)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor_cell = grid[nr][nc]
                    if neighbor_cell.get("blocked", False):
                        continue

                    v = (nr, nc)
                    # Euclidean step distance (1.0 for orthogonal, ~1.414 for diagonal)
                    step_distance = math.hypot(dr, dc)
                    dest_risk = float(neighbor_cell.get("risk_score", 0.0))

                    # Movement cost combines distance and environmental risk penalty
                    weight = step_distance * (1.0 + (dest_risk / 12.0))
                    G.add_edge(u, v, weight=weight)

    # 4. Grid-coordinate Euclidean distance heuristic
    def heuristic(u: tuple, v: tuple) -> float:
        return math.hypot(u[0] - v[0], u[1] - v[1])

    start_node = (start_row, start_col)
    end_node = (end_row, end_col)

    try:
        raw_path = nx.astar_path(
            G, source=start_node, target=end_node, heuristic=heuristic, weight="weight"
        )
        total_cost = nx.astar_path_length(
            G, source=start_node, target=end_node, heuristic=heuristic, weight="weight"
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {
            "path": [],
            "total_cost": 0.0,
            "average_risk": 0.0,
            "error": "No viable navigable corridor found between coordinates avoiding hazards.",
        }

    # 5. Format response
    path_list = [{"row": r, "col": c} for r, c in raw_path]
    total_risk = sum(float(grid[r][c].get("risk_score", 0.0)) for r, c in raw_path)
    avg_risk = round(total_risk / len(raw_path), 2) if raw_path else 0.0

    return {
        "path": path_list,
        "total_cost": round(total_cost, 2),
        "average_risk": avg_risk,
    }
