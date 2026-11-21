from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
import numpy as np
import cv2
import random
from math import *
import time
from gym_mario import *
import multiprocessing
import copy

class Element:
    def __init__(self, number_of_inputs, number_of_neurons):
        self.game = Game()
        self.obstacle_grid = None
        self.input = 0 ##initial input is nothing, after each step we will start generating inputs

        ## Create weights and biases for neurnal net
        self.weights = (0.10 * np.random.randn(number_of_inputs, 18))
        self.biases = np.zeros((1,18))

        # print(len(self.weights))

        self.hidden_layer_weights = (0.10 * np.random.randn(18, number_of_neurons)) ##hidden layer of 18 neurons
        self.output_biases = np.zeros((1, number_of_neurons))
        
        # print(len(self.hidden_layer_weights))

        self.fitness = 0

    def forward(self,inputs, weights, biases):
        self.output = np.dot(inputs, weights) + biases

    def activation_ReLU(self, inputs):
        self.output =  np.maximum(0, inputs) ## we don't want any values that are negative, return the values as 0 if negative.
    
    def generate_game_input(self):
        self.input = np.argmax(self.output) ##look at the index position of the highest number
        # print(grid)

    def measure_fitness(self):
        # print(self.game.info)
        self.fitness += self.game.reward

    def breed(self, partner):
        child = Element(208,12)

        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                if random.choice([0, 1]):
                    child.weights[i][j] = partner.weights[i][j]
                else:
                    child.weights[i][j] = self.weights[i][j]

        for i in range(len(self.biases)):
            for j in range(len(self.biases[i])):
                if random.choice([0, 1]):
                    child.biases[i][j] = partner.biases[i][j]
                else:
                    child.biases[i][j] = self.biases[i][j]

        for i in range(len(self.hidden_layer_weights)):
            for j in range(len(self.hidden_layer_weights[i])):
                if random.choice([0, 1]):
                    child.hidden_layer_weights[i][j] = partner.hidden_layer_weights[i][j]
                else:
                    child.hidden_layer_weights[i][j] = self.hidden_layer_weights[i][j]

        for i in range(len(self.output_biases)):
            for j in range(len(self.output_biases[i])):
                if random.choice([0, 1]):
                    child.output_biases[i][j] = partner.output_biases[i][j]
                else:
                    child.output_biases[i][j] = self.output_biases[i][j]
        
        return child
            
    

    # def terminate_if_dumb(self):
    #     if self.fitness < 0:
    #         self.game.done = True

def create_population(n):
    elements = []
    for _ in range(n):
        elements.append(Element(208, 12)) ##mario grid is len 208 ## 18 NEURONS for first hidden layer
    return elements

def clone_network(e):
    child = Element(208,12)
    child.weights = e.weights.copy()
    child.biases = e.biases.copy()
    child.hidden_layer_weights = e.hidden_layer_weights.copy()
    child.output_biases = e.output_biases.copy()
    return child

def generate_mating_pool():
    mating_pool = []
    for e in elements:
        n = floor(e.fitness / 10)
        for _ in range(n):
            mating_pool.append(e)

    print(len(mating_pool))
    return mating_pool

def breed_new_pop(n, mating_pool, population):
    n_of_elites = int(n / 15)

    elites = sorted(population, key = lambda e: e.fitness, reverse = True)[:n_of_elites]
    new_population = [clone_network(e) for e in elites]

    for _ in range(n - n_of_elites):
        parent_a = random.choice(mating_pool)
        parent_b = random.choice(mating_pool)
        child = parent_a.breed(parent_b)
        new_population.append(child)
    
    return new_population, n_of_elites

def mutate_population(population, n_of_elites):
    for e in population[n_of_elites:]:
        for i in range(len(e.weights)):
            for j in range(len(e.weights[i])):
                if random.random() < 0.1:
                    e.weights[i][j] += random.uniform(-0.08, 0.08)

        for i in range(len(e.biases)):
            for j in range(len(e.biases[i])):
                if random.random() < 0.1:
                    e.biases[i][j] += random.uniform(-0.08, 0.08)

        for i in range(len(e.hidden_layer_weights)):
            for j in range(len(e.hidden_layer_weights[i])):
                if random.random() < 0.1:
                    e.hidden_layer_weights[i][j] += random.uniform(-0.05, 0.05)

        for i in range(len(e.output_biases)):
            for j in range(len(e.output_biases[i])):
                if random.random() < 0.1:
                    e.output_biases[i][j] += random.uniform(-0.05, 0.05)
    
def train(elements, show_all_games, steps, gen_count):
    cols = math.ceil(math.sqrt(len(elements)))
    for step in range(steps):
        obst_grids, frames = step_games_and_return_obstacles(elements, show_all_games)

        for i, e in enumerate(elements): ## FEED obstacle grdis to neural networks. Generate outputs.
            e.obstacle_grid = obst_grids[i].flatten()
            e.forward(e.obstacle_grid, e.weights, e.biases)
            e.activation_ReLU(e.output)
            e.forward(e.output, e.hidden_layer_weights, e.output_biases)
            # print(e.output)
            e.generate_game_input()
            e.measure_fitness()
        
        if show_all_games: #and step % 10 == 0:
            leader_idx = max(range(len(elements)), key=lambda k: elements[k].fitness)
            render_with_feature(frames, cols, frames[leader_idx], fitness_history, gen_count)

    close_games(elements,show_all_games)

def draw_fitness_graph(history, w, h):
    graph = np.full((h, w, 3), 30, dtype=np.uint8)
    cv2.putText(graph, "best fitness:",(15,28),cv2.FONT_HERSHEY_SIMPLEX, 1, (200,200,200),1,cv2.LINE_AA)
    if len(history) < 2:
        return graph
    low, high = min(history), max(history)
    span = (high - low) or 1
    pad = 40
    pts = []
    for i, f in enumerate(history):
        x = pad + int(i / (len(history) - 1) * (w - 2 * pad))
        y = (h - pad) - int((f - low) / span * (h - 2 * pad))
        pts.append((x, y))
    for a,b in zip(pts, pts[1:]):
        cv2.line(graph, a, b, (0,255,0), 2, cv2.LINE_AA)
    for p in pts:
        cv2.circle(graph,p,3,(0,255,0), -1)
    cv2.putText(graph,f"latest: {int(history[-1])}", (15,h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1, cv2.LINE_AA)
    return graph

def render_with_feature(frames, cols, featured_frame, fitness_history, gen_count):
    grid = tile(frames, cols=cols)
    gh, gw, _ = grid.shape

    panel_h = gh // 2
    panel_w = int(panel_h * (256 / 240))

    featured = cv2.resize(featured_frame, (panel_w, panel_h), interpolation=cv2.INTER_NEAREST)
    graph = draw_fitness_graph(fitness_history, panel_w, panel_h)

    right_col = np.vstack([featured, graph])
    if right_col.shape[0] != gh:
        right_col = cv2.resize(right_col, (panel_w, gh))
    screen = np.hstack([grid, right_col])
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.putText(screen, f"GEN {gen_count}", (10, gh - 15), cv2.FONT_HERSHEY_SIMPLEX, 10, (0, 0, 0),20, cv2.LINE_AA)
    cv2.imshow('Like and Subscribe', screen)
    cv2.waitKey(1)

def save_best(elements):
    best = max(elements, key=lambda e: e.fitness)
    np.savez("best_neural_network", weights=best.weights, biases = best.biases, hidden_layer_weights = best.hidden_layer_weights, output_biases = best.output_biases, fitness = best.fitness)
    print("saved best fitness")

def save_population(elements):
    np.savez("last_population",
             weights=np.array([e.weights for e in elements]),
             biases=np.array([e.biases for e in elements]),
             hidden_layer_weights=np.array([e.hidden_layer_weights for e in elements]),
             output_biases=np.array([e.output_biases for e in elements]),
             fitness=np.array([e.fitness for e in elements]))
    print("saved last population")

def load_population(path="last_population.npz"):
    data = np.load(path)
    weights = data["weights"]
    biases = data["biases"]
    hidden_layer_weights = data["hidden_layer_weights"]
    output_biases = data["output_biases"]

    elements = []
    for i in range(len(weights)):
        e = Element(208, 12)
        e.weights = weights[i]
        e.biases = biases[i]
        e.hidden_layer_weights = hidden_layer_weights[i]
        e.output_biases = output_biases[i]
        e.fitness = 0
        elements.append(e)
    return elements

def load_top_from_population(path="last_population.npz"):
    data = np.load(path)
    fitness = data["fitness"]
    idx = int(np.argmax(fitness))

    e = Element(208,12)
    e.weights = data["weights"][idx]
    e.biases = data["biases"][idx]
    e.hidden_layer_weights = data["hidden_layer_weights"][idx]
    e.output_biases = data["output_biases"][idx]
    e.fitness = 0
    return

steps = 2000
# n = 100
gen_count = 0
fitness_history = []
best_fitness = []
rolling_avg_fitness = []
# elements = create_population(n)
# elements = [load_top_from_population()]
elements = load_population()
start_time = time.time()
duration = 24 * 60 * 60

while time.time() - start_time < duration:
    train(elements=elements,show_all_games=True,steps=steps, gen_count=gen_count)
    best = max(e.fitness for e in elements)
    fitness_history.append(best)
    print(f"gen: {gen_count} | best fitness: {best}")
    mating_pool = generate_mating_pool()
    elements, n_of_elites = breed_new_pop(n, mating_pool, elements)
    mutate_population(elements, n_of_elites)
    gen_count += 1

    if gen_count % 10 == 0:
        save_best(elements)
        save_population(elements)