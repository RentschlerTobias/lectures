from manim import *
import numpy as np

class BowyerWatsonVisualization(Scene):
    def construct(self):
        self.camera.save_png = True
        self.num_img = 0 
#        self.camera.background_color = WHITE 
        axes = Axes(
            x_range=[-2.0, 3.0, 1.0],
            y_range=[-2.0, 2.0, 1.0],
            x_length=8,
            y_length=6,
            axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 1}},
        ).to_edge(DOWN)
        self.play(Create(axes))
        self.wait(1)

        # Generate random points in [0, 1] x [0, 1]
        num_points = 8  # You can change the number of points here
        point_array = np.random.rand(num_points, 2)
        point_list = point_array.tolist()

        # Draw points
        point_dots = []
        for point in point_list:
            dot = Dot(axes.coords_to_point(*point), color=WHITE)
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
                
                # Convert triangle vertices to screen coordinates
                point_a = axes.coords_to_point(*a)
                point_b = axes.coords_to_point(*b)
                point_c = axes.coords_to_point(*c)
                
                # Create circumcircle using Manim's built-in method
                try:
                    circumcircle = Circle.from_three_points(
                        point_a, point_b, point_c,
                        color=GREEN,
                        stroke_opacity=0.5,
                    )
                    self.play(Create(circumcircle), run_time=0.3)
                    
                    self.wait(1.0)
                    # Get circumcenter and radius in coordinate space for point-in-circle test
                    cc_center, cc_radius = self.get_circumcircle(a, b, c)
                    
                    # Check if current point is inside circumcircle
                    dist = np.linalg.norm(np.array(point) - np.array(cc_center))
                    if dist < cc_radius:
                        bad_triangles.append(triangle)
                        bad_triangle_mobs.append(triangle_mobs[tri_index])
                        self.play(
                            triangle_mobs[tri_index].animate.set_fill(RED, opacity=0.5),
                            run_time=0.3,
                        )
                    else:
                        self.play(FadeOut(circumcircle), run_time=0.3)
                        
                except Exception as e:
                    # Fallback if three points are collinear or other issues
                    print(f"Could not create circumcircle for triangle {triangle}: {e}")
                    continue

                circumcircles.append(circumcircle)

            # Remove circumcircles
            for circumcircle in circumcircles:
                if circumcircle in self.mobjects:
                    self.remove(circumcircle)
            
            # Find the boundary of the polygonal hole
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
            self.play(current_dot.animate.set_color(WHITE), run_time=0.3)

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
        # Using a more numerically stable method
        ax, ay = a
        bx, by = b
        cx, cy = c
        
        # Convert to numpy arrays for easier computation
        A = np.array([ax, ay])
        B = np.array([bx, by])
        C = np.array([cx, cy])
        
        # Calculate the perpendicular bisectors
        # Midpoints
        mid_AB = (A + B) / 2
        mid_BC = (B + C) / 2
        
        # Direction vectors
        dir_AB = B - A
        dir_BC = C - B
        
        # Perpendicular vectors (rotate 90 degrees)
        perp_AB = np.array([-dir_AB[1], dir_AB[0]])
        perp_BC = np.array([-dir_BC[1], dir_BC[0]])
        
        # Check if points are collinear
        cross_product = np.cross(dir_AB, dir_BC)
        if abs(cross_product) < 1e-10:
            # Points are collinear or too close together
            center = [(ax + bx + cx) / 3, (ay + by + cy) / 3]
            radius = 1e10
            return center, radius
        
        # Solve for intersection of perpendicular bisectors
        # mid_AB + t1 * perp_AB = mid_BC + t2 * perp_BC
        # This gives us a 2x2 system: [perp_AB, -perp_BC] * [t1, t2] = mid_BC - mid_AB
        
        matrix = np.column_stack([perp_AB, -perp_BC])
        rhs = mid_BC - mid_AB
        
        try:
            t_values = np.linalg.solve(matrix, rhs)
            t1 = t_values[0]
            
            # Calculate circumcenter
            circumcenter = mid_AB + t1 * perp_AB
            
            # Calculate radius (distance from circumcenter to any vertex)
            radius = np.linalg.norm(circumcenter - A)
            
            # Verify the calculation by checking distances to all three vertices
            dist_A = np.linalg.norm(circumcenter - A)
            dist_B = np.linalg.norm(circumcenter - B)
            dist_C = np.linalg.norm(circumcenter - C)
            
            # Use the average for better numerical stability
            radius = (dist_A + dist_B + dist_C) / 3
            
            return circumcenter.tolist(), radius
            
        except np.linalg.LinAlgError:
            # Fallback to original method if matrix is singular
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) < 1e-10:
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
