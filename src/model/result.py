"""
Module providing Result class for result representation.
"""

import numpy as np


class Result:
    def __init__(self, simulation, runtime, config):
        """
        Initializes a Result object.
        """
        self.config = config
        self.simulation = simulation
        self.runtime = runtime

    def get_gc_count(self):
        return len(self.simulation.growth_cones)

    def get_num_steps(self):
        return self.simulation.num_steps

    def get_summary(self):
        """
        Returns a summary dictionary with key simulation parameters and runtime.
        """
        return {
            "totalGrowthCones": self.get_gc_count(),
            "simulationSteps": self.get_num_steps(),
            "computationTime": f"{self.runtime:.3f}",
            "config": self.config,
        }

    def get_mapping(self, attribute="id"):
        """
        Generates a projection mapping representation based on a specified attribute.
        Supports 'id', 'start_pos', or 'final_pos' for y-axis mapping.

        :param attribute: Attribute for y-axis values ('id', 'start_pos', 'final_pos').
        """
        x_values = np.array([gc.pos[0] for gc in self.simulation.growth_cones])
        if attribute == "id":
            y_values = np.array([gc.id for gc in self.simulation.growth_cones])
        elif attribute == "start_pos":
            y_values = np.array(
                [gc.get_start_pos()[1] for gc in self.simulation.growth_cones])
        elif attribute == "final_pos":
            y_values = np.array([gc.pos[1] for gc in self.simulation.growth_cones])
        else:
            raise ValueError("Invalid attribute specified for mapping.")

        return x_values, y_values

    def get_projection_ypos(self):
        """
        Generates a projection mapping based on initial y-positions of growth cones.
        """
        return self.get_mapping(attribute="start_pos")

    def get_projection_id(self):
        """
        Generates a projection mapping based on the ids of growth cones.
        """
        return self.get_mapping(attribute="id")

    def get_projection_halved(self):
        """
        Generates a halved projection mapping based on the ids of growth cones.
        """
        return self.get_mapping(attribute="id", halved=True)

    def get_final_positioning(self):
        """
        Retrieves the final positions of the growth cones after the model.
        """
        return self.get_mapping(attribute="final_pos")

    def __str__(self):
        """
        Returns a string representation of the projection representation.
        """
        x_values, y_values = self.get_projection_id()
        return x_values.__str__(), y_values.__str__()
