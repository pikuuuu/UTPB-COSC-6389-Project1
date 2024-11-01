import math
import random
import tkinter as tk
from tkinter import *
import numpy as np

num_cities = 25
num_roads = 100
city_scale = 5
road_width = 4
padding = 100


POPULATION_SIZE = 100
MUTATION_RATE = 0.01
GENERATIONS = 1000


NUM_ANTS = 20
ALPHA = 1  
BETA = 2  
RHO = 0.1  
Q = 100  
MAX_ITERATIONS = 100


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x - city_scale, self.y - city_scale, self.x + city_scale, self.y + city_scale,
                           fill=color)


class Edge:
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def draw(self, canvas, color='grey', style=(2, 4)):
        canvas.create_line(self.city_a.x,
                           self.city_a.y,
                           self.city_b.x,
                           self.city_b.y,
                           fill=color,
                           width=road_width,
                           dash=style)


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Traveling Salesman")
        self.option_add("*tearOff", FALSE)
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (width, height))
        self.state("zoomed")
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)

        self.w = width - padding
        self.h = height - padding * 2
        self.cities_list = []
        self.roads_list = []
        self.edge_list = []

        self.iteration_label = Label(self, text="Iteration: 0")
        self.iteration_label.place(x=10, y=10)
        self.distance_label = Label(self, text="Best Distance: N/A")
        self.distance_label.place(x=10, y=40)

        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_TS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)
        menu_TS.add_command(label="Generate", command=self.generate, underline=0)

        menu_solve = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_solve, label='Solve', underline=0)
        menu_solve.add_command(label="Genetic Algorithm", command=self.start_solving_ga, underline=0)
        menu_solve.add_command(label="Ant Colony Optimization", command=self.start_solving_aco, underline=0)

        self.mainloop()

    def generate(self):
        self.generate_city()
        self.draw_city()
        self.update_info(0, float('inf'))

    def generate_city(self):
        self.cities_list = []
        self.roads_list = []
        self.edge_list = []
        for _ in range(num_cities):
            self.add_city()
        for _ in range(num_roads):
            self.add_road()

    def add_city(self):
        x = random.randint(padding, self.w)
        y = random.randint(padding, self.h)
        node = Node(x, y)
        self.cities_list.append(node)

    def add_road(self):
        a = random.randint(0, len(self.cities_list) - 1)
        b = random.randint(0, len(self.cities_list) - 1)
        road = f'{min(a, b)},{max(a, b)}'
        while a == b or road in self.roads_list:
            a = random.randint(0, len(self.cities_list) - 1)
            b = random.randint(0, len(self.cities_list) - 1)
            road = f'{min(a, b)},{max(a, b)}'
        edge = Edge(self.cities_list[a], self.cities_list[b])
        self.roads_list.append(road)
        self.edge_list.append(edge)

    def draw_city(self):
        self.canvas.delete("all")
        for e in self.edge_list:
            e.draw(self.canvas)
        for n in self.cities_list:
            n.draw(self.canvas)

    
    def start_solving_ga(self):
        self.after(100, self.genetic_algorithm)

    def initialize_population(self):
        return [self.generate_random_tour() for _ in range(POPULATION_SIZE)]

    def generate_random_tour(self):
        return random.sample(range(len(self.cities_list)), len(self.cities_list))

    def fitness(self, tour):
        total_distance = self.calculate_tour_distance(tour)
        return 1 / total_distance, total_distance

    def crossover(self, parent1, parent2):
        start = random.randint(0, len(parent1) - 1)
        end = random.randint(start + 1, len(parent1))
        child = [-1] * len(parent1)
        child[start:end] = parent1[start:end]
        remaining = [item for item in parent2 if item not in child]
        for i in range(len(child)):
            if child[i] == -1:
                child[i] = remaining.pop(0)
        return child

    def mutate(self, tour):
        if random.random() < MUTATION_RATE:
            i, j = random.sample(range(len(tour)), 2)
            tour[i], tour[j] = tour[j], tour[i]
        return tour

    def genetic_algorithm(self):
        population = self.initialize_population()
        best_tour = None
        best_fitness = 0
        best_distance = float('inf')

        for generation in range(GENERATIONS):
            population = sorted(population, key=lambda x: self.fitness(x)[0], reverse=True)

            current_fitness, current_distance = self.fitness(population[0])
            if current_fitness > best_fitness:
                best_tour = population[0]
                best_fitness = current_fitness
                best_distance = current_distance
                self.draw_tour(best_tour)
                self.update_info(generation + 1, best_distance)
                self.update()

            new_population = population[:2]  

            while len(new_population) < POPULATION_SIZE:
                parent1, parent2 = random.choices(population[:20], k=2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)

            population = new_population

        return best_tour

    
    def start_solving_aco(self):
        self.after(100, self.ant_colony_optimization)

    def initialize_pheromones(self):
        n = len(self.cities_list)
        return np.ones((n, n))

    def ant_colony_optimization(self):
        n = len(self.cities_list)
        pheromones = self.initialize_pheromones()
        best_tour = None
        best_distance = float('inf')

        for iteration in range(MAX_ITERATIONS):
            ant_tours = []
            ant_distances = []

            for _ in range(NUM_ANTS):
                tour = self.construct_solution(pheromones)
                distance = self.calculate_tour_distance(tour)
                ant_tours.append(tour)
                ant_distances.append(distance)

                if distance < best_distance:
                    best_distance = distance
                    best_tour = tour
                    self.draw_tour(best_tour)
                    self.update_info(iteration + 1, best_distance)
                    self.update()

            self.update_pheromones(pheromones, ant_tours, ant_distances)

        return best_tour

    def construct_solution(self, pheromones):
        n = len(self.cities_list)
        unvisited = set(range(n))
        start = random.randint(0, n - 1)
        tour = [start]
        unvisited.remove(start)

        while unvisited:
            current = tour[-1]
            probabilities = self.calculate_probabilities(current, unvisited, pheromones)
            next_city = random.choices(list(unvisited), weights=probabilities)[0]
            tour.append(next_city)
            unvisited.remove(next_city)

        return tour

    def calculate_probabilities(self, current, unvisited, pheromones):
        probabilities = []
        for city in unvisited:
            distance = self.calculate_distance(self.cities_list[current], self.cities_list[city])
            pheromone = pheromones[current][city]
            probability = (pheromone ** ALPHA) * ((1 / distance) ** BETA)
            probabilities.append(probability)
        return probabilities

    def update_pheromones(self, pheromones, ant_tours, ant_distances):
        n = len(self.cities_list)
        pheromones *= (1 - RHO)  

        for tour, distance in zip(ant_tours, ant_distances):
            for i in range(n):
                from_city = tour[i]
                to_city = tour[(i + 1) % n]
                pheromones[from_city][to_city] += Q / distance
                pheromones[to_city][from_city] += Q / distance

   
    def calculate_tour_distance(self, tour):
        total_distance = 0
        n = len(tour)
        for i in range(n):
            from_city = self.cities_list[tour[i]]
            to_city = self.cities_list[tour[(i + 1) % n]]
            total_distance += self.calculate_distance(from_city, to_city)
        return total_distance

    def calculate_distance(self, city1, city2):
        return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)

    def draw_tour(self, tour):
        self.canvas.delete("all")
        for i in range(len(tour)):
            from_city = self.cities_list[tour[i]]
            to_city = self.cities_list[tour[(i + 1) % len(tour)]]
            self.canvas.create_line(from_city.x, from_city.y, to_city.x, to_city.y, fill='red', width=road_width)
        for city in self.cities_list:
            city.draw(self.canvas, 'blue')

    def update_info(self, iteration, distance):
        self.iteration_label.config(text=f"Iteration: {iteration}")
        self.distance_label.config(text=f"Best Distance: {distance:.2f}")


if __name__ == '__main__':
    UI()