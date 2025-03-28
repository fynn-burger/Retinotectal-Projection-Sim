"""
Main module which executes simulation logic
"""
import math
import time
from model.result import Result
from model.simulation.potential_calculation import calculate_potential, calculate_ff_coef
import random


class Simulation:
    """
    Manages the simulation of growth cone dynamics within a defined substrate.

    Attributes:
        substrate (object): The environmental context in which growth cones grow.
        growth_cones (list): A collection of all active growth cone instances participating in the simulation.
        adaptation (bool): Flag to determine whether growth cones adapt.
        step_size (int): The magnitude of each movement step taken by the growth cones.
        steps_total (int): The number of steps each growth cone will attempt to complete in the simulation.
        x_step_p (float): The probability of a step generated in the positive x-direction.
        y_step_p (float): The probability of a step generated in the positive y-direction.
        sigma (float): The standard deviation parameter used in potential calculations.
        sigmoid_steepness (float): Controls the sharpness of the sigmoid function in ff_coef calculation.
        sigmoid_shift (float): Modifies the midpoint of the sigmoid function in ff_coef calculation.
        force (bool): Flag to toggle forcing growth cones to move regardless of step probabilities.
        forward_sig (bool): Flag to toggle forward signals in potential calculation.
        reverse_sig (bool): Flag to toggle reverse signals in potential aging calculation.
        ff_inter (bool): Flag to toggle fiber-fiber interactions in potential calculation.
        ft_inter (bool): Flag to toggle fiber-target interactions in potential calculation.
        mu (float): Adjusting parameter for the adaptation coefficient.
        lambda_ (float): Adjusting parameter for the resetting force.
        history_length (int): The number of historical steps to consider for adaptation.
    """

    def __init__(self, substrate, growth_cones, adaptation, step_size, num_steps, x_step_p, y_step_p, sigmoid_steepness,
                 sigmoid_shift, sigma, force, forward_sig, reverse_sig, ff_inter, ft_inter, mu, lambda_,
                 history_length):
        """
        Initialize the Simulation class with necessary parameters explained above.
        """
        self.forward_sig = forward_sig
        self.reverse_sig = reverse_sig
        self.ff_inter = ff_inter
        self.ft_inter = ft_inter
        self.substrate = substrate
        self.growth_cones = growth_cones
        self.adaptation = adaptation
        self.step_size = step_size
        self.steps_total = num_steps
        self.x_step_p = x_step_p
        self.y_step_p = y_step_p
        self.sigmoid_steepness = sigmoid_steepness
        self.sigmoid_shift = sigmoid_shift
        self.sigma = sigma
        self.force = force
        self.mu = mu
        self.lambda_ = lambda_
        self.history_length = history_length

    def run(self):
        """
        Manages the full execution of the simulation, timing the process and orchestrating the setup,
        iteration, and completion steps.
        """
        start_time = time.time()  # Start timing the model

        self.prepare_gcs()
        print(f"\nInitialization completed.")

        print(f"\nIteration starts, {self.steps_total} many steps will be taken\n")
        self.iterate_simulation()

        end_time = time.time()  # End timing the model
        total_time = end_time - start_time
        print(f"\nIteration completed in {total_time:.2f} seconds\n")

        for gc in self.growth_cones:
            print(gc)

        return Result(self.growth_cones, self.substrate)

    def prepare_gcs(self):
        """
        Initializes the potential values for each growth cone.
        """
        for gc in self.growth_cones:
            # Potential initialization
            gc.potential = calculate_potential(gc, self.growth_cones, self.substrate, 0)

    def iterate_simulation(self):
        """
        Iteratively processes each simulation step, generating random steps, and making stepping decisions.
        """
        for step_current in range(self.steps_total):
            if step_current % 250 == 0:
                print(f"Current Step: {step_current}")

            for gc in self.growth_cones:
                if self.adaptation:
                    self.adapt_growth_cone(gc)
                if not gc.freeze:
                    self.gen_random_step(gc)
                    ff_coef = calculate_ff_coef(step_current, self.steps_total, self.sigmoid_steepness,
                                                self.sigmoid_shift)
                    self.step_decision(gc, ff_coef)

    def adapt_growth_cone(self, gc):
        """
        Adapt the growth cones. Check adaptation_exploration experiment for more details on the parameters.
        """
        gc.calculate_adaptation(self.mu, self.lambda_, self.history_length)
        gc.apply_adaptation()

    def step_decision(self, gc, ff_coef):
        """
        Decides whether the growth cone should step in the new position proposal based on its guidance potential
        """
        # Calculate new potential
        new_potential = calculate_potential(gc, self.growth_cones, self.substrate, ff_coef,
                                            self.forward_sig, self.reverse_sig, self.ff_inter, self.ft_inter)

        if self.force:
            # Force gc to take the random generated step, neglecting ques from guidance potential
            gc.take_step(new_potential)
            return

        # Calculate Step realization probabilities
        old_density = probabilistic_density(gc.potential, self.sigma)
        new_density = probabilistic_density(new_potential, self.sigma)
        probability = calculate_step_probability(old_density, new_density)

        # Step Decision
        random_number = random.random()
        if random_number > probability:
            gc.take_step(new_potential)

    def gen_random_step(self, gc):
        """
        Generates a random step for the growth cone based on predefined probabilities.
        """

        # Initialization
        x_prob = self.x_step_p
        y_prob = self.y_step_p

        # Randomly step in xt and yt directions -1, 0, +1
        xt_direction = random.choices([-1, 0, 1], weights=[(1 - x_prob), (1 - x_prob), x_prob])[0]
        yt_direction = random.choices([-1, 0, 1], weights=[y_prob, (1 - y_prob), y_prob])[0]

        xt_direction *= self.step_size
        yt_direction *= self.step_size

        gc.pos_new = clamp_to_boundaries(gc.pos_current, self.substrate, gc.size, xt_direction, yt_direction)


"""
Utility functions needed for step decision
"""


def clamp_to_boundaries(position, substrate, size, xt_direction, yt_direction):
    """
    Ensures that the position of the growth cone remains within the boundaries defined by the substrate after moving.

    Parameters:
        position (tuple): Current x and y coordinates of the growth cone.
        substrate (object): Substrate defining the boundaries and structure of the model area.
        size (int): Radius of the growth cone to ensure it does not overlap the boundary.
        xt_direction (int): Horizontal movement direction and magnitude.
        yt_direction (int): Vertical movement direction and magnitude.

    Returns:
        tuple: Clamped x and y coordinates of the growth cone.
    """
    new_x = position[0] + xt_direction
    new_y = position[1] + yt_direction

    # Adjust the new position to prevent the growth cone from crossing the substrate boundaries
    new_x_clamped = max(size, min(new_x, substrate.cols - 1 - size))
    new_y_clamped = max(size, min(new_y, substrate.rows - 1 - size))

    return new_x_clamped, new_y_clamped


def probabilistic_density(potential, sigma):
    """
    Computes the value of the Gaussian probability density function at a given potential. Peaks at 0.
    """
    return math.exp(-potential ** 2 / (2 * sigma ** 2)) / (math.sqrt(2 * math.pi) * sigma)


def calculate_step_probability(old_prob, new_prob):
    """
    Determines the decision probability for a growth cone's step based on comparing new and old potentials.
    """
    if old_prob + new_prob == 0:
        probability = 0.5  # Handle the case where optimal location is arrived
    else:
        probability = old_prob / (old_prob + new_prob)
    return probability
