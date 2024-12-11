import math
import random
import tkinter as tk
from tkinter import *
import threading

num_elements = 100
fraction_target = 0.7
min_val = 128
max_val = 2048

padding_screen = 25
padding_element = 5
border_thickness = 5

num_iterations = 1000
population_size = 50
elite_count = 2
mutation_probability = 0.1

delay_time = 0.1

def generate_random_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
    return hex_color


class Element:
    def __init__(self):
        self.value = random.randint(min_val, max_val)
        self.color = generate_random_color()
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def place(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, canvas, is_active=False):
        canvas.create_text(self.x + self.width + padding_element + border_thickness * 2, self.y + self.height / 2, text=f'{self.value}')
        if is_active:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.width,
                                    self.y + self.height,
                                    fill=self.color,
                                    outline=self.color,
                                    width=border_thickness)
        else:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.width,
                                    self.y + self.height,
                                    fill='',
                                    outline=self.color,
                                    width=border_thickness)


class KnapsackUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Knapsack Solver")
        self.option_add("*tearOff", FALSE)
        self.screen_width, self.screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.screen_width, self.screen_height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.screen_width, height=self.screen_height)

        self.element_list = []

        menu_bar = Menu(self)
        self['menu'] = menu_bar

        menu_knapsack = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_knapsack, label='Knapsack', underline=0)

        def generate_elements():
            self.create_knapsack()
            self.render_elements()

        menu_knapsack.add_command(label="Generate", command=generate_elements, underline=0)

        self.target_value = 0

        def set_target_value():
            selected_elements = random.sample(self.element_list, int(num_elements * fraction_target))
            self.target_value = sum(element.value for element in selected_elements)
            self.render_target()

        menu_knapsack.add_command(label="Set Target", command=set_target_value, underline=0)

        def initiate_thread():
            thread = threading.Thread(target=self.execute, args=())
            thread.start()

        menu_knapsack.add_command(label="Run", command=initiate_thread, underline=0)

        self.mainloop()

    def get_random_element(self):
        element = Element()
        for existing_element in self.element_list:
            if element.value == existing_element.value:
                return None
        return element

    def add_element(self):
        element = self.get_random_element()
        while element is None:
            element = self.get_random_element()
        self.element_list.append(element)

    def create_knapsack(self):
        for i in range(num_elements):
            self.add_element()

        max_value = 0
        min_value = 9999
        for element in self.element_list:
            min_value = min(min_value, element.value)
            max_value = max(max_value, element.value)

        width = self.screen_width - padding_screen
        height = self.screen_height - padding_screen
        rows = math.ceil(num_elements / 6)
        row_width = width / 8 - padding_element
        row_height = (height - 200) / rows

        for x in range(0, 6):
            for y in range(0, rows):
                if x * rows + y >= num_elements:
                    break
                element = self.element_list[x * rows + y]
                element_width = row_width / 2
                element_height = max(element.value / max_value * row_height, 1)
                element.place(padding_screen + x * row_width + x * padding_element,
                              padding_screen + y * row_height + y * padding_element,
                              element_width,
                              element_height)

    def clear_canvas(self):
        self.canvas.delete("all")

    def render_elements(self):
        for element in self.element_list:
            element.draw(self.canvas)

    def render_target(self):
        x = (self.screen_width - padding_screen) / 8 * 7
        y = padding_screen
        width = (self.screen_width - padding_screen) / 8 - padding_screen
        height = self.screen_height / 2 - padding_screen
        self.canvas.create_rectangle(x, y, x + width, y + height, fill='black')
        self.canvas.create_text(x + width // 2, y + height + padding_screen, text=f'{self.target_value}', font=('Arial', 18))

    def render_sum(self, total_sum, target):
        x = (self.screen_width - padding_screen) / 8 * 6
        y = padding_screen
        width = (self.screen_width - padding_screen) / 8 - padding_screen
        height = self.screen_height / 2 - padding_screen
        height *= (total_sum / target)
        self.canvas.create_rectangle(x, y, x + width, y + height, fill='black')
        self.canvas.create_text(x + width // 2, y + height + padding_screen, text=f'{total_sum}', font=('Arial', 18))

    def render_genome(self, genome, generation_number):
        for i in range(num_elements):
            element = self.element_list[i]
            active = genome[i]
            element.draw(self.canvas, active)
        x = (self.screen_width - padding_screen) / 8 * 6
        y = padding_screen
        width = (self.screen_width - padding_screen) / 8 - padding_screen
        height = self.screen_height / 4 * 3
        self.canvas.create_text(x + width, y + height + padding_screen * 2, text=f'Generation {generation_number}', font=('Arial', 18))

    def execute(self):
        global population_size
        global num_iterations

        def calculate_sum(genome):
            total = sum(self.element_list[i].value for i in range(len(genome)) if genome[i])
            return total

        def evaluate_fitness(genome):
            return abs(calculate_sum(genome) - self.target_value)

        def generate_population(previous_population=None, fitness_values=None):
            population = []
            if previous_population is None:
                for _ in range(population_size):
                    genome = [random.random() < fraction_target for _ in range(num_elements)]
                    population.append(genome)
                return population
            else:
                elites = [previous_population[i] for i in range(elite_count)]
                population.extend(elites)

                while len(population) < population_size:
                    parents = random.sample(previous_population, 2)
                    crossover_point = random.randint(0, num_elements - 1)
                    child = parents[0][:crossover_point] + parents[1][crossover_point:]
                    if random.random() < mutation_probability:
                        mutate_index = random.randint(0, num_elements - 1)
                        child[mutate_index] = not child[mutate_index]
                    population.append(child)

                return population

        def process_generation(generation=0, current_population=None):
            if generation >= num_iterations:
                return

            if current_population is None:
                current_population = generate_population()

            fitness_values = sorted(current_population, key=evaluate_fitness)
            best_genome = fitness_values[0]
            best_fitness = evaluate_fitness(best_genome)

            self.after(0, self.clear_canvas)
            self.after(0, self.render_target)
            self.after(0, self.render_sum, calculate_sum(best_genome), self.target_value)
            self.after(0, self.render_genome, best_genome, generation)

            if best_fitness == 0:
                print(f'Target met at generation {generation}!')
                return  
            self.after(int(delay_time * 1000), process_generation, generation + 1, generate_population(current_population))

        process_generation()


if __name__ == '__main__':
    KnapsackUI()