import networkx as nx

def basic_graph_stats(G: nx.Graph) -> dict:
    """
    Calculate basic statistics for the graph.
    """
    degrees = dict(G.degree())
    degree_values = list(degrees.values()) if degrees else [0]

    return {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "max_degree": max(degree_values),
        "min_degree": min(degree_values),
        "avg_degree": sum(degree_values) / len(degree_values) if degree_values else 0,
        "degrees": degrees,
    }
