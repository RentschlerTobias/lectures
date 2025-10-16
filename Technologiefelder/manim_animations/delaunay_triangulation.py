
import numpy as np
from manim import *
from scipy.spatial import Delaunay


class DelaunayTriangulation(Scene):
    def construct(self):
        # Add the axis
        self.add_axis()

        # Step 1: Define the initial boundary nodes
        boundary_nodes = np.array([
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 0)
        ])
        points = list(boundary_nodes)

        # Visualize the initial nodes
        mapped_nodes = [self.ax.coords_to_point(
            x, y) for x, y in boundary_nodes]
        boundary_dots = VGroup(*[Dot(point, color=BLUE)
                               for point in mapped_nodes])
        boundary_square = Polygon(*mapped_nodes, color=BLUE)

        self.add(boundary_square, boundary_dots)
        self.wait(1)

        # Specify the number of random nodes to add
        num_random_nodes = 5

        # Add nodes and visualize the triangulation process
        for _ in range(num_random_nodes):
            # Add a random point inside the domain
            new_point = np.random.rand(2)
            points.append(new_point)
            self.add_point_to_scene(new_point)

            # Perform Delaunay triangulation
            delaunay = Delaunay(points)
            self.visualize_triangulation(points, delaunay)

    def add_axis(self):
        # Add axis to the scene
        self.ax = Axes(
            x_range=(-0.1, 1.1),
            y_range=(-0.1, 1.1),
            axis_config={"include_numbers": True}
        )
        self.add(self.ax)
        self.wait(1)

    def add_point_to_scene(self, point):
        # Map and add a point to the scene
        mapped_point = self.ax.coords_to_point(*point)
        dot = Dot(mapped_point, color=RED)
        self.add(dot)
        self.wait(0.5)

    def visualize_triangulation(self, points, delaunay):
        # Clear previous triangles
        self.remove(*[m for m in self.mobjects if isinstance(m, Polygon)])

        # Map points to scene coordinates
        mapped_points = [self.ax.coords_to_point(x, y) for x, y in points]

        # Draw triangles
        for tri in delaunay.simplices:
            triangle_vertices = [mapped_points[i] for i in tri]
            triangle = Polygon(*triangle_vertices,
                               color=YELLOW, fill_opacity=0.3)
            self.add(triangle)

            # Draw circumcircles for each triangle
            p1, p2, p3 = [points[i] for i in tri]
            self.visualize_circumcircle(p1, p2, p3)

        self.wait(1)

    def visualize_circumcircle(self, p1, p2, p3):
        # Calculate circumcenter and radius
        A = np.array(p1)
        B = np.array(p2)
        C = np.array(p3)

        # Solve for the circumcenter
        D = 2 * (A[0] * (B[1] - C[1]) +
                 B[0] * (C[1] - A[1]) +
                 C[0] * (A[1] - B[1]))
        Ux = ((A[0]**2 + A[1]**2) * (B[1] - C[1]) +
              (B[0]**2 + B[1]**2) * (C[1] - A[1]) +
              (C[0]**2 + C[1]**2) * (A[1] - B[1])) / D
        Uy = ((A[0]**2 + A[1]**2) * (C[0] - B[0]) +
              (B[0]**2 + B[1]**2) * (A[0] - C[0]) +
              (C[0]**2 + C[1]**2) * (B[0] - A[0])) / D
        circumcenter = np.array([Ux, Uy])

        # Calculate the radius as the distance from the circumcenter to any vertex
        radius = np.linalg.norm(circumcenter - A)

        # Map circumcenter and radius to the scene
        circumcenter_mapped = self.ax.coords_to_point(*circumcenter)
        radius_mapped = self.ax.c2p(radius, 0)[0] - self.ax.c2p(0, 0)[0]

        # Draw the circumcircle
        circumcircle = Circle(radius=radius_mapped, color=YELLOW)
        circumcircle.move_to(circumcenter_mapped)
        self.add(circumcircle)

        # Wait briefly to visualize
        self.wait(0.5)
        # Remove the circumcircle
        self.remove(circumcircle)
