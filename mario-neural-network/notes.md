

Neural network
	Neural referes to the neurons in the model
	network is in reference to their connection

	Neuron - A thing that holds a number.
	Final layer - how much the model thinks the input cooresponds with a given digit
	hidden layer - don't worry about this for now

Genetic Algorithms
	primary means for developing code systems that evolve
	
	populations of potentinal solutions to a problem 
	evlove over generations through processse that mimic natural selection in biological evolution.

	traditional genetic algorithm - through a reward system, you can arrive at a correct ouput more quickly, your answer can evolve.

	Interactive selection - the process of evolving something through user interaction

	Ecosystem simulation - traditional computer science GA. Interactive selection technique.

How they work
	Heredity
		Mechanism that allows parent creatures in one generation to pass their traits down to a child creature

	Variation
		mechanism that creates variety in the traits present.

	Selection
		Survival of the fittest. Something that determines which offspring get to pass their genetic information to offspring.

		DESIGN YOUR OWN FITNESS FUNCTION!

Steps of a genetic algorithm
	Step 1 - Population creation
		create a population. A population needs enough variety to evolve to an optimal solution. 

		Create a population of N elements, each with randomly generated DNA

		genotype - the genetic code, what gets passed down from generation to generation
			(a colors RGB value)

		phenotype - expression of that data (cat will be big, cat will be small, cat will be an effective typist)
			(the actual resulting color from the RGB value)

	Step 2 - Selection
		a function that produces a numeric score to describe the fitness of a given element of the population.

		use an elements fitness score to weigh it's odds of being selected to reproduce for the next generation

	Step 3 - Reproduction
		Pick two parents and create a child
		crossover
			for string example, use a random midpoint and take one "half" from one parent and the other "half" from another and combine to create a new string.

			could also do a coint flip approach where you grab a character from a random parent for each index of the string

		mutation
			allow each character in the phrase to have a 1 percent chance to of mutating before being born


Neural network
	interconnected web of neurons transmitting elaborate patterns of electrical signals

	things that are easy for humans, but hard for computers
		pattern recognition
		time-series predicition and anomaly detection


	Individual Neruon -
		feed-forward model
			data passes through the network in one direction

		perceptron
			one or more inputs, a processor, and a single output

		inputs
		x0 = 12, w0 = 0.5
		x1 = 4, w1 = -1

		signum function - sgn(x) - extracts the direction or positivity of a real number ( the sign of the sum )

		For every input, multiply that input by its weight.
		Sum all the weighted inputs.
		Compute the output of the perceptron by passing that sum through an activation function (the sign of the sum).

		neural networks are considered a connectionist system. It processes information through a network of nodes

		a neural network is a complex adaptive system - it can change its internal structure based on the information flowing through it


		train network

		provide perceptron with inputs for which there is a known answer
		ask the perceptron to guess an answer
		compute the error
		adjust weights according to the error
		repeat

		learning constant

		A high learning constant causes the weights to change more drastically, but also increases the risk of overshooting the optimal weights


The machine learning life cycle
	0 identify the problem
	1 collect the data
		this could like a lot of different things
	2 prepare the data
		clean the dataset
		seperate into traiing, validation and testing
	3 choose a model
	4 train the model
	5 evaluate the model
	6 tune the parameters -
		learning rate (constant),
	7 deploy the model

Classification and Regression
	Classification - involves predicting a label


Activation functions
	with linear activation functions, you can only approximate using linear funtions. 

	sigmoid function - creates a gradual range of values between 0 and 1. More preferrable to show the neural network how 'close" it was to being a 0 or a 1

	ReLU(x) - If x < 0, 0 if x > 0, x. Faster than sigmoid. It simply "works" accordings to bro