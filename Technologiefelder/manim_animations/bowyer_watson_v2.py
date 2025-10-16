from manim import *
import numpy as np

class BowyerWatsonVisualization(Scene):
    def construct(self):
        self.camera.save_png = True
        self.num_img = 0 
        self.camera.background_color = WHITE 
        axes = Axes(
            x_range=[-1.2, 2.2, 1.0],
            y_range=[-1.2, 2.0, 1.0],
            x_length=8,
            y_length=6,
            axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 1},"color":BLACK},
        ).to_edge(DOWN)
        self.play(Create(axes))
        self.wait(1)

        # Generate random points in [0, 1] x [0, 1]
        num_points = 14  # You can change the number of points here
        #point_array = np.random.rand(num_points, 2)
        #point_array = np.array([[0.0,0.5],[1.0,0.5],[0.75,0.8],[0.75,0.2]])        # Draw points
        point_array = np.array([[0.0,0.5],[1.0,0.5],[0.75,1.0],[0.75,0.0]])        # Draw points
        point_list = point_array.tolist()

        point_dots = []
        for point in point_list:
            dot = Dot(axes.coords_to_point(*point), color=BLACK)
            point_dots.append(dot)
            self.play(FadeIn(dot), run_time=0.3)
        #self.capture_mobject_frame(output_file=f"frames/bowyer_watson_algo_{num_image}.png")
        #self.num_img  +=1
        self.wait(1)

        # Create super triangle that contains all points
        super_triangle_vertices = [
            [-1, -1],
            [2, -1],
            [0.5, 2],
        ]

        super_triangle_points = [axes.coords_to_point(*v) for v in super_triangle_vertices]

        super_triangle = Polygon(*super_triangle_points, stroke_color=BLUE)
        self.play(Create(super_triangle))
        #self.capture_mobject_frame(output_file=f"frames/bowyer_watson_algo_{num_image}.png")
        #self.num_img  +=1
        self.wait(1)

        # Initialize triangulation with super triangle
        triangulation = [super_triangle_vertices]
        triangle_mobs = [super_triangle]

        # Start Bowyer-Watson algorithm visualization
        for point_index, point in enumerate(point_list):
            # Highlight current point
            current_dot = point_dots[point_index]
            self.play(current_dot.animate.set_color(YELLOW), run_time=0.3)
           # self.capture_mobject_frame(output_file=f"frames/bowyer_watson_algo_{num_image}.png")
            #self.num_img  +=1
            self.wait(1.0)

            # Find bad triangles
            bad_triangles = []
            bad_triangle_mobs = []
            circumcircles = []

            for tri_index, triangle in enumerate(triangulation):
                a, b, c = triangle
                cc_center, cc_radius = self.get_circumcircle(a, b, c)
                circle_center_point = axes.coords_to_point(*cc_center)
                # Transform circumcircle radius to the screen space
                x_unit_length = axes.x_length / (axes.x_range[1] - axes.x_range[0])
                y_unit_length = axes.y_length / (axes.y_range[1] - axes.y_range[0])
                average_unit_length = (x_unit_length + y_unit_length) / 2

                circumcircle = Circle(
                radius=cc_radius * average_unit_length,
                color=GREEN,
                stroke_opacity=0.5,
                ).move_to(circle_center_point)
                self.play(Create(circumcircle), run_time=0.3)

                dist = np.linalg.norm(np.array(point) - np.array(cc_center))
                if dist < cc_radius:
                    bad_triangles.append(triangle)
                    bad_triangle_mobs.append(triangle_mobs[tri_index])
                   # self.play(Create(circumcircle), run_time=0.3)
                    self.play(
                        triangle_mobs[tri_index].animate.set_fill(RED, opacity=0.5),
                        run_time=0.3,
                    )
                else:
                        self.play(FadeOut(circumcircle), run_time=0.3)

                circumcircles.append(circumcircle)

    # Remove circumcircles
            edges = []
            for triangle in bad_triangles:
                edges.extend(
                    [(triangle[i], triangle[(i + 1) % 3]) for i in range(3)]
                )

            edge_counts = {}
            for edge in edges:
                sorted_edge = tuple(map(tuple, sorted(edge, key=lambda x: (x[0], x[1]))))
                edge_counts[sorted_edge] = edge_counts.get(sorted_edge, 0) + 1
            polygon = [edge for edge, count in edge_counts.items() if count == 1]

            # Highlight boundary edges
            boundary_edges = []
            for edge in polygon:
                start_point = axes.coords_to_point(*edge[0])
                end_point = axes.coords_to_point(*edge[1])
                edge_mob = Line(start_point, end_point, color=YELLOW)
                boundary_edges.append(edge_mob)
                self.play(Create(edge_mob), run_time=0.3)
#            for circumcircle in circumcircles:
#                if circumcircle in self.mobjects:
#                    self.remove(circumcircle)
            # Find the boundary of the polygonal hole
 
            # Remove bad triangles from triangulation
            for bad_triangle_mob in bad_triangle_mobs:
                self.play(FadeOut(bad_triangle_mob), run_time=0.3)
                triangle_mobs.remove(bad_triangle_mob)
            for bad_triangle in bad_triangles:
                triangulation.remove(bad_triangle)

            # Re-triangulate the polygonal hole
            new_triangles = []
            new_triangle_mobs = []
            for edge in polygon:
                new_triangle_vertices = [edge[0], edge[1], point]
                new_triangles.append(new_triangle_vertices)
                triangle_points = [
                    axes.coords_to_point(*v) for v in new_triangle_vertices
                ]
                new_triangle_mob = Polygon(
                    *triangle_points,
                    stroke_color=BLUE,
                    fill_color=WHITE,
                    fill_opacity=0.3,
                )
                new_triangle_mobs.append(new_triangle_mob)
                self.play(Create(new_triangle_mob), run_time=0.3)

            triangulation.extend(new_triangles)
            triangle_mobs.extend(new_triangle_mobs)

            # Remove boundary edges
            for edge_mob in boundary_edges:
                self.play(FadeOut(edge_mob), run_time=0.3)

            # Reset the color of the current point
            self.play(current_dot.animate.set_color(BLACK), run_time=0.3)
            for circumcircle in circumcircles:
                if circumcircle in self.mobjects:
                    self.remove(circumcircle)
 
        # Remove triangles containing vertices from original super triangle
        triangles_to_remove = []
        triangles_to_remove_mobs = []
        super_triangle_vertices_set = set(tuple(v) for v in super_triangle_vertices)
        for i, triangle in enumerate(triangulation):
            if any(tuple(vertex) in super_triangle_vertices_set for vertex in triangle):
                triangles_to_remove.append(triangle)
                triangles_to_remove_mobs.append(triangle_mobs[i])

        for triangle_mob in triangles_to_remove_mobs:
            self.play(FadeOut(triangle_mob), run_time=0.3)
            triangle_mobs.remove(triangle_mob)

        # Remove super triangle
        self.play(FadeOut(super_triangle), run_time=0.3)

        self.wait(2)

    def get_circumcircle(self, a, b, c):
        # Compute the circumcenter and radius of the triangle abc
        ax, ay = a
        bx, by = b
        cx, cy = c

        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-10:
            # Points are colinear or too close together
            center = [(ax + bx + cx) / 3, (ay + by + cy) / 3]
            radius = 1e10
            return center, radius

        ux = (
            (ax ** 2 + ay ** 2) * (by - cy)
            + (bx ** 2 + by ** 2) * (cy - ay)
            + (cx ** 2 + cy ** 2) * (ay - by)
        ) / d
        uy = (
            (ax ** 2 + ay ** 2) * (cx - bx)
            + (bx ** 2 + by ** 2) * (ax - cx)
            + (cx ** 2 + cy ** 2) * (bx - ax)
        ) / d

        center = [ux, uy]
        radius = np.sqrt((ux - ax) ** 2 + (uy - ay) ** 2)

        return center, radius
