from shapely.geometry import LineString, Point
import geopandas as gpd
import matplotlib.pyplot as plt
import math
import networkx as nx
import random
import time

def get_random_color():
    return (random.random(), random.random(), random.random())

def angle_between_lines(line1: LineString, line2: LineString):
    def get_vector(line):
        x0, y0 = line.coords[0]
        x1, y1 = line.coords[-1]

        return (x1 - x0, y1 - y0)

    def angle(v1, v2):
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        
        if mag1 == 0 or mag2 == 0:
            return 180  # Treat as totally dissimilar
        
        # Compute both angle and its reverse version
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        cos_theta = max(-1, min(1, dot / (mag1 * mag2)))
        theta = math.degrees(math.acos(cos_theta))

        return min(theta, 180 - theta)

    v1 = get_vector(line1)
    v2 = get_vector(line2)

    return angle(v1, v2)

def are_connected(line1: LineString, line2: LineString, angle_threshold=30, distance_threshold=1e-6):
    if not line1.intersects(line2):
        return False
    
    intersection = line1.intersection(line2)
    
    if not intersection.is_empty and intersection.geom_type == "Point":
        angle = angle_between_lines(line1, line2)

        return angle < angle_threshold

def build_street_graph(gdf, angle_threshold=30, distance_threshold=1e-6):
    G = nx.Graph()
    print(f"Number of lines: {len(gdf)}")
    print(f"Angle threshold: {angle_threshold}")  
    print(f"Distance threshold: {distance_threshold}")
    print("Adding nodes and edges...")
    
    for idx, row in gdf.iterrows():
        time.sleep(1)
        print(f"Adding node {idx} with geometry {row.geometry}")
        G.add_node(idx, geometry=row.geometry)

    for i in range(len(gdf)):
        print(f"Processing line {i}...")
        for j in range(i+1, len(gdf)):
            time.sleep(1)
            print(f"Checking line {i} against line {j}...")
            line1 = gdf.iloc[i].geometry
            print(f"Line 1: {line1}")
            line2 = gdf.iloc[j].geometry
            print(f"Line 2: {line2}")
            
            if are_connected(line1, line2, angle_threshold, distance_threshold):
                print(f"Lines {i} and {j} are connected.")
                G.add_edge(i, j)
    
    return G

def assign_colors_by_street_group(gdf, G):
    print("Assigning colors to street groups...")
    color_map = {}
    for group_id, component in enumerate(nx.connected_components(G)):
        print(f"Processing component {group_id} with nodes {component}")
        color = get_random_color()
        for idx in component:
            print(f"Assigning color {color} to node {idx}")
            color_map[idx] = color
    
    gdf["color"] = gdf.index.map(color_map)

    print("Color assignment complete.")
    print(f"Color map: {color_map}")
    return gdf

def plot_colored_streets(gdf, output_path):
    print("Plotting colored streets...")
    print(f"Output path: {output_path}")
    fig, ax = plt.subplots(figsize=(30, 30), dpi=100)
    
    for _, row in gdf.iterrows():
        time.sleep(1)
        print(f"Plotting line with color {row['color']}")
        print(f"Geometry: {row.geometry}")
        if row.geometry.geom_type == "LineString":
            print(f"Line coordinates: {row.geometry.xy}")
            ax.plot(
                row.geometry.xy[0],
                row.geometry.xy[1],
                color=row["color"],
                linewidth=1.2
            )
    
    ax.set_title("Street Grouping Algorithm Result", fontsize=20)
    plt.axis("equal")
    plt.axis("off")
    plt.savefig(output_path, dpi=100, bbox_inches=None, pad_inches=0)
    print(f"Saved plot to {output_path}")

if __name__ == "__main__":
    gdf = gpd.read_file("sample/roads.shp")
    print(f"Number of lines: {len(gdf)}")
    G = build_street_graph(gdf)
    print("Street graph built.")
    print(f"Number of edges in graph: {G.number_of_edges()}")
    gdf = assign_colors_by_street_group(gdf, G)
    print("Colors assigned to street groups.")
    print(f"Number of unique colors: {len(gdf['color'].unique())}")
    plot_colored_streets(gdf, "output/solution-test1.png")
    print("Plotting completed.")
    print("Street grouping algorithm completed and saved to output/solution-test1.png")
