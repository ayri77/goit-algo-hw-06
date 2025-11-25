import networkx as nx
import heapq

def geographic_distance(G: nx.Graph, u: str, v: str) -> float:
    """
    Calculate the geographic distance between two nodes using Haversine formula.
    Returns distance in kilometers.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    u_lat = G.nodes[u]['lat']
    u_lon = G.nodes[u]['lon']
    v_lat = G.nodes[v]['lat']
    v_lon = G.nodes[v]['lon']
    
    # Haversine formula for great-circle distance
    R = 6371  # Earth radius in km
    lat1, lon1 = radians(u_lat), radians(u_lon)
    lat2, lon2 = radians(v_lat), radians(v_lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def travel_time_weight(G: nx.Graph, u: str, v: str) -> float:
    """
    Get travel time between two nodes from edge attributes.
    """
    if G.has_edge(u, v):
        travel_times = G[u][v].get("travel_time", [])
        if travel_times:
            return min(travel_times)  # minimum time
    return 60  # default 1 minute

def add_edge_weights(G: nx.Graph, weight_func, weight_type: str = "geographic") -> nx.Graph:
    """
    Add weights to the edges of the graph.
    
    Args:
        G: Graph
        weight_func: Function to calculate weight (geographic_distance or travel_time_weight)
        weight_type: "geographic" or "time"
    """
    for u, v in G.edges():
        if weight_type == "geographic":
            G[u][v]['weight'] = weight_func(G, u, v)
        elif weight_type == "time":
            # use saved time from edges
            travel_times = G[u][v].get("travel_time", [])
            if travel_times:
                # can take minimum, average or first value
                G[u][v]['weight'] = min(travel_times)  # or sum(travel_times) / len(travel_times)
            else:
                G[u][v]['weight'] = 60  # default 1 minute
    return G

def dijkstra_shortest_path(G, start, end) -> tuple[list, float]:
    """
    Find the shortest path between two nodes using Dijkstra's algorithm.
    """
    # initialize distances and predecessors
    distances = {node: float('inf') for node in G.nodes()}
    predecessors = {node: None for node in G.nodes()}
    distances[start] = 0
    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == end:
            # reconstruct path
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = predecessors[current_node]
            path.reverse()
            return path, distances[end]
        for neighbor, attrs in G[current_node].items():
            weight = attrs.get('weight', 1)
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (new_distance, neighbor))
    
    # no path found
    return None, float('inf')

def all_pairs_shortest_paths(G) -> dict:
    """
    Find all shortest paths between all pairs of nodes using Dijkstra's algorithm.
    Returns a dictionary: {(start, end): (path, distance)}
    """
    all_paths = {}
    nodes = list(G.nodes())
    total_pairs = len(nodes) * (len(nodes) - 1) // 2
    processed = 0
    
    for i, start in enumerate(nodes):
        for end in nodes[i+1:]:  # Only compute for unique pairs (start != end)
            path, distance = dijkstra_shortest_path(G, start, end)
            if path:  # Only add if path exists
                all_paths[(start, end)] = (path, distance)
            processed += 1
            if processed % 100 == 0:
                print(f"  Processed {processed}/{total_pairs} pairs...", end='\r')
    
    return all_paths