import pandas as pd
import networkx as nx

def build_stop_clusters(stops: pd.DataFrame, used_stop_ids: set[str]) -> tuple[pd.DataFrame, dict]:
    """
    Merge GTFS stops with identical stop_name into single graph nodes.
    Node id == stop_name; coordinates are averaged.
    Only stops from used_stop_ids are included.
    """
    stops = stops[stops["stop_id"].isin(used_stop_ids)].copy()
    stops["stop_name_clean"] = stops["stop_name"].str.strip()

    clusters = (
        stops
        .groupby("stop_name_clean")
        .agg(
            lat=("stop_lat", "mean"),
            lon=("stop_lon", "mean"),
            stop_ids=("stop_id", list),
        )
        .reset_index()
        .rename(columns={"stop_name_clean": "node_id"})
    )

    # Mapping from original stop_id to merged node_id
    stop_id_to_node = {}
    for _, row in clusters.iterrows():
        for sid in row["stop_ids"]:
            stop_id_to_node[sid] = row["node_id"]

    return clusters, stop_id_to_node

def parse_gtfs_time(time_str: str) -> int:
    """
    Parse GTFS time format (HH:MM:SS) to seconds since midnight.
    """
    if pd.isna(time_str) or not time_str:
        return 0
    
    parts = str(time_str).split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    return 0

def build_hvv_graph(
    stops: pd.DataFrame,
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    routes: pd.DataFrame,
    allowed_route_types: set[int] | None = None,
) -> tuple[nx.Graph, pd.DataFrame, pd.DataFrame]:
    """
    Build undirected graph of the HVV network:

    - Filter routes by allowed_route_types.
    - Nodes: merged stops (clustered by stop_name, only for used stop_ids).
    - Edges: consecutive stops within each trip.
      Each edge stores a set of route_ids using this segment.
    """
    # Filter routes by type
    if allowed_route_types is not None:
        routes_sel = routes[routes["route_type"].isin(allowed_route_types)].copy()
    else:
        routes_sel = routes.copy()

    # Filter trips and stop_times
    trips_sel = trips[trips["route_id"].isin(routes_sel["route_id"])].copy()
    stop_times_sel = stop_times[stop_times["trip_id"].isin(trips_sel["trip_id"])].copy()

    # Determine which stops are actually used
    used_stop_ids = set(stop_times_sel["stop_id"].unique())

    # Build clusters only for used stops
    clusters, stop_id_to_node = build_stop_clusters(stops, used_stop_ids)

    # Join stop_times with trips and routes
    st = stop_times_sel.merge(
        trips_sel[["trip_id", "route_id"]],
        on="trip_id",
        how="left",
    ).merge(
        routes_sel[["route_id", "route_type"]],
        on="route_id",
        how="left",
    )

    # Build graph
    G = nx.Graph()

    # Add nodes with attributes
    for _, r in clusters.iterrows():
        G.add_node(
            r["node_id"],
            lat=r["lat"],
            lon=r["lon"],
            stop_ids=r["stop_ids"],
            transfer=len(r["stop_ids"]) > 1,
        )

    # Add edges per trip
    for trip_id, group in st.sort_values(["trip_id", "stop_sequence"]).groupby("trip_id"):
        group = group.sort_values("stop_sequence")
        nodes = []
        route_ids = []
        route_types = []
        times = []
        for _, row in group.iterrows():
            node = stop_id_to_node.get(row["stop_id"])
            if node:
                nodes.append(node)
                route_ids.append(row["route_id"])
                route_types.append(row["route_type"])
                # add time
                arrival_time = parse_gtfs_time(row.get("arrival_time", ""))
                departure_time = parse_gtfs_time(row.get("departure_time", ""))
                # save to list for use when creating edges
                times.append((arrival_time, departure_time))

        # Create edges between consecutive nodes
        for i in range(len(nodes) - 1):
            u, v = nodes[i], nodes[i + 1]
            if u != v:
                # calculate time between stops
                # time = arrival_time of the next stop - departure_time of the current stop
                if i + 1 < len(times):
                    travel_time = times[i + 1][0] - times[i][1]  # arrival_next - departure_current
                    if travel_time < 0:  # if it crosses midnight
                        travel_time += 24 * 3600
                else:
                    travel_time = 60  # default 1 minute
                
                if G.has_edge(u, v):
                    G[u][v]["route_ids"].add(route_ids[i])
                    G[u][v]["route_types"].add(route_types[i])
                    # update time (can take minimum or average)
                    if "travel_time" not in G[u][v]:
                        G[u][v]["travel_time"] = []
                    G[u][v]["travel_time"].append(travel_time)
                else:
                    G.add_edge(u, v, 
                            route_ids={route_ids[i]}, 
                            route_types={route_types[i]},
                            travel_time=[travel_time])

    return G, clusters, routes_sel
