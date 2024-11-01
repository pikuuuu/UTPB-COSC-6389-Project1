import math
import random
import tkinter as tk
from tkinter import *
import threading


NUM_ITEMS = 100
FRAC_TARGET = 0.7
MIN_VALUE = 128
MAX_VALUE = 2048

SCREEN_PADDING = 25
ITEM_PADDING = 5
STROKE_WIDTH = 5


NUM_GENERATIONS = 1000
POP_SIZE = 100  
TOURNAMENT_SIZE = 5  
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.02  
ELITISM_COUNT = 4  

SLEEP_TIME = 0.1

def random_rgb_color():
    """Generate random RGB color in hex format."""
    return '#{:02x}{:02x}{:02x}'.format(
        random.randint(0x10, 0xff),
        random.randint(0x10, 0xff),
        random.randint(0x10, 0xff)
    )

class Item:
    """Represents an item in the knapsack problem."""
    def __init__(self):
        self.value = random.randint(MIN_VALUE, MAX_VALUE)
        self.color = random_rgb_color()
        self.x = self.y = self.w = self.h = 0

    def place(self, x, y, w, h):
        """Set item's position and dimensions."""
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self, canvas, active=False):
        """Draw the item on the canvas."""
        canvas.create_text(
            self.x + self.w + ITEM_PADDING + STROKE_WIDTH*2,
            self.y + self.h/2,
            text=f'{self.value}'
        )
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.w,
            self.y + self.h,
            fill=self.color if active else '',
            outline=self.color,
            width=STROKE_WIDTH
        )

class GeneticAlgorithm:
    """Improved Genetic Algorithm implementation."""
    def __init__(self, items, target):
        self.items = items
        self.target = target
        self.best_solution = None
        self.best_fitness = float('inf')

    def create_individual(self):
        """Create a random individual with balanced initialization."""
        genome = [False] * len(self.items)
        num_ones = int(len(genome) * FRAC_TARGET)
        indices = random.sample(range(len(genome)), num_ones)
        for idx in indices:
            genome[idx] = True
        return genome

    def calculate_fitness(self, genome):
        """Calculate fitness with penalty for exceeding target."""
        total = sum(item.value for item, selected in zip(self.items, genome) if selected)
        if total > self.target:
            
            return abs(total - self.target) * 1.5
        return abs(total - self.target)

    def tournament_selection(self, population):
        """Tournament selection for parent selection."""
        tournament = random.sample(population, TOURNAMENT_SIZE)
        return min(tournament, key=lambda x: self.calculate_fitness(x))

    def uniform_crossover(self, parent1, parent2):
        """Uniform crossover implementation."""
        if random.random() > CROSSOVER_RATE:
            return parent1[:]
        
        child = []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child.append(gene1)
            else:
                child.append(gene2)
        return child

    def adaptive_mutation(self, genome):
        """Adaptive mutation with varying rates based on diversity."""
        if random.random() > MUTATION_RATE:
            return genome
        
        mutated = genome[:]
        num_mutations = max(1, int(len(genome) * MUTATION_RATE))
        positions = random.sample(range(len(genome)), num_mutations)
        
        for pos in positions:
            mutated[pos] = not mutated[pos]
        return mutated

    def evolve_population(self, population):
        """Evolve population using improved genetic operators."""
        new_population = []
        
        
        sorted_population = sorted(population, key=lambda x: self.calculate_fitness(x))
        new_population.extend(sorted_population[:ELITISM_COUNT])
        
        
        while len(new_population) < POP_SIZE:
            parent1 = self.tournament_selection(population)
            parent2 = self.tournament_selection(population)
            child = self.uniform_crossover(parent1, parent2)
            child = self.adaptive_mutation(child)
            new_population.append(child)
        
        return new_population

class UI(tk.Tk):
    """UI implementation with improved genetic algorithm integration."""
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.items_list = []
        self.target = 0
        self.ga = None
        self.mainloop()

    def setup_window(self):
        """Setup window properties."""
        self.title("Knapsack Solver")
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")

    def setup_ui(self):
        """Setup UI elements."""
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        
        knapsack_menu = Menu(menu_bar)
        menu_bar.add_cascade(menu=knapsack_menu, label='Knapsack', underline=0)
        
        knapsack_menu.add_command(label="Generate", command=self.generate_knapsack, underline=0)
        knapsack_menu.add_command(label="Set Target", command=self.set_target, underline=0)
        knapsack_menu.add_command(label="Run Solver", command=self.start_solver, underline=0)

    def generate_knapsack(self):
        """Generate knapsack items."""
        self.items_list.clear()
        seen_values = set()
        
        while len(self.items_list) < NUM_ITEMS:
            item = Item()
            if item.value not in seen_values:
                self.items_list.append(item)
                seen_values.add(item.value)
        
        self.arrange_items()
        self.draw_items()

    def arrange_items(self):
        """Arrange items on canvas."""
        w = self.width - SCREEN_PADDING
        h = self.height - SCREEN_PADDING
        num_rows = math.ceil(NUM_ITEMS / 6)
        row_w = w / 8 - ITEM_PADDING
        row_h = (h - 200) / num_rows
        
        item_max = max(item.value for item in self.items_list)
        
        for x in range(6):
            for y in range(num_rows):
                idx = x * num_rows + y
                if idx >= NUM_ITEMS:
                    break
                    
                item = self.items_list[idx]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                
                item.place(
                    SCREEN_PADDING + x * row_w + x * ITEM_PADDING,
                    SCREEN_PADDING + y * row_h + y * ITEM_PADDING,
                    item_w,
                    item_h
                )

    def set_target(self):
        """Set target value for knapsack."""
        if not self.items_list:
            return
            
        target_items = random.sample(self.items_list, int(NUM_ITEMS * FRAC_TARGET))
        self.target = sum(item.value for item in target_items)
        self.draw_target()
        
        
        self.ga = GeneticAlgorithm(self.items_list, self.target)

    def start_solver(self):
        """Start solver in separate thread."""
        if not self.target or not self.items_list:
            return
            
        thread = threading.Thread(target=self.run_solver)
        thread.daemon = True
        thread.start()

    def run_solver(self):
        """Run genetic algorithm solver."""
        if not self.ga:
            return

        
        population = [self.ga.create_individual() for _ in range(POP_SIZE)]
        
        for generation in range(NUM_GENERATIONS):
            
            current_best = min(population, key=self.ga.calculate_fitness)
            current_fitness = self.ga.calculate_fitness(current_best)
            
            
            if current_fitness < self.ga.best_fitness:
                self.ga.best_solution = current_best
                self.ga.best_fitness = current_fitness
                
                
                self.update_display(current_best, current_fitness, generation)
                
                
                if current_fitness == 0:
                    break
            
            
            population = self.ga.evolve_population(population)
            
            
            self.after(int(SLEEP_TIME * 1000))

    def update_display(self, solution, fitness, generation):
        """Update UI with current solution."""
        def update():
            self.clear_canvas()
            self.draw_target()
            self.draw_solution(solution, generation)
            total_value = sum(item.value for item, selected in zip(self.items_list, solution) if selected)
            self.draw_sum(total_value)
        
        self.after(0, update)

    def clear_canvas(self):
        """Clear canvas."""
        self.canvas.delete("all")

    def draw_items(self):
        """Draw all items."""
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        """Draw target value."""
        x = (self.width - SCREEN_PADDING) / 8 * 7
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 2 - SCREEN_PADDING
        
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(
            x + w/2,
            y + h + SCREEN_PADDING,
            text=f'Target: {self.target}',
            font=('Arial', 18)
        )

    def draw_solution(self, solution, generation):
        """Draw current solution."""
        for item, selected in zip(self.items_list, solution):
            item.draw(self.canvas, selected)
            
        x = (self.width - SCREEN_PADDING) / 8 * 6
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 4 * 3
        
        self.canvas.create_text(
            x + w,
            y + h + SCREEN_PADDING*2,
            text=f'Generation {generation}',
            font=('Arial', 18)
        )

    def draw_sum(self, total):
        """Draw current solution value."""
        x = (self.width - SCREEN_PADDING) / 8 * 6
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 2 - SCREEN_PADDING
        
        ratio = total / self.target if self.target else 0
        current_h = h * ratio
        
        self.canvas.create_rectangle(x, y, x + w, y + current_h, fill='black')
        self.canvas.create_text(
            x + w/2,
            y + current_h + SCREEN_PADDING,
            text=f'{total} ({"+- "[total > self.target]}{abs(total-self.target)})',
            font=('Arial', 18)
        )

if __name__ == '__main__':
    UI()