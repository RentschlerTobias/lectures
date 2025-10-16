
import pickle
from manim import *
import torch
import torch_geometric
# Define the animation class
class IndirectMeshTransformation(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera.background_color = WHITE  # Set background color to white

    def construct(self):
        with open('meshDataset.pkl', 'rb') as file: 
            meshDataSet = pickle.load(file)
        
        scaling_factor = 10  # Scale the mesh for better visibility

        # Load the first mesh
        self.mesh_id = 0
        self.mesh = meshDataSet[self.mesh_id]

        # Get nodes and adjust z-dimension to 0 for 2D plotting
        self.nodes = self.mesh.x
        self.nodes[:, 2] = 0  # Assuming x has 3 dimensions, adjust for 2D display
        self.nodes *= scaling_factor

        # Center the mesh by shifting nodes
        center = self.nodes.mean(axis=0)  # Calculate center of the mesh
        self.nodes -= center  # Shift the mesh to center it at the origin

        # Adjust the camera to ensure the entire mesh is visible
        max_distance = torch.norm(self.nodes, dim=1).max().item()
        self.camera.frame_width = 2 * max_distance + 1  # Adjust frame width
        self.camera.frame_center = ORIGIN  # Center the camera on the origin

        # Initial and final edge connections
        self.edges_init = self.mesh.train_edges.T.numpy()  # Convert to numpy for processing
        self.edges_final = self.mesh.true_edges.T.numpy()

        # Create dots for the nodes
        dots = []
        for n in range(self.nodes.size(0)):
            node = self.nodes[n, :].numpy()
            dot = Dot(node, color=BLUE)  # Use the first two dimensions for positioning
            dots.append(dot)

        # Group all dots into a single object
        node_group = VGroup(*dots)

        # Add the dots to the scene
        self.play(FadeIn(node_group), run_time=2)

        # Draw initial edges
        init_edges = self.create_edges(self.edges_init, dots, color=BLACK)
        self.play(Create(init_edges), run_time=2)
        self.wait(2)
        

        # Transition to final edges
        final_edges = self.create_edges(self.edges_final, dots, color=BLACK)
        self.play(FadeIn(final_edges),run_time =1)
        self.play(FadeOut(init_edges),run_time =2)
        #        self.play(Transform(init_edges, final_edges), run_time=2)
        self.wait(2)

    def create_edges(self, edges, dots, color):
        """Helper function to create edges between nodes."""
        lines = []
        for edge in edges:
            start_idx, end_idx = edge
            line = Line(
                dots[start_idx].get_center(), 
                dots[end_idx].get_center(), 
                color=color
            )
            lines.append(line)
        return VGroup(*lines)

