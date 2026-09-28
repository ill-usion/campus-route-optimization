import argparse
import osmnx as ox
import networkx as nx

import matplotlib
matplotlib.use('TkAgg')
osm_filepath = "./map.osm"

class RouteOptimizer:
    def __init__(self, graph):
        self.G = graph

    def get_node(self, ref: str):
        for node, attr in self.G.nodes(data=True):
            if attr.get("ref") == ref:
                return node

    def get_all_nodes(self):
        return [attr.get("ref") for node, attr in self.G.nodes(data=True) if attr.get("ref") is not None]

    def find_shortest_route(self, start, end):
        try:
            route = nx.astar_path(self.G, source=start, target=end, weight="length")
            dist = nx.astar_path_length(self.G, source=start, target=end, weight="length")
            return route, dist
        except nx.NetworkXNoPath:
            print("No path found")
            return None
        except Exception as e:
            print("Error:", e)
            return None

    def plot_route(self, route):
        # ox.plot_graph(G)
        fig, ax = ox.plot_graph_route(self.G, route, route_color="red", route_linewidth=4, node_size=0)


def main():
    parser = argparse.ArgumentParser(description="A proof of concept program for campus path optimization")
    parser.add_argument("-s", "--start", help="Start node ref", type=str, required=True)
    parser.add_argument("-f", "--finish", help="Finish node ref", type=str, required=True)
    parser.add_argument("-l", "--list", help="List all nodes", action="store_true") 

    args = parser.parse_args()

    G = ox.graph_from_xml(osm_filepath, simplify=True, retain_all=False)
    op = RouteOptimizer(G)

    if args.list:
        nodes = op.get_all_nodes()
        print("\n".join(sorted(nodes)))
        exit(0)

    start_node = op.get_node(args.start)
    finish_node = op.get_node(args.finish)

    if start_node is None:
        print("Start node is none")
        exit(1)

    if finish_node is None:
        print("Finish node is none")
        exit(1)

    ret = op.find_shortest_route(start_node, finish_node)
    if ret is not None:
        route, dist = ret
        print("Distance:", dist)
        op.plot_route(route)


if __name__ == "__main__":
    main()
