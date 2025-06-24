"""
Module providing GrowthCone and History classes for representing growth cone dynamics and their time histories.

Classes:
- GrowthCone: Models a single growth cone's state, movement, adaptation, and sensor dynamics.
- History: Records past values of key growth cone attributes for adaptation calculations.
"""
import math


class GrowthCone:
    """
    Represents a growth cone in the simulation environment.

    Attributes:
        pos: Current (x, y) center position of the growth cone.
        radius: Radius of the circular growth cone (+1 for FT-Interaction).
        id: Unique identifier for the growth cone.
        receptor: Base receptor level (possibly adjusted by knock-in).
        ligand: Base ligand level (possibly adjusted by knock-in).
        outer_receptor_current: Current outer receptor sensor value (scaled by rho).
        outer_ligand_current: Current outer ligand sensor value (scaled by rho).
        inner_receptor_current: Current inner receptor sensor value (scaled by rho).
        inner_ligand_current: Current inner ligand sensor value (scaled by rho).
        potential: Latest computed potential value for this cone.
        adap_co: Current adaptation coefficient.
        reset_force: Current resetting force for rho.
        rho_current: Current receptor fraction used to split outer/inner sensors.
        history: Time history of potentials, positions, sensors, and rho.
        freeze: Whether the growth cone is frozen.
    """
    def __init__(self, position: tuple[int, int], size: int, ligand: float, receptor: float, id: int, rho: float,
                 knock_in: float, freeze: bool = False):
        self.pos = position
        self.radius = size
        self.id = id
        self.receptor = self.set_receptor(receptor, knock_in)
        self.ligand = ligand
        # self.ligand = self.set_ligand(ligand, knock_in)
        self.outer_ligand_current = self.ligand * rho
        self.outer_receptor_current = self.receptor * rho
        self.inner_ligand_current = self.ligand * (1 - rho)
        self.inner_receptor_current = self.receptor * (1 - rho)

        self.potential = 0
        self.adap_co = 1  # Adaptation coefficient starts at 1

        self.reset_force = 0
        self.rho_current = rho
        self.freeze = freeze  # needed for polarity reversal

        self.history = History(self.potential, self.adap_co, self.pos,
                               self.outer_ligand_current, self.outer_receptor_current,
                               self.inner_ligand_current, self.inner_receptor_current,
                               self.rho_current, self.reset_force)

    def __str__(self):
        """
        Provides a string representation of the growth cone's attributes.
        """
        return (f"Receptor: {self.receptor}, Ligand: {self.ligand}, rho: {self.rho_current}, "
                f"Outer_L: {self.outer_ligand_current}, Outer_R: {self.outer_receptor_current}, "
                f"Inner_L: {self.inner_ligand_current}, Inner_R: {self.inner_receptor_current}, "
                f"Position: {self.pos}, "f"Start Position: {self.get_start_pos()}, Potential: {self.potential}, "
                f"ID: {self.id}, Adaptation Coefficient: {self.adap_co}, "
                f"Reset Force: {self.reset_force}")

    def set_receptor(self, receptor: float, knock_in: float) -> float:
        """
        Apply knock-in modification to the receptor level for even-indexed cones.

        Args:
            receptor (float): Base receptor value.
            knock_in (float): Knock-in increment.

        Returns:
            float: Modified receptor value.
        """
        if self.id % 2 == 0 and knock_in != 0:
            return receptor + knock_in
        return receptor

    def set_ligand(self, ligand: float, knock_in: float) -> float:
        """
        (Optional) Apply knock-in modification to ligand level.

        Args:
            ligand (float): Base ligand value.
            knock_in (float): Knock-in parameter.

        Returns:
            float: Modified ligand value.
        """
        if self.id % 2 == 0 and knock_in != 0:
            return 1.0 / self.receptor
        return ligand

    def take_step(self, pos_new, potential_new):
        """
        Move the cone to a new position and update its potential.

        Args:
            pos_new (tuple): Proposed new (x, y) position.
            potential_new (float): Computed potential at the new position.
        """
        self.history.update_potential(potential_new)
        self.history.update_position(pos_new)
        self.potential = potential_new
        self.pos = pos_new

    def calculate_adaptation(self, mu, lambda_, h):
        """
        Update adaptation coefficient and resetting force based on history.

        Args:
            mu (float): Adaptation rate parameter.
            lambda_ (float): Resetting force parameter.
            h (int): Number of steps from history to consider.
        """
        # Ensure we have enough history to calculate adaptation
        if len(self.history.potential) >= h:
            recent_history = self.history.potential[-h:]  # Get the last h elements from the history

            # New adaptation formula
            adap_co_temp = math.exp(
                           - mu * sum(k * abs(potential_diff) for k, potential_diff in enumerate(recent_history, 1)) /
                           sum(range(1, h + 1)))

            self.adap_co = float("{:.6f}".format(adap_co_temp))

            # Calculate resetting force depending on rho
            self.reset_force = lambda_ * (1 - self.rho_current)

        self.history.update_adap_co(self.adap_co)
        self.history.update_reset_force(self.reset_force)

    def apply_adaptation(self):
        """
        Apply the adaptation coefficient and resetting force to the ligand and receptor values and update history of the
        growth cone.
        """

        # calculate rho
        rho_temp = self.rho_current * self.adap_co
        rho_temp = max(0.0, rho_temp + self.reset_force)

        # apply new rho to current and history
        self.rho_current = float("{:.6f}".format(rho_temp))
        self.history.update_rho(self.rho_current)

        # calculate inner and outer sensors based on rho
        outer_ligand_temp = self.ligand * self.rho_current
        outer_receptor_temp = self.receptor * self.rho_current
        inner_ligand_temp = self.ligand * (1 - self.rho_current)
        inner_receptor_temp = self.receptor * (1 - self.rho_current)

        # apply new sensor values to current and history
        self.outer_ligand_current = float("{:.6f}".format(outer_ligand_temp))
        self.outer_receptor_current = float("{:.6f}".format(outer_receptor_temp))
        self.inner_ligand_current = float("{:.6f}".format(inner_ligand_temp))
        self.inner_receptor_current = float("{:.6f}".format(inner_receptor_temp))

        # update history
        self.history.update_outer_ligand(self.outer_ligand_current)
        self.history.update_outer_receptor(self.outer_receptor_current)
        self.history.update_inner_ligand(self.inner_ligand_current)
        self.history.update_inner_receptor(self.inner_receptor_current)

    def get_start_pos(self):
        return self.history.position[0]


class History:
    """
    Records time history of a GrowthCone's key state variables.

    Attributes:
        potential: List of past potential values.
        adap_co: List of past adaptation coefficients.
        position: List of past positions.
        outer_ligand: List of past outer ligand values.
        outer_receptor: List of past outer receptor values.
        inner_ligand: List of past inner ligand values.
        inner_receptor: List of past inner receptor values.
        rho: List of past rho values.
        reset_force: List of past resetting forces.
    """
    def __init__(self, potential_ini: float, adap_co_ini: float, position_ini: tuple[float, float],
                 outer_ligand_ini: float, outer_receptor_ini: float, inner_ligand_ini: float, inner_receptor_ini: float,
                 rho_ini: float, reset_force_ini: float):
        self.potential = [potential_ini]
        self.adap_co = [adap_co_ini]
        self.position = [position_ini]
        self.outer_ligand = [outer_ligand_ini]
        self.outer_receptor = [outer_receptor_ini]
        self.inner_ligand = [inner_ligand_ini]
        self.inner_receptor = [inner_receptor_ini]
        self.rho = [rho_ini]
        self.reset_force = [reset_force_ini]

    def update_potential(self, potential_new):
        self.potential.append(potential_new)

    def update_adap_co(self, adap_co_new):
        self.adap_co.append(adap_co_new)

    def update_position(self, adap_position_new):
        self.position.append(adap_position_new)

    def update_outer_ligand(self, outer_ligand_new):
        self.outer_ligand.append(outer_ligand_new)

    def update_outer_receptor(self, outer_receptor_new):
        self.outer_receptor.append(outer_receptor_new)

    def update_inner_ligand(self, inner_ligand_new):
        self.inner_ligand.append(inner_ligand_new)

    def update_inner_receptor(self, inner_receptor_new):
        self.inner_receptor.append(inner_receptor_new)

    def update_rho(self, rho_new):
        self.rho.append(rho_new)

    def update_reset_force(self, reset_force_new):
        self.reset_force.append(reset_force_new)
