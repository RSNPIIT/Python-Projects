import random
from matplotlib import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Perceptron:
    def __init__(self, total_inputs, learning_const):
        self.weights = []
        self.learning_constant = learning_const
        for i in range(total_inputs):
            self.weights.append(random.uniform(-1,1))
        print(self.weights)

    def activate(self, sum):
        if sum > 0:
            return 1
        else:
            return -1

    def feedForward(self, inputs):
        sum = 0
        for i in range(len(self.weights)):
            sum += inputs[i] * self.weights[i]
        return self.activate(sum)

    def train(self, inputs, desired):
        guess = self.feedForward(inputs)
        error = desired - guess
        for i in range(len(self.weights)):
            self.weights[i] = self.weights[i] + error * inputs[i] * self.learning_constant ##calc new weights

def f(x):
    return 0.5 * x - 1

count = 0
training = []
perceptron = Perceptron(3, 0.0001)
for i in range(2000):
    x = random.uniform(-100,100)
    y = random.uniform(-100,100)
    training.append([x,y,1]) ##1 is the learning constant

def draw():
    global count
    ax.clear()
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.plot([-100, 100], [f(-100), f(100)], color='blue')
    w = perceptron.weights
    if w[1] != 0:
        ax.plot([-100, 100], [-(w[0]*-100 + w[2]) / w[1], -(w[0]*100 + w[2]) / w[1]], color='red')
    x = training[count][0]
    y = training[count][1]
    desired = -1
    if y > f(x):
        desired = 1
    perceptron.train(inputs = training[count], desired = desired)
    count += 1
    for d in training:
        guess = perceptron.feedForward(d)
        if guess > 0:
            pass
            color = (0.5, 0.5, 0.5)
        else:
            pass
            color = (1.0, 1.0, 1.0)
        ax.add_patch(plt.Circle((d[0], d[1]), 4, facecolor=color, edgecolor='black', linewidth=1))

fig, ax = plt.subplots()
ani = FuncAnimation(fig, lambda frame: draw(), frames=len(training) - 1, interval=1, repeat=False)
plt.show()