import networkx as nx
from typing import Optional
from collections import deque

def dfs_path(G: nx.Graph, start: str, end: str) -> Optional[list]:
    """
    Depth-First Search path (not guaranteed shortest).

    Uses:
        - stack (LIFO)
        - visited set
        - parent dict for path reconstruction
    """
    if start not in G or end not in G:
        return None

    stack = [start]
    visited = {start}
    parent = {start: None}

    while stack:
        current = stack.pop()

        if current == end:
            # Reconstruct path from target back to source
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    return None  # no path


def bfs_path(G: nx.Graph, start: str, end: str) -> Optional[list]:
    """
    Breadth-First Search path (unweighted shortest path by number of edges).

    Uses:
        - queue (FIFO)
        - visited set
        - parent dict for path reconstruction
    """
    if start not in G or end not in G:
        return None

    queue = deque([start])
    visited = {start}
    parent = {start: None}

    while queue:
        current = queue.popleft()

        if current == end:
            # Reconstruct path from target back to source
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None  # no path


def compare_paths(path1: Optional[list], path2: Optional[list], G: nx.Graph) -> dict:
    """
    Compare two paths and return statistics.
    
    Args:
        path1: First path (e.g., from DFS)
        path2: Second path (e.g., from BFS)
        G: Graph for additional analysis
    
    Returns:
        Dictionary with comparison results
    """
    result = {
        "path1_length": len(path1) if path1 else None,
        "path2_length": len(path2) if path2 else None,
        "path1": path1,
        "path2": path2,
        "same_path": path1 == path2 if (path1 and path2) else False,
        "path1_exists": path1 is not None,
        "path2_exists": path2 is not None,
    }
    
    if path1 and path2:
        result["length_difference"] = len(path1) - len(path2)
        result["path1_edges"] = len(path1) - 1
        result["path2_edges"] = len(path2) - 1
    else:
        result["length_difference"] = None
        result["path1_edges"] = None
        result["path2_edges"] = None
    
    return result