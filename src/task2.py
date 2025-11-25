'''
Напишіть програму, яка використовує алгоритми DFS і BFS для знаходження шляхів 
у графі, який було розроблено у першому завданні.

Далі порівняйте результати виконання обох алгоритмів для цього графа, висвітлить 
різницю в отриманих шляхах. Поясніть, чому шляхи для алгоритмів саме такі.
'''

from graph_utils.data_loader import load_gtfs_tables, HVV_DATA
from graph_utils.graph_builder import build_hvv_graph
from graph_utils.pathfinding import dfs_path, bfs_path, compare_paths
from graph_utils.visualization import plot_paths_comparison

from pathlib import Path

def main():
    
    gtfs_dir = Path(HVV_DATA)
    tables = load_gtfs_tables(gtfs_dir)

    # U-Bahn (route_type = 402) + S-Bahn (route_type = 109)
    allowed_types = {402, 109}

    G, _, _ = build_hvv_graph(
        stops=tables["stops"],
        stop_times=tables["stop_times"],
        trips=tables["trips"],
        routes=tables["routes"],
        allowed_route_types=allowed_types,
    )

    nodes = list(G.nodes())
    print(f"Total nodes in graph: {len(nodes)}")
    print(f"Example nodes: {nodes[:10]}")    
    
    # start and end stops
    start = "Stade"
    #start = "Landwehr"
    end = "Ohlsdorf"
    #end = "Dammtor (Messe/CCH)"

    if start not in G:
        print(f"Node '{start}' not found in graph!")
        exit(1)
    if end not in G:
        print(f"Node '{end}' not found in graph!")
        exit(1)
    
    # find paths
    dfs_result = dfs_path(G, start, end)
    bfs_result = bfs_path(G, start, end)
    
    # print results
    print(f"\nDFS путь: {dfs_result}")
    print(f"DFS path length: {len(dfs_result) if dfs_result else 'Path not found'}")
    
    print(f"\nBFS path: {bfs_result}")
    print(f"BFS path length: {len(bfs_result) if bfs_result else 'Path not found'}")
    
    # compare paths
    comparison = compare_paths(dfs_result, bfs_result, G)
    print("\n" + "=" * 60)
    print("Comparison of paths:")
    print(f"  DFS length: {comparison['path1_length']}")
    print(f"  BFS length: {comparison['path2_length']}")
    print(f"  Difference: {comparison['length_difference']}")
    print(f"  Same paths: {comparison['same_path']}")
    
    # explain differences
    print("\n" + "=" * 60)
    print("Explanation of differences:")
    print("\nDFS (Depth-First Search):")
    print("  - Uses stack (LIFO - Last In First Out)")
    print("  - Goes deep into the graph, exploring one path to the end")
    print("  - Does not guarantee the shortest path")
    print("  - May find a longer path if the first branch does not lead to the goal")
    
    print("\nBFS (Breadth-First Search):")
    print("  - Uses queue (FIFO - First In First Out)")
    print("  - Goes wide, exploring all neighbors at each level")
    print("  - Guarantees the shortest path by number of edges (for an unweighted graph)")
    print("  - Always finds a path with the minimum number of transitions")
    
    if comparison['path1_length'] and comparison['path2_length']:
        if comparison['path1_length'] > comparison['path2_length']:
            print(f"\nIn this case, DFS found a longer path by {comparison['length_difference']} stations, "
                  f"because it went down the first available branch, which turned out to be not the shortest.")
        elif comparison['path1_length'] < comparison['path2_length']:
            print(f"\nIn this case, DFS accidentally found a shorter path, "
                  f"but this is not guaranteed by the algorithm.")
        else:
            print(f"\nIn this case, both algorithms found paths of the same length.")

    print("\n" + "=" * 60)
    print("Visualization of paths...")
    
    plot_paths_comparison(
        G,
        routes=tables["routes"],
        dfs_path=dfs_result,
        bfs_path=bfs_result,
        start=start,
        end=end,
        use_geo_coords=True,
        title=f"DFS vs BFS: {start} → {end}",
    )

if __name__ == "__main__":
    main()