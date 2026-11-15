from manim import *

class TravelingSalesmanProblem(Scene):
    def construct(self):
        # 1. Define city coordinates (vertices)
        vertices = {
            "A": np.array([-3, 1, 0]),
            "B": np.array([0, 2.5, 0]),
            "C": np.array([3, 1, 0]),
            "D": np.array([2, -2, 0]),
            "E": np.array([-2, -2, 0]),
        }

        # 2. Define edges
        edges = [
            ("A", "B"), ("B", "C"), ("C", "D"), 
            ("D", "E"), ("E", "A"), ("A", "C"), 
            ("B", "D")
        ]

        # 3. Create the Graph mobject
        g = Graph(
            list(vertices.keys()),
            edges,
            layout=vertices,
            vertex_config={"radius": 0.3, "color": BLUE, "fill_color": DARK_BLUE},
            edge_config={"stroke_width": 2, "color": GRAY},
        )

        # Use Text() instead of Tex() so LaTeX is not needed
        title = Text("Traveling Salesman Problem (TSP)", font_size=36).to_edge(UP)

        self.play(Write(title), Create(g))
        self.wait(1)

        # 4. Highlight an optimal tour: A -> B -> C -> D -> E -> A
        tour_edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")]

        tour_animations = []
        for u, v in tour_edges:
            # Handle undirected edge lookup safely
            edge_key = (u, v) if (u, v) in g.edges else (v, u)
            edge_mobject = g.edges[edge_key]
            tour_animations.append(edge_mobject.animate.set_color(YELLOW).set_stroke(width=6))

        self.play(*tour_animations, run_time=3)
        self.wait(2)

