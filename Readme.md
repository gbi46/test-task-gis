## Quick Start

You can run the project using a Python virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How the Algorithm Works
This algorithm groups line segments into what humans would perceive as a single street — based solely on geometry, without any street names or external metadata. Here's how it works:

1️⃣ Treat Lines as Graph Nodes
Each line segment from the shapefile is treated as a node in a graph.

Initially, all lines are considered separate, unconnected entities.

2️⃣ Detect Connections Based on Geometry
Two line segments are considered part of the same street if all of the following are true:

They intersect at a single point (not just endpoints).

The angle between their local directions near the intersection is below a configurable threshold (default: 30°).

The algorithm is direction-agnostic — reversed lines are still considered connected.

This allows:

Curved streets to remain connected.

Streets to continue seamlessly through intersections.

Lines in either direction to be grouped together.

3️⃣ Local Angle Calculation at Intersection
Instead of comparing the global direction from start to end, the algorithm:

Finds the intersection point between two lines.

Computes vectors adjacent to that point (i.e., local segment direction).

Calculates the smallest angle between those two vectors using acos (with clamp for precision).

This approach is more robust for curved and segmented lines.

4️⃣ Build a Graph of Street Relationships
Using networkx, a graph is constructed with nodes (line segments) and edges (logical connections).

All connected components in the graph are identified.

Each component is interpreted as a single street group.

5️⃣ Assign Colors and Visualize
Each group of connected lines receives a unique, randomly generated color.

The grouped lines are plotted using matplotlib into a 3000×3000 pixel image.

The output includes a grid and axis ticks for spatial clarity.