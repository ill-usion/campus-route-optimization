import argparse
import osmnx as ox
import networkx as nx

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

matplotlib.use('TkAgg')
osm_filepath = "./map.osm"

paused = False

def get_node(G, ref: str):
    if ref is None:
        return None

    for node, attr in G.nodes(data=True):
        if attr.get("ref") == ref:
            return node


def get_all_nodes(G):
    return [attr.get("ref") for node, attr in G.nodes(data=True) if attr.get("ref") is not None]


def label_poi(ax, G, node, fallback_lbl="POI"):
    gnode = G.nodes(data=True)[node]
    x = gnode['x']
    y = gnode['y']
    label = gnode.get("ref", fallback_lbl)
    
    ax.text(x, y, label, color='white', fontsize=6, weight="bold")


def tree_traverse(G, start_node: int, finish_node: int, algorithm: str):
    frontier = [start_node]
    explored = set()
    path = {}
    searchpath = []

    next_func = (lambda: frontier.pop()) if algorithm == "dfs" else (lambda: frontier.pop(0))
    iterations = 0
    while len(frontier):
        iterations += 1
        current = next_func()
        searchpath.append(current)

        if current == finish_node:
            break

        explored.add(current)
        for neighbor in G.neighbors(current):
            if neighbor not in explored:
                frontier.append(neighbor)
                path[neighbor] = current


    fwd_path = {}
    cell = finish_node
    route = []
    while cell != start_node:
        route.insert(0, cell)
        fwd_path[path[cell]] = cell
        cell = path[cell]

    route.insert(0, start_node)
    return searchpath, fwd_path, route, iterations


def main():
    parser = argparse.ArgumentParser(description="A proof of concept program for campus path optimization")
    parser.add_argument("-s", "--start", help="Start node ref", type=str)
    parser.add_argument("-f", "--finish", help="Finish node ref", type=str)
    parser.add_argument("-alg", "--algorithm", help="Tree traversal algorithm (dfs, bfs)", type=str, default="dfs")
    parser.add_argument("--speed", help="Animation delay", type=int, default=400)
    parser.add_argument("--no-anim", help="Plot route without animating", action="store_true")
    parser.add_argument("-l", "--list", help="Lists all points of interest", action="store_true")

    args = parser.parse_args()
    G = ox.graph_from_xml(osm_filepath, simplify=True, retain_all=False)

    if args.list:
        nodes = get_all_nodes(G)
        print("\n".join(sorted(nodes)))
        return

    start_node = get_node(G, args.start)
    finish_node = get_node(G, args.finish)

    if (start_node is None) or (finish_node is None):
        print("Start and Finish nodes must be valid")
        exit(1)

    print("Start:", start_node, "Finish:", finish_node, "Algorithm:", args.algorithm)
    _, _, route, iterations = tree_traverse(G, start_node, finish_node, args.algorithm)

    fig, ax = ox.plot_graph(G, node_size=0, show=False, close=False)

    ax.set_title(f"Algorithm: {args.algorithm}, Steps: {iterations}")
    label_poi(ax, G, start_node)
    label_poi(ax, G, finish_node)

    ax.set_position([0, 0, 1, 0.9])
    ax.set_xmargin(0)
    ax.set_ymargin(10)

    if args.no_anim:
        ox.plot_graph_route(G, route, ax=ax, node_size=0, route_linewidth=2, route_color="yellow", show=False, close=False)
    else:
        def update(frame):
            sub_route = route[:frame+1]

            ox.plot_graph_route(G, sub_route, ax=ax, node_size=0, route_linewidth=2, route_color="yellow", show=False, close=False)
            if frame == len(route) - 1:
                fig.suptitle("Finished")
                fig.canvas.draw_idle()

        anim = FuncAnimation(
            fig,
            update,
            frames=len(route),
            interval=args.speed,
            repeat=False,
            cache_frame_data=False)

        def on_key_press(event):
            global paused
            if event.key == ' ':
                paused = not paused
                if paused:
                    anim.pause()
                    fig.suptitle("Paused")
                else:
                    anim.resume()
                    fig.suptitle("Running")

                fig.canvas.draw_idle()
                

        fig.canvas.mpl_connect("key_press_event", on_key_press)

    plt.show()

if __name__ == "__main__":
    main()
