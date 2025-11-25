'''
Створіть граф за допомогою бібліотеки networkX для моделювання певної реальної мережі 
(наприклад, транспортної мережі міста, соціальної мережі, інтернет-топології).

info
📖 Реальну мережу можна вибрати на свій розсуд, якщо немає можливості придумати свою мережу, наближену до реальності.

Візуалізуйте створений граф, проведіть аналіз основних характеристик 
(наприклад, кількість вершин та ребер, ступінь вершин).
'''

'''
Для вирішення завдання я використав набори даних:
HVV – Транспортна мережа Гамбурга
'''
# HVV-specific route_type values (from routes.txt):
#
# 3    – Bus routes (majority of entries).
# 402  – U-Bahn metro lines (e.g. U1, U2, U3, U4).
# 2    – Other rail services (e.g. regional / train-like services; HVV-specific use).
# 702  – Special rail / regional service type (HVV-specific).
# 109  – Special rail / regional service type (HVV-specific).
# 1200 – Additional special / regional service type (HVV-specific).
#
# Note:
# - HVV uses its own extended route_type codes that do not fully follow the
#   standard GTFS specification.
# - For precise semantics of 2, 702, 109, 1200, refer to HVV / GTFS documentation.

from pathlib import Path
from graph_utils.data_loader import load_gtfs_tables, HVV_DATA
from graph_utils.graph_builder import build_hvv_graph
from graph_utils.graph_analysis import basic_graph_stats
from graph_utils.visualization import plot_hvv_graph

def main():
    gtfs_dir = Path(HVV_DATA)
    tables = load_gtfs_tables(gtfs_dir)

    # U-Bahn (route_type = 402) + S-Bahn (route_type = 109)
    allowed_types = {402, 109}

    G, clusters, routes_sel = build_hvv_graph(
        stops=tables["stops"],
        stop_times=tables["stop_times"],
        trips=tables["trips"],
        routes=tables["routes"],
        allowed_route_types=allowed_types,
    )

    stats = basic_graph_stats(G)
    print("Nodes:", stats["num_nodes"])
    print("Edges:", stats["num_edges"])
    print("Avg degree:", stats["avg_degree"])

    plot_hvv_graph(
        G,
        routes=routes_sel,
        route_ids=None,
        use_geo_coords=True,
        title="Hamburg U-Bahn & S-Bahn (merged transfers)",
    )


if __name__ == "__main__":
    main()