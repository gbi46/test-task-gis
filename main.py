from shapely.geometry import LineString, Point
import geopandas as gpd
import matplotlib.pyplot as plt
import math
import networkx as nx
import random

def get_random_color():
    return (random.random(), random.random(), random.random())

def angle_between_intersections(line1: LineString, line2: LineString, intersection: Point):
    def direction_at_point(line, point):
        coords = list(line.coords)
        nearest_idx = min(range(len(coords)), key=lambda i: Point(coords[i]).distance(point))
        
        # Use a vector from the nearest point to the next one (forward or backward)
        if nearest_idx < len(coords) - 1:
            x0, y0 = coords[nearest_idx]
            x1, y1 = coords[nearest_idx + 1]
        else:
            x0, y0 = coords[nearest_idx - 1]
            x1, y1 = coords[nearest_idx]

        return (x1 - x0, y1 - y0)
    
    v1 = direction_at_point(line1, intersection)
    v2 = direction_at_point(line2, intersection)

    
    mag1 = math.hypot(*v1)
    mag2 = math.hypot(*v2)
    
    if mag1 == 0 or mag2 == 0:
        return 180
    
    # Compute both angle and its reverse version
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    cos_theta = max(-1, min(1, dot / (mag1 * mag2)))
    theta = math.degrees(math.acos(cos_theta))

    return min(theta, 180 - theta)

def are_connected(line1: LineString, line2: LineString, angle_threshold=30, distance_threshold=1e-6):
    if not line1.intersects(line2):
        return False
    
    intersection = line1.intersection(line2)
    
    if not intersection.is_empty and intersection.geom_type == "Point":
        angle = angle_between_intersections(line1, line2, intersection)

        return angle < angle_threshold
    
    return False

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
    plt.axis("equal")
    plt.grid(True)
    plt.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    plt.savefig(output_path, dpi=100, bbox_inches=None, pad_inches=0)

if __name__ == "__main__":
    gdf = gpd.read_file("sample/roads.shp")
    G = build_street_graph(gdf)
    gdf = assign_colors_by_street_group(gdf, G)
    plot_colored_streets(gdf, "output/solution.png")
    print("Street grouping algorithm completed and saved to output/solution.png")
