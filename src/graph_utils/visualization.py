import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np


def make_route_color_map(routes: pd.DataFrame, default="#999999") -> dict:
    """
    Map route_id -> matplotlib color string.
    GTFS route_color is hex without leading '#'.
    """
    color_map = {}
    for _, row in routes.iterrows():
        route_id = row["route_id"]
        col = row.get("route_color", "")
        
        # Check for NaN or empty values
        if pd.isna(col) or (isinstance(col, str) and col.strip() == ""):
            color_map[route_id] = default
            continue
            
        col = str(col).strip()
        # Validate hex color format (3 or 6 hex digits)
        if len(col) in (3, 6) and all(c in "0123456789ABCDEFabcdef" for c in col):
            color_map[route_id] = "#" + col
        else:
            color_map[route_id] = default
    return color_map

def plot_hvv_graph(
    G: nx.Graph,
    routes: pd.DataFrame,
    route_ids: list[str] | None = None,
    use_geo_coords: bool = True,
    title: str = "HVV network",
    show_legend: bool = True,
    curve_radius: float = 0.0006,
):
    """
    Draw graph with curved edges for parallel routes and legend.
    """
    # Positions
    if use_geo_coords:
        pos = {n: (G.nodes[n]["lon"], G.nodes[n]["lat"]) for n in G.nodes}
    else:
        pos = nx.spring_layout(G, seed=42, k=0.3)

    # Route colors only for actually used routes
    if route_ids is None:
        route_ids = sorted({
            rid
            for _, _, data in G.edges(data=True)
            for rid in data.get("route_ids", [])
        })

    routes_for_plot = routes[routes["route_id"].isin(route_ids)].copy()
    route_color = make_route_color_map(routes_for_plot)
    
    # Create route name mapping for legend
    route_names = {}
    for _, row in routes_for_plot.iterrows():
        route_id = row["route_id"]
        route_short_name = row.get("route_short_name", "")
        route_long_name = row.get("route_long_name", "")
        if route_short_name and not pd.isna(route_short_name):
            route_names[route_id] = str(route_short_name)
        elif route_long_name and not pd.isna(route_long_name):
            route_names[route_id] = str(route_long_name)[:30]
        else:
            route_names[route_id] = route_id

    plt.figure(figsize=(14, 10))
    ax = plt.gca()
    plt.title(title, fontsize=14, pad=20)

    # Group edges by (u, v) to detect parallel routes
    edge_routes = {}
    for u, v, data in G.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key not in edge_routes:
            edge_routes[edge_key] = []
        edge_routes[edge_key].extend(list(data.get("route_ids", set())))

    # Draw edges per route with curves for parallel routes
    legend_handles = []
    drawn_edges = set()  # Track drawn edges to avoid duplicates
    
    for idx, rid in enumerate(route_ids):
        edges_for_route = [
            (u, v)
            for u, v, data in G.edges(data=True)
            if rid in data.get("route_ids", set())
        ]
        if not edges_for_route:
            continue

        color = route_color.get(rid, "#999999")
        
        for u, v in edges_for_route:
            edge_key = tuple(sorted([u, v]))
            parallel_routes = edge_routes[edge_key]
            route_index = parallel_routes.index(rid) if rid in parallel_routes else 0
            num_parallel = len(set(parallel_routes))
            
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Calculate perpendicular offset for curve
            dx = x2 - x1
            dy = y2 - y1
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0 and num_parallel > 1:
                # Perpendicular vector
                perp_x = -dy / length
                perp_y = dx / length
                
                # Offset based on route index
                offset = (route_index - (num_parallel - 1) / 2) * curve_radius
                
                # Control point for quadratic curve (midpoint with offset)
                mid_x = (x1 + x2) / 2 + perp_x * offset
                mid_y = (y1 + y2) / 2 + perp_y * offset
                
                # Draw curved line
                t = np.linspace(0, 1, 50)
                curve_x = (1 - t)**2 * x1 + 2 * (1 - t) * t * mid_x + t**2 * x2
                curve_y = (1 - t)**2 * y1 + 2 * (1 - t) * t * mid_y + t**2 * y2
                
                ax.plot(curve_x, curve_y, color=color, linewidth=1.8, alpha=0.9, zorder=1)
            else:
                # Straight line for single route
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.8, alpha=0.9, zorder=1)

        # Add to legend (only once per route)
        if rid not in drawn_edges:
            legend_handles.append(
                mpatches.Patch(color=color, label=route_names.get(rid, rid))
            )
            drawn_edges.add(rid)

    # Nodes: transfer vs regular
    transfer_nodes = [n for n, d in G.nodes(data=True) if d.get("transfer", False)]
    regular_nodes = [n for n in G.nodes if n not in transfer_nodes]

    nx.draw_networkx_nodes(
        G, pos, nodelist=regular_nodes,
        node_size=25, node_color="#1f78b4", alpha=0.9,
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=transfer_nodes,
        node_size=80, node_color="#ff7f00", alpha=0.95,
    )
    nx.draw_networkx_labels(
        G, pos,
        labels={n: n for n in transfer_nodes},
        font_size=6,
    )

    # Add legend
    if show_legend and legend_handles:
        max_legend_items = 30
        legend_handles.sort(key=lambda x: x.get_label())
        if len(legend_handles) > max_legend_items:
            legend_handles = legend_handles[:max_legend_items]
            legend_handles.append(
                mpatches.Patch(color='white', label=f'...and also {len(route_ids) - max_legend_items} routes')
            )
        
        plt.legend(
            handles=legend_handles,
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            fontsize=8,
            framealpha=0.9,
            title="U-Bahn Linies",
            title_fontsize=10,
        )

    plt.axis("off")
    plt.tight_layout()
    plt.show()


def build_route_segments(
    G: nx.Graph,
    path: list,
    routes: pd.DataFrame,
) -> list[str]:
    """
    Build a list of route segments in the format:
    ["Station - Line - Station", "Station - Line - Station", ...]
    
    Args:
        G: Graph
        path: List of path nodes
        routes: DataFrame with route information
    
    Returns:
        List of route segments as strings
    """
    if not path or len(path) < 2:
        return ["Path not found"]
    
    # create a dictionary route_id -> route_short_name
    route_names = {}
    for _, row in routes.iterrows():
        route_id = row["route_id"]
        route_short_name = row.get("route_short_name", "")
        if route_short_name and not pd.isna(route_short_name):
            route_names[route_id] = str(route_short_name)
        else:
            route_names[route_id] = route_id
    
    segments = []
    current_routes = None
    current_route_names = None
    segment_start = path[0]
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        
        if G.has_edge(u, v):
            edge_routes = G[u][v].get("route_ids", set())
            
            # get route names
            route_names_list = sorted([
                route_names.get(rid, str(rid)) 
                for rid in edge_routes
            ])
            
            # if the route changed, this is a transfer - finish current segment and start new
            if current_routes is not None and edge_routes != current_routes:
                # finish current segment: segment_start - line - u
                line_str = ", ".join(current_route_names)
                segments.append(f"{segment_start} - {line_str} - {u}")
                # start new segment from transfer station
                segment_start = u
                current_routes = edge_routes
                current_route_names = route_names_list
            elif current_routes is None:
                # first segment: start tracking
                current_routes = edge_routes
                current_route_names = route_names_list
        else:
            # if the edge is not present, finish current segment if any
            if current_routes is not None:
                line_str = ", ".join(current_route_names)
                segments.append(f"{segment_start} - {line_str} - {u}")
            segment_start = v
            current_routes = None
            current_route_names = None
    
    # finish last segment
    if current_routes is not None and current_route_names:
        line_str = ", ".join(current_route_names)
        segments.append(f"{segment_start} - {line_str} - {path[-1]}")
    elif len(segments) == 0:
        # if no segments were created, create a simple one
        segments.append(f"{path[0]} - {path[-1]}")
    
    return segments

def plot_paths_comparison(
    G: nx.Graph,
    routes: pd.DataFrame,
    dfs_path: list | None = None,
    bfs_path: list | None = None,
    start: str | None = None,
    end: str | None = None,
    use_geo_coords: bool = True,
    title: str = "DFS vs BFS Path Comparison",
):
    """
    Visualize graph with DFS and BFS paths highlighted.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # get positions
    if use_geo_coords:
        pos = {n: (G.nodes[n]["lon"], G.nodes[n]["lat"]) for n in G.nodes}
    else:
        pos = nx.spring_layout(G, seed=42, k=0.3)
    
    # create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    plt.title(title, fontsize=14, pad=20)
    
    # draw all edges of the graph (light-gray)
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], 
                color='lightgray', linewidth=0.5, alpha=0.3, zorder=1)
    
    # draw DFS path (blue)
    if dfs_path and len(dfs_path) > 1:
        for i in range(len(dfs_path) - 1):
            u, v = dfs_path[i], dfs_path[i + 1]
            if u in pos and v in pos:
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                ax.plot([x1, x2], [y1, y2], 
                        color='blue', linewidth=3, alpha=0.7, 
                        label='DFS Path' if i == 0 else '', zorder=2)
    
    # draw BFS path (red)
    if bfs_path and len(bfs_path) > 1:
        for i in range(len(bfs_path) - 1):
            u, v = bfs_path[i], bfs_path[i + 1]
            if u in pos and v in pos:
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                ax.plot([x1, x2], [y1, y2], 
                        color='red', linewidth=3, alpha=0.7,
                        linestyle='--', 
                        label='BFS Path' if i == 0 else '', zorder=3)
    
    # find transfer stations (where route changes)
    def find_transfer_stations(G, path, routes):
        """Find stations where route changes (transfers)."""
        if not path or len(path) < 2:
            return set()
        
        # create route names dictionary
        route_names = {}
        for _, row in routes.iterrows():
            route_id = row["route_id"]
            route_short_name = row.get("route_short_name", "")
            if route_short_name and not pd.isna(route_short_name):
                route_names[route_id] = str(route_short_name)
            else:
                route_names[route_id] = route_id
        
        transfer_stations = set()
        current_routes = None
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if G.has_edge(u, v):
                edge_routes = G[u][v].get("route_ids", set())
                # if route changed, u is a transfer station
                if current_routes is not None and edge_routes != current_routes:
                    transfer_stations.add(u)
                current_routes = edge_routes
        
        return transfer_stations
    
    # collect all path nodes
    all_path_nodes = set()
    transfer_stations = set()
    
    if dfs_path:
        all_path_nodes.update(dfs_path)
        transfer_stations.update(find_transfer_stations(G, dfs_path, routes))
    
    if bfs_path:
        all_path_nodes.update(bfs_path)
        transfer_stations.update(find_transfer_stations(G, bfs_path, routes))
    
    # regular nodes (not in path)
    regular_nodes = [n for n in G.nodes() if n not in all_path_nodes]
    if regular_nodes:
        reg_pos = {n: pos[n] for n in regular_nodes if n in pos}
        if reg_pos:
            ax.scatter(*zip(*reg_pos.values()), c='lightgray', s=15, 
                      alpha=0.3, zorder=4)
    
    # highlight only transfer stations
    transfer_pos = {n: pos[n] for n in transfer_stations if n in pos}
    if transfer_pos:
        ax.scatter(*zip(*transfer_pos.values()), c='orange', s=200, 
                  marker='o', edgecolors='darkorange', linewidths=2,
                  alpha=0.9, zorder=6, label='Transfer stations')
    
    # start node (always highlight)
    if start and start in pos:
        ax.scatter(*pos[start], c='green', s=300, marker='*', 
                  edgecolors='darkgreen', linewidths=2, 
                  zorder=7, label='Start')
    
    # end node (always highlight)
    if end and end in pos:
        ax.scatter(*pos[end], c='red', s=300, marker='*', 
                  edgecolors='darkred', linewidths=2, 
                  zorder=7, label='End')
    
    # label all path nodes (but don't highlight non-transfer stations)
    for node in all_path_nodes:
        if node in pos:
            x, y = pos[node]
            # Skip labeling if it's a transfer station (will be labeled separately)
            if node in transfer_stations:
                continue
            # Skip start/end if they are already highlighted
            if (node == start or node == end):
                # Still label start/end for clarity
                ax.annotate(node, (x, y), fontsize=6, 
                           ha='center', va='bottom',
                           color='black', alpha=0.8,
                           bbox=dict(boxstyle='round,pad=0.2', 
                                    facecolor='white', alpha=0.6),
                           zorder=8)
            else:
                # Regular path node - just text, no highlight
                ax.annotate(node, (x, y), fontsize=5, 
                           ha='center', va='center',
                           color='black', alpha=0.6,
                           zorder=8)
    
    # label transfer stations with better visibility
    for node in transfer_stations:
        if node in pos:
            x, y = pos[node]
            ax.annotate(node, (x, y), fontsize=6, 
                       ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='yellow', alpha=0.8),
                       zorder=9)
    
    # build route segments for legend
    handles, labels = ax.get_legend_handles_labels()
    
    # add route descriptions as text elements
    from matplotlib.patches import Rectangle
    
    # Add DFS route segments
    if dfs_path and len(dfs_path) > 1:
        dfs_segments = build_route_segments(G, dfs_path, routes)
        # add header
        text_handle = Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', visible=False)
        handles.append(text_handle)
        labels.append("Маршрут 1 (DFS):")
        # add segments
        for segment in dfs_segments:
            text_handle = Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', visible=False)
            handles.append(text_handle)
            labels.append(f"  {segment}")
    
    # Add BFS route segments
    if bfs_path and len(bfs_path) > 1:
        bfs_segments = build_route_segments(G, bfs_path, routes)
        # add header
        text_handle = Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', visible=False)
        handles.append(text_handle)
        labels.append("Маршрут 2 (BFS):")
        # add segments
        for segment in bfs_segments:
            text_handle = Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', visible=False)
            handles.append(text_handle)
            labels.append(f"  {segment}")
    
    plt.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.02, 1), 
              fontsize=7, framealpha=0.9)
    plt.axis("off")
    plt.tight_layout()
    plt.show()