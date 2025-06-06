# nn.py
# rayboytim 6/5/25

import random
import math

class NN:
    def __init__(self, networkShape: list[int]):
        self.networkShape = networkShape

        # ignores first layer (aka inputs)
        self.layers = []
        for i in range(1, len(networkShape)):
            self.layers.append(NN.Layer(networkShape[i-1], networkShape[i])) # i-1 inputs, i nodes

    class Layer:
        def __init__(self, numInputs, numNodes):

            self.__numInputs = numInputs
            self.__numNodes = numNodes

            # weights array
            self.weights = []

            for _ in range(numNodes):
                row = []
                for _ in range(numInputs):
                    row.append(random.uniform(-1, 1))
                self.weights.append(row)

            # biases array
            self.biases = []

            for _ in range(numNodes):
                self.biases.append(random.uniform(-1, 1))

            # node array
            self.nodes = []

            for _ in range(numNodes):
                self.nodes.append(0.0)

        def forward(self, inputs: list[float]):
            # reset nodes
            self.nodes = []

            for _ in range(self.__numNodes):
                self.nodes.append(0.0)

            # i represents nodes
            # j represents inputs

            for i in range(self.__numNodes):

                # sum of weights times inputs
                for j in range(self.__numInputs):
                    self.nodes[i] += self.weights[i][j] * inputs[j]

                # add the bias
                self.nodes[i] += self.biases[i]

        def activation(self):
            # RELU
            for node in self.nodes:
                if node < 0:
                    node = 0
                    
        # mutate each layer based on chance and amount
        def mutate(self, amount: float, chance: float):
            for i in range(self.__numNodes):

                for j in range(self.__numInputs):

                    # mutate weights
                    if random.random() < chance:
                        self.weights[i][j] += random.uniform(-amount, amount)
                        
                # mutate biases
                if random.random() < chance:
                    self.biases[i] += random.uniform(-amount, amount)

    def brain(self, inputs: list[float]) -> list[float]:
        # first hidden layer gets directly from inputs 
        self.layers[0].forward(inputs)
        self.layers[0].activation()

        # loop through each other layer
        for i in range(1, len(self.layers)):

            # last layer has no activation function 
            if i == len(self.layers)-1:
                self.layers[i].forward(self.layers[i-1].nodes)
            # base case
            else:
                # forward function grabbing from previous layer
                self.layers[i].forward(self.layers[i-1].nodes)
                # activation function
                self.layers[i].activation()

        # returns output of last layer
        return self.layers[len(self.layers)-1].nodes
    
    def mutate(self, amount: float, chance: float):
        # mutate each layer
        for layer in self.layers:
            layer.mutate(amount, chance)