import math
import pygame
from numpy import array
from numpy import linalg
from numpy import random

target = array([320.0, 60.0])

class DNA:
    def __init__(self, length): 
        self.genes = []
        self.maxForce = 0.1
        for i in range(length):
            self.genes.append(
                random.uniform(-self.maxForce, self.maxForce, 2)
            )

    def crossover(self, partner):
        child = DNA(len(self.genes))
        midpoint = random.randint(len(self.genes))
        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]
        return child

    def mutate(self, mutationRate):
        for i in range(len(self.genes)):
            if random.random() < mutationRate:
                self.genes[i] = random.uniform(-self.maxForce, self.maxForce, 2)


class Rocket:
    def __init__(self, x, y, dna):
        self.dna = dna
        self.fitness = 0
        self.geneCounter = 0
        self.position = array([x, y], dtype=float)
        self.velocity = array([0.0, 0.0])
        self.acceleration = array([0.0, 0.0])

    def applyForce(self, force):
        self.acceleration += force

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

    def calculateFitness(self):
        distance = linalg.norm(self.position - target)
        self.fitness = 1 / (distance * distance)

    def run(self):
        self.applyForce(self.dna.genes[self.geneCounter])
        self.geneCounter += 1
        self.update()


class Population:
    def __init__(self, mutation, populationSize, lifespan):
        self.mutationRate = mutation
        self.population = []
        self.generations = 0
        for i in range(populationSize):
            self.population.append(Rocket(320, 220, DNA(lifespan)))

    def fitness(self):
        for rocket in self.population:
            rocket.calculateFitness()

    def selection(self):
        total_fitness = 0
        for rocket in self.population:
            total_fitness += rocket.fitness
        for rocket in self.population:
            rocket.fitness /= total_fitness

    def weightedSelection(self):
        index = 0
        start = random.random()
        while start > 0 and index < len(self.population):
            start = start - self.population[index].fitness
            index += 1
        index -= 1
        return self.population[index]

    def reproduction(self):
        new_population = []
        for i in range(len(self.population)):
            parentA = self.weightedSelection()
            parentB = self.weightedSelection()
            child = parentA.dna.crossover(parentB.dna)
            child.mutate(self.mutationRate)
            new_population.append(Rocket(320, 240, child))
        self.population = new_population

    def live(self):
        for rocket in self.population:
            rocket.run()


# --- pygame stuff----

WIDTH, HEIGHT = 640, 480
NAVY = (9, 12, 29)
RED = (251, 92, 92)
LIGHT = (230, 230, 235)


def draw_rocket(surface, rocket, size=7):
    vx, vy = rocket.velocity
    angle = math.atan2(vy, vx) if (vx or vy) else -math.pi / 2
    pts = [(size, 0), (-size * 0.6, size * 0.6), (-size * 0.6, -size * 0.6)]
    ca, sa = math.cos(angle), math.sin(angle)
    px, py = float(rocket.position[0]), float(rocket.position[1])
    poly = [(px + x * ca - y * sa, py + x * sa + y * ca) for x, y in pts]
    pygame.draw.polygon(surface, RED, poly)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Like and Subscribe")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

lifespan = 200
population = Population(0.01, 100, lifespan)
frame = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target = array([float(event.pos[0]), float(event.pos[1])])

    if frame < lifespan:
        population.live()
        frame += 1
    else:
        population.fitness()
        population.selection()
        population.reproduction()
        population.generations += 1
        frame = 0

    screen.fill(NAVY)
    pygame.draw.circle(screen, LIGHT, (int(target[0]), int(target[1])), 10, 2)
    for rocket in population.population:
        draw_rocket(screen, rocket)
    screen.blit(font.render(f"Generation {population.generations}", True, LIGHT), (10, 10))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()