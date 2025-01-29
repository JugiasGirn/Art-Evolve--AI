
import numpy as np
import matplotlib.pyplot as plt
import random
import os
import colorsys
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg
import tkinter.messagebox as messagebox


class ArtEvolve:
    def __init__(self, population_size=5, generations=3, mutation_rate=0.6, canvas_size=(800, 800)):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.genome_length = 500# Number of shapes that each image is going to have
        self.canvas_size = canvas_size
        self.shape_types = [ 'triangle','rectangle', 'star', 'spiral','circle']#,
        self.color_palettes = self.generate_color_palettes()
        self.population = self.initialize_population()
        self.output_dir = "evolved_art"

        # Ensure output directory exists
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"Output directory created/verified: {self.output_dir}")
        except Exception as e:
            print(f"Error creating output directory: {e}")

    def generate_color_palettes(self):
        # Generating a list of color palettes
        palettes = []
        for _ in range(10):  # Creates 10 different palettes
            base_hue = random.random()
            palette = []
            for i in range(5):  # Each palette has 5 colors
                hue = (base_hue + i * 0.1) % 1.0
                saturation = random.uniform(0.5, 1.0)
                lightness = random.uniform(0.4, 0.7)
                rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
                palette.append(rgb)
            palettes.append(palette)
        return palettes

    def initialize_population(self):
        # Population is initialized with random genomes
        population = []
        for _ in range(self.population_size):
            genome = {
                'shapes': [self.random_shape() for _ in range(self.genome_length)],
                'color_palette': random.choice(self.color_palettes)
            }
            population.append(genome)
        return population

    def random_shape(self):
        # Generating a random shape
        return {
            'type': random.choice(self.shape_types),
            'position': (random.uniform(0, 1), random.uniform(0, 1)),
            'size': random.uniform(0.02, 0.15),
            'rotation': random.uniform(0, 360),
            'opacity': random.uniform(0.3, 0.8),
            'complexity': random.uniform(0.2, 1.0)
        }

    def render_genome(self, genome):
        # Render the genome into a PIL image using FigureCanvasAgg
        try:
            fig = plt.Figure(figsize=(8, 8))
            canvas = FigureCanvasAgg(fig)
            ax = fig.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            # Draw the shapes
            for shape in genome['shapes']:
                self.draw_shape(ax, shape, genome['color_palette'])

            # Rendering the figure to a canvas
            canvas.draw()

            # Convert the canvas to a PIL image
            buf = canvas.buffer_rgba()
            width, height = fig.get_size_inches() * fig.get_dpi()
            pil_image = Image.frombuffer('RGBA', (int(width), int(height)), buf, 'raw', 'RGBA', 0, 1)
            plt.close(fig)
            return pil_image
        except Exception as e:
            print(f"Error rendering genome: {e}")
            return None

    def draw_shape(self, ax, shape, color_palette):
        # Draw a shape on the matplotlib axis
        shape_type = shape['type']
        x, y = shape['position']
        size = shape['size']
        rotation = shape['rotation']
        opacity = shape['opacity']
        color = random.choice(color_palette)
        color_with_opacity = (*color, opacity)

        if shape_type == 'circle':
            circle = plt.Circle((x, y), size, color=color_with_opacity)
            ax.add_artist(circle)
        elif shape_type == 'rectangle':
            rect = plt.Rectangle((x - size / 2, y - size / 2), size, size,
                                 angle=rotation, color=color_with_opacity)
            ax.add_patch(rect)
        elif shape_type == 'triangle':
            triangle = plt.Polygon(self.get_polygon_points(x, y, size, 3, rotation),
                                   color=color_with_opacity)
            ax.add_patch(triangle)
        elif shape_type == 'star':
            star = plt.Polygon(self.get_star_points(x, y, size, rotation),
                               color=color_with_opacity)
            ax.add_patch(star)
        elif shape_type == 'spiral':
            pass

    def get_polygon_points(self, x_center, y_center, radius, sides, rotation):
        points = []
        angle = np.deg2rad(rotation)
        for i in range(sides):
            theta = 2 * np.pi * i / sides + angle
            x = x_center + radius * np.cos(theta)
            y = y_center + radius * np.sin(theta)
            points.append([x, y])
        return points

    def get_star_points(self, x_center, y_center, radius, rotation):
        points = []
        angle = np.deg2rad(rotation)
        for i in range(10):  # 5-pointed star (10 vertices)
            r = radius if i % 2 == 0 else radius * 0.5  # Alternate radii
            theta = np.pi * i / 5 + angle
            x = x_center + r * np.cos(theta)
            y = y_center + r * np.sin(theta)
            points.append([x, y])
        return points

    def crossover(self, parent1, parent2):
        # Perform crossover between two genomes
        idx = random.randint(0, self.genome_length)
        child1_shapes = parent1['shapes'][:idx] + parent2['shapes'][idx:]
        child2_shapes = parent2['shapes'][:idx] + parent1['shapes'][idx:]
        child1 = {'shapes': child1_shapes, 'color_palette': parent1['color_palette']}
        child2 = {'shapes': child2_shapes, 'color_palette': parent2['color_palette']}
        return child1, child2

    def mutate(self, genome):
        # Randomly It will modify some shapes in the genome
        for shape in genome['shapes']:
            if random.random() < self.mutation_rate:
                shape['size'] = random.uniform(0.02, 0.15)
                shape['rotation'] = random.uniform(0, 360)
                shape['opacity'] = random.uniform(0.3, 0.8)
                shape['complexity'] = random.uniform(0.2, 1.0)

    def save_images(self, generation, population):
        """
        Save the top-rated images from each generation


        """
        # Ensure the output directory exists
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error ensuring output directory exists: {e}")
            return

        # Save top images from the generation
        for idx, genome in enumerate(population):
            try:
                # Render the genome to an image
                pil_image = self.render_genome(genome)

                if pil_image is None:
                    print(f"Skipping image generation for generation {generation}, image {idx + 1}")
                    continue

                # Create filename with generation and index
                filename = os.path.join(
                    self.output_dir,
                    f"generation_{generation}_image_{idx + 1}.png"
                )

                # Save the image
                pil_image.save(filename)
                print(f"Successfully saved image: {filename}")
            except Exception as e:
                print(f"Error saving image for generation {generation}, image {idx + 1}: {e}")

    def get_user_selections(self, genomes, generation):
        images = []
        ratings = {}

        # Render all the images to PIL images
        for genome in genomes:
            pil_image = self.render_genome(genome)
            images.append(pil_image)

        root = tk.Tk()
        root.title(f"Rate Generation {generation + 1}")

        # Creating a canvas and scrollbar
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Instructions
        instruction_label = tk.Label(
            scrollable_frame,
            text="Rate each image from 1 (lowest) to 5 (highest):",
            font=("Arial", 12, "bold")
        )
        instruction_label.pack(pady=10)

        # Display images and ratings
        for idx, pil_image in enumerate(images):
            frame = tk.Frame(scrollable_frame)
            frame.pack(padx=10, pady=10)

            # Display image in tkinter
            photo = ImageTk.PhotoImage(pil_image.resize((250, 250)))
            image_label = tk.Label(frame, image=photo)
            image_label.image = photo  # Keep reference
            image_label.pack()

            # Add rating scale
            rating_var = tk.IntVar(value=3)  # Default rating of 3
            ratings[idx] = rating_var

            rating_frame = tk.Frame(frame)
            rating_frame.pack(pady=5)

            for value in range(1, 6):
                rb = tk.Radiobutton(
                    rating_frame,
                    text=str(value),
                    variable=rating_var,
                    value=value,
                    font=("Arial", 10)
                )
                rb.pack(side=tk.LEFT, padx=5)

        selected_indices = []

        def submit_ratings():
            # Check if all ratings are provided
            for idx, var in ratings.items():
                if var.get() == 0:
                    messagebox.showwarning("Incomplete Ratings", "Please rate all images before submitting.")
                    return
            # Convert ratings to selection indices, favoring higher-rated images
            rated_indices = [(idx, var.get()) for idx, var in ratings.items()]
            # Sort by rating (descending) and select indices of top-rated images
            sorted_indices = [idx for idx, rating in sorted(rated_indices, key=lambda x: x[1], reverse=True)]
            nonlocal selected_indices
            selected_indices = sorted_indices[:max(2, len(sorted_indices) // 2)]  # Select at least 2 images
            root.quit()
            root.destroy()

        # Submit button
        submit_button = tk.Button(
            scrollable_frame,
            text="Submit Ratings",
            command=submit_ratings,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=10
        )
        submit_button.pack(pady=20)

        root.mainloop()
        return selected_indices

    def evolve(self):
        # Main loop for evolution
        for generation in range(self.generations):
            print(f"Generation {generation + 1}/{self.generations}")

            # User rates the preferred images
            selected_indices = self.get_user_selections(self.population, generation)

            if not selected_indices:  # If user closed window without selecting
                print("Evolution terminated by user")
                break

            # Save the current generation's images
            print(f"Saving images for generation {generation + 1}")
            self.save_images(generation + 1, self.population)

            new_population = [self.population[i] for i in selected_indices]

            # Create new Population through crossover and mutation
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(new_population, 2)
                child1, child2 = self.crossover(parent1, parent2)

                # Apply mutation
                if random.random() < self.mutation_rate:
                    self.mutate(child1)
                if random.random() < self.mutation_rate:
                    self.mutate(child2)

                new_population.extend([child1, child2])

            self.population = new_population[:self.population_size]

        # Explicitly save the final population images
        print("Saving final generation images...")
        self.save_images(self.generations, self.population)

        print("Evolution complete!")

    def run(self):
        # Starting the Abstract Art program
        print("Welcome to Evolutionary Art!")
        print("Please rate each image in the upcoming windows.")
        self.evolve()


# Running the program
if __name__ == "__main__":
    art_evolver = ArtEvolve(
        population_size=3,
        generations=3,  # We can adjust the program as needed
        mutation_rate=0.6,
        canvas_size=(800, 800)
    )
    art_evolver.run()