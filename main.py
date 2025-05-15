from shapely.geometry import LineString, Point
import geopandas as gpd
import matplotlib.pyplot as plt
import math
import networkx as nx
import random

def get_random_color():
    return (random.random(), random.random(), random.random())

def angle_between_lines(line1: LineString, line2: LineString):
    def get_vector(line):
        x0, y0 = line.coords[0]
        x1, y1 = line.coords[-1]
        return (x1 - x0, y1 - y0)

    def angle(v1, v2):
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 == 0 or mag2 == 0:
            return 180  # Treat as totally dissimilar
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(-1, min(1, cos_theta))  # clamp for safety
        return math.degrees(math.acos(cos_theta))

    v1 = get_vector(line1)
    v2 = get_vector(line2)
    return angle(v1, v2)

def are_connected(line1: LineString, line2: LineString, angle_threshold=30, distance_threshold=1e-6):
    # Check if lines touch at an endpoint
    endpoints1 = [Point(line1.coords[0]), Point(line1.coords[-1])]
    endpoints2 = [Point(line2.coords[0]), Point(line2.coords[-1])]

    touching = any(p1.distance(p2) < distance_threshold for p1 in endpoints1 for p2 in endpoints2)

    if not touching:
        return False

    # Check angle
    angle = angle_between_lines(line1, line2)
    return angle < angle_threshold

def build_street_graph(gdf, angle_threshold=30, distance_threshold=1e-6):
    G = nx.Graph()
    
    for idx, row in gdf.iterrows():
        G.add_node(idx, geometry=row.geometry)

    for i in range(len(gdf)):
        for j in range(i+1, len(gdf)):
            line1 = gdf.iloc[i].geometry
            line2 = gdf.iloc[j].geometry
            
            if are_connected(line1, line2, angle_threshold, distance_threshold):
                G.add_edge(i, j)
    
    return G

def assign_colors_by_street_group(gdf, G):
    color_map = {}
    for group_id, component in enumerate(nx.connected_components(G)):
        color = get_random_color()
        for idx in component:
            color_map[idx] = color
    
    gdf["color"] = gdf.index.map(color_map)
    return gdf

def plot_colored_streets(gdf, output_path):
    fig, ax = plt.subplots(figsize=(30, 30), dpi=100)
    for _, row in gdf.iterrows():
        if row.geometry.geom_type == "LineString":
            ax.plot(
                row.geometry.xy[0],
                row.geometry.xy[1],
                color=row["color"],
                linewidth=1.2
            )
    ax.set_title("Street Grouping Algorithm Result", fontsize=20)
    plt.grid(True)
    plt.axis("equal")
    plt.savefig(output_path, dpi=100, bbox_inches="tight")

if __name__ == "__main__":
    gdf = gpd.read_file("sample/roads.shp")
    G = build_street_graph(gdf)
    gdf = assign_colors_by_street_group(gdf, G)
    plot_colored_streets(gdf, "output/solution.png")
    print("Street grouping algorithm completed and saved to output/solution.png")
