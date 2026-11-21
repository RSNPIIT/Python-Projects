inputs = [12,4]
weights = [0.5, -1]

sum = 0
for i in range(len(inputs)):
	sum += inputs[i] * weights[i]

def activate(sum):
	if sum > 0:
		return 1
	else:
		return 0

print(activate(sum))
	