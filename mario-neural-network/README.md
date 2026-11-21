# mario-neural-network

The code from my video where I try to make an AI from scratch. A neural network, trained by a genetic algorithm, learns to play Super Mario Bros.

## What's here

- `mario_nn/` — the actual Mario AI
  - `main.py` — the neural network, breeding/crossover/mutation, and the training loop
  - `gym_mario.py` — emulator wrapper; reads the NES RAM and builds the 16×13 tile grid the network sees
- Everything else is the practice exercises I did while learning:
  - `simple_perceptron.py` — a single perceptron by hand
  - `perceptrons.py` — perceptron that learns to classify points above/below a line
  - `neural_network.py` — first layers + ReLU with numpy
  - `string_evolution.py` — genetic algorithm evolving a target string
  - `rockets.py` — smart rockets evolving toward a target
  - `notes.md` — notes I took while learning

## Running the Mario AI

```
pip install numpy opencv-python gym-super-mario-bros nes-py
python mario_nn/main.py
```

`main.py` currently resumes from a saved population (`last_population.npz`, not included). To train from scratch, swap `elements = load_population()` for the commented-out `n = 100` / `elements = create_population(n)` lines.

The exercises additionally use `matplotlib`, `nnfs`, and `pygame`.
