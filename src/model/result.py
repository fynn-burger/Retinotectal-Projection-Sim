"""
Module providing Result class containing all simulation information and methods to retrieve it for representation.
"""

import numpy as np


class Result:
    """
    Encapsulates the outputs of a simulation, offering summary statistics and projection mappings for analysis and
    visualization.
    """

    def __init__(self, simulation, runtime: float, config: dict):
        """
        Initialize a Result instance.

        Args:
            simulation: Simulation object with containing all information saved during the simulation
            runtime: Elapsed computation time in seconds.
            config: Configuration used for the simulation.
        """
        self.config = config
        self.simulation = simulation
        self.runtime = runtime

    def get_mapping(self, attribute: str = "id") -> tuple[np.ndarray, np.ndarray]:
        """Generates a projection mapping representation based on a specified attribute.
        Supports 'id', or 'final_pos' for y-axis mapping.

        Args:
            attribute: determines the attribute to be mapped.

        Returns:
            x_values: Array containing final position of anterior-posterior-axis of all growth cones
            y-values:
                With attribute "id": Array containing all growth cone ids, as proxy for their nasal-temporal start-pos
                With attribute "final_pos": Array containing final position on nasal-temporal-axis of all growth cones
        """
        x_values = np.array([gc.pos[0] for gc in self.simulation.growth_cones])
        if attribute == "id":
            y_values = np.array([gc.id for gc in self.simulation.growth_cones])
        elif attribute == "final_pos":
            y_values = np.array([gc.pos[1] for gc in self.simulation.growth_cones])
        else:
            raise ValueError("Invalid attribute specified for mapping.")

        return x_values, y_values

    def get_projection_id(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Generates a projection mapping based on the ids of growth cones.
        """
        return self.get_mapping(attribute="id")

    def get_final_positioning(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Retrieves the final positions of the growth cones after the model.
        """
        return self.get_mapping(attribute="final_pos")

    def __str__(self) -> tuple[str, str]:
        """
        Returns a string representation of the projection representation.
        """
        x_values, y_values = self.get_projection_id()
        return x_values.__str__(), y_values.__str__()
