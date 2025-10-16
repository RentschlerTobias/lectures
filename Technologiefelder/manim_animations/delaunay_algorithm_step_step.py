import numpy as np
from manim import *


class DelaunayAlgorithmStepByStep(Scene):
    def construct(self):
        # Add the axis
        self.add_axis()

        # Step 1: Define initial points
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)
        ]

        # Map points to scene coordinates
        scene_points = [self.ax.coords_to_point(x, y) for x, y in points]
        dots = VGroup(*[Dot(p, color=RED) for p in scene_points])

        # Step 2: Add points one by one
        for dot in dots:
            self.add(dot)
            self.wait(0.5)

        # Step 3: Connect initial points to form the first triangle
        self.show_initial_triangle(scene_points)

        # Step 4: Add new point and illustrate circumcircle check
        new_point = (0.6, 0.4)
        mapped_new_point = self.ax.coords_to_point(*new_point)
        self.add(Dot(mapped_new_point, color=BLUE))
        self.wait(1)

        # Step 5: Highlight invalid triangles
        self.highlight_invalid_triangle(
            scene_points[0], scene_points[1], mapped_new_point)

        # Step 6: Remove invalid triangles and re-triangulate
        self.retriangulate(scene_points, mapped_new_point)

    def add_axis(self):
        # Add axis to the scene
        self.ax = Axes(
            x_range=(-0.1, 1.1),
            y_range=(-0.1, 1.1),
            axis_config={"include_numbers": True}
        )
        self.add(self.ax)
        self.wait(1)

    def show_initial_triangle(self, points):

        # Draw the first triangle
        triangle = Polygon(points[0], points[1],
                           points[2], color=YELLOW, fill_opacity=0.3)
        self.add(triangle)
        self.wait(1)

        # Highlight edges
        edges = [
            Line(points[0], points[1], color=GREEN),
            Line(points[1], points[2], color=GREEN),
            Line(points[2], points[0], color=GREEN)
        ]
        self.add(*edges)
        self.wait(1)

    def highlight_invalid_triangle(self, p1, p2, p_new):
        # Draw circumcircle of the first triangle
        circumcircle = Circle(color=BLUE)
        circumcircle.set_width(1)  # Adjust size based on triangle
        # Center it around the new point for illustration
        circumcircle.move_to(p_new)
        self.add(circumcircle)
        self.wait(1)

        # Highlight invalid triangle
        invalid_triangle = Polygon(p1, p2, p_new, color=RED, fill_opacity=0.4)
        self.add(invalid_triangle)
        self.wait(1)

    def retriangulate(self, points, new_point):
        # Remove invalid triangle
        self.clear()

        # Add new edges to form valid triangulation
        new_triangles = [
            Polygon(points[0], points[1], new_point,
                    color=YELLOW, fill_opacity=0.3),
            Polygon(points[1], points[2], new_point,
                    color=YELLOW, fill_opacity=0.3),
            Polygon(points[2], points[0], new_point,
                    color=YELLOW, fill_opacity=0.3)
        ]
        self.add(*new_triangles)
        self.wait(1)
