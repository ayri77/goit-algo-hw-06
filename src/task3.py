'''
Реалізуйте алгоритм Дейкстри для знаходження найкоротшого шляху 
в розробленому графі: додайте у граф ваги до ребер та знайдіть 
найкоротший шлях між всіма вершинами графа.
'''

from pathlib import Path

from graph_utils.data_loader import load_gtfs_tables, HVV_DATA
from graph_utils.graph_builder import build_hvv_graph

from graph_utils.dijkstra import add_edge_weights, dijkstra_shortest_path, all_pairs_shortest_paths
from graph_utils.dijkstra import geographic_distance, travel_time_weight

def format_time(seconds: float) -> str:
    """Format seconds to human-readable time."""
    if seconds < 60:
        return f"{seconds:.1f} sec"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} min"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{int(hours)} h {int(minutes)} min"

def format_distance(km: float) -> str:
    """Format distance to human-readable format."""
    if km < 1:
        return f"{km * 1000:.0f} m"
    else:
        return f"{km:.2f} km"

def main():
    print("=" * 70)
    print("Dijkstra's algorithm for finding the shortest path")
    print("=" * 70)
    
    # U-Bahn (route_type = 402) + S-Bahn (route_type = 109)
    allowed_types = {402, 109}

    gtfs_dir = Path(HVV_DATA)
    print("\n📊 Loading GTFS data...")
    tables = load_gtfs_tables(gtfs_dir)
    
    print("🔨 Building graph...")
    G, _, _ = build_hvv_graph(
        stops=tables["stops"],
        stop_times=tables["stop_times"],
        trips=tables["trips"],
        routes=tables["routes"],
        allowed_route_types=allowed_types,
    )
    print(f"✓ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Selection of weight calculation method
    print("\n" + "=" * 70)
    print("Selection of weight calculation method:")
    print("  1. Geographic distance (Haversine)")
    print("  2. Travel time (from GTFS schedule)")
    print("=" * 70)
    
    weight_type = "geographic"  # or "time"
    weight_func = geographic_distance
    
    if weight_type == "geographic":
        print("\n📍 Geographic distance (Haversine formula) is used")
        G_weighted = add_edge_weights(G, weight_func=geographic_distance, weight_type="geographic")
        unit = "km"
        format_value = format_distance
    else:
        print("\n⏱️  Travel time (from GTFS schedule) is used")
        G_weighted = add_edge_weights(G, weight_func=None, weight_type="time")
        unit = "seconds"
        format_value = lambda x: format_time(x)
    
    # Find shortest path
    print("\n" + "=" * 70)
    print("Finding shortest path")
    print("=" * 70)
    
    start = "Stade"
    end = "Ohlsdorf"
    
    if start not in G_weighted or end not in G_weighted:
        print(f"❌ Node '{start}' or '{end}' not found in graph!")
        print(f"Available nodes: {list(G_weighted.nodes())[:10]}...")
        exit(1)
    
    print(f"\n🔍 Finding path from '{start}' to '{end}'...")
    path, distance = dijkstra_shortest_path(G_weighted, start, end)
    
    if path:
        print(f"\n✓ Path found!")
        print(f"\n📏 Path length: {format_value(distance)}")
        print(f"\n🗺️  Route ({len(path)} stations):")
        print("-" * 70)
        for i, station in enumerate(path, 1):
            marker = "🚉" if i == 1 else ("🏁" if i == len(path) else "  ")
            print(f"  {i:2d}. {marker} {station}")
        print("-" * 70)
        
        # Detail of segments
        print(f"\n📋 Detail of route:")
        total_segments = len(path) - 1
        for i in range(total_segments):
            u, v = path[i], path[i + 1]
            if G_weighted.has_edge(u, v):
                segment_weight = G_weighted[u][v].get('weight', 0)
                print(f"  {i+1}. {u} → {v}: {format_value(segment_weight)}")
    else:
        print(f"\n❌ Path not found!")
    
    # Statistics for all pairs (optional, may be slow)
    print("\n" + "=" * 70)
    print("Statistics of shortest paths")
    print("=" * 70)
    
    print("\n📊 Calculating all pairs of paths...")
    all_paths = all_pairs_shortest_paths(G_weighted)
    print(f"\n✓ Found {len(all_paths)} unique pairs of paths")
     
    # Statistics
    if all_paths:
        distances = []
        for (start, end), (path, distance) in all_paths.items():
            if path and distance != float('inf'):
                distances.append(distance)
        
        if distances:
            print(f"\n📊 Statistics of distances:")
            print(f"  Minimum: {format_value(min(distances))}")
            print(f"  Maximum: {format_value(max(distances))}")
            print(f"  Average: {format_value(sum(distances) / len(distances))}")
            print(f"  Total pairs: {len(distances)}")
        else:
            print("\n⚠️  No valid paths found in statistics")
    else:
        print("\n⚠️  No paths calculated")
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()