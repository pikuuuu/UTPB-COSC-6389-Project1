import math
import random
import tkinter as tk
from tkinter import *
import threading


num_vertices = 20  
num_colors = 4  
edge_probability = 0.2  


screen_padding = 25
node_radius = 15
edge_width = 2


num_generations = 1000
pop_size = 50
elitism_count = 2
mutation_rate = 0.1

sleep_time = 0.1


COLOR_PALETTE = [
    '#FF0000',  # Red
    '#00FF00',  # Green
    '#0000FF',  # Blue
    '#FFFF00',  # Yellow
    '#FF00FF',  # Magenta
    '#00FFFF',  # Cyan
    '#FFA500',  # Orange
    '#800080',  # Purple
    '#008000',  # Dark Green
    '#000080',  # Navy
]


class Graph:
    def __init__(self, num_vertices, edge_probability):
        self.num_vertices = num_vertices
        self.edges = []
        self.vertex_positions = {}

       
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if random.random() < edge_probability:
                    self.edges.append((i, j))

        
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            radius = 0.8  
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.vertex_positions[i] = (x, y)

    def get_edges(self):
        return self.edges

    def get_neighbors(self, vertex):
        neighbors = []
        for edge in self.edges:
            if edge[0] == vertex:
                neighbors.append(edge[1])
            elif edge[1] == vertex:
                neighbors.append(edge[0])
        return neighbors

    def get_vertex_position(self, vertex):
        return self.vertex_positions[vertex]


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Graph Coloring Solver")
        self.option_add("*tearOff", FALSE)

       
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

      
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

       
        self.graph = None

        
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_graph = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_graph, label='Graph Coloring', underline=0)

       
        menu_graph.add_command(label="Generate Graph", command=self.generate_graph, underline=0)
        menu_graph.add_command(label="Run Algorithm", command=self.start_thread, underline=0)

        
        self.best_fitness = float('inf')
        self.current_conflicts = 0

        self.mainloop()

    def generate_graph(self):
        self.graph = Graph(num_vertices, edge_probability)
        self.clear_canvas()
        self.draw_graph()

    def clear_canvas(self):
        self.canvas.delete("all")

    def transform_coordinates(self, x, y):
        
        padding = 100 
        screen_x = (x + 1) * (self.width - 2 * padding) / 2 + padding
        screen_y = (y + 1) * (self.height - 2 * padding) / 2 + padding
        return screen_x, screen_y

    def draw_graph(self, coloring=None):
        if not self.graph:
            return

        
        for edge in self.graph.get_edges():
            v1, v2 = edge
            x1, y1 = self.graph.get_vertex_position(v1)
            x2, y2 = self.graph.get_vertex_position(v2)

           
            x1, y1 = self.transform_coordinates(x1, y1)
            x2, y2 = self.transform_coordinates(x2, y2)

            self.canvas.create_line(x1, y1, x2, y2, width=edge_width, fill='gray')

        
        for vertex in range(self.graph.num_vertices):
            x, y = self.graph.get_vertex_position(vertex)
            x, y = self.transform_coordinates(x, y)

            color = COLOR_PALETTE[coloring[vertex] if coloring else 0]

           
            self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=color, outline='black', width=2
            )

            
            self.canvas.create_text(x, y, text=str(vertex), fill='white')

    def draw_stats(self, generation):
        
        x = self.width - 200
        y = 50

        stats_text = f"Colors used: {num_colors}\n"
        stats_text += f"Current conflicts: {self.current_conflicts}\n"
        stats_text += f"Best fitness: {self.best_fitness}\n"
        stats_text += f"Generation: {generation}"

        self.canvas.create_text(
            x, y,
            text=stats_text,
            font=('Arial', 12),
            anchor='ne'
        )

    def start_thread(self):
        if not self.graph:
            print("Generate a graph first!")
            return
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        def count_conflicts(coloring):
            conflicts = 0
            for edge in self.graph.get_edges():
                v1, v2 = edge
                if coloring[v1] == coloring[v2]:
                    conflicts += 1
            return conflicts

        def fitness(genome):
            return count_conflicts(genome)

        def create_initial_population():
            population = []
            for _ in range(pop_size):
                
                genome = [random.randint(0, num_colors - 1) for _ in range(num_vertices)]
                population.append(genome)
            return population

        def select_parents(population, fitnesses):
            
            def tournament_select():
                tournament_size = 3
                tournament = random.sample(list(enumerate(fitnesses)), tournament_size)
                winner_idx = min(tournament, key=lambda x: x[1])[0]
                return population[winner_idx]

            return tournament_select(), tournament_select()

        def crossover(parent1, parent2):
            
            crossover_points = sorted(random.sample(range(len(parent1)), 2))
            child = parent1[:crossover_points[0]] + \
                    parent2[crossover_points[0]:crossover_points[1]] + \
                    parent1[crossover_points[1]:]
            return child

        def mutate(genome):
            if random.random() < mutation_rate:
                
                point = random.randint(0, len(genome) - 1)
                new_color = random.randint(0, num_colors - 1)
                while new_color == genome[point]: 
                    new_color = random.randint(0, num_colors - 1)
                genome[point] = new_color
            return genome

        def evolution_step(generation=0, population=None):
            if generation >= num_generations:
                return

            if population is None:
                population = create_initial_population()

            
            population_fitness = [(genome, fitness(genome)) for genome in population]
            population_fitness.sort(key=lambda x: x[1])

            best_genome = population_fitness[0][0]
            self.best_fitness = population_fitness[0][1]
            self.current_conflicts = self.best_fitness

            print(f'Generation {generation}, Conflicts: {self.best_fitness}')

            
            self.after(0, self.clear_canvas)
            self.after(0, self.draw_graph, best_genome)
            self.after(0, self.draw_stats, generation)  

            if self.best_fitness == 0:  
                return

         
            new_population = []

            
            new_population.extend([genome for genome, _ in population_fitness[:elitism_count]])

            
            while len(new_population) < pop_size:
                parent1, parent2 = select_parents(
                    [genome for genome, _ in population_fitness],
                    [fitness for _, fitness in population_fitness]
                )
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_population.append(child)

            
            self.after(int(sleep_time * 1000), evolution_step, generation + 1, new_population)

        
        evolution_step()



if __name__ == "__main__":
    UI()
