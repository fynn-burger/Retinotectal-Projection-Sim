"""
Module providing Growth Cone class for growth cone representation.
"""
import math


class GrowthCone:
    """
    Represents a growth cone in the model environment.

    Attributes:
        pos_start (tuple): Initial position of the growth cone.
        pos (tuple): Center point of the circular modeled growth cone (x, y coordinates).
        pos_new (tuple): New position proposal (used for step decision).
        radius (int): Radius of the growth cone.
        ligand_current (float): Ligand value of growth cone.
        receptor_current (float): Receptor value of growth cone.
        potential (float): Current potential of the growth cone.
    """

    def __init__(self, position, radius, ligand, receptor, id, rho, gauss_kernel, freeze=False, marked=False):
        self.pos = position
        '''
        self.ligand_current = ligand
        self.receptor_current = receptor
        '''
        self.ligand = ligand
        self.receptor = receptor
        self.outer_ligand_current = self.ligand * rho
        self.outer_receptor_current = self.receptor * rho
        self.inner_ligand_current = self.ligand * (1 - rho)
        self.inner_receptor_current = self.receptor * (1 - rho)
        self.radius = radius
        self.gauss_kernel = gauss_kernel

        self.potential = 0
        self.adap_co = 1  # Adaptation coefficient starts at 1
        # Apply resetting force only to rho not to ligand and receptor
        '''
        self.reset_force_receptor = 0  # Resetting forces start at 0
        self.reset_force_ligand = 0
        '''
        self.reset_force = 0
        self.id = id
        self.rho_current = rho
        self.freeze = freeze  # needed for polarity reversal
        self.marked = marked  # needed to visualize two sets of GCs like in knock-in

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

    def take_step(self, pos_new, potential_new):
        """
        Actualize growth cone by moving it to its new position
        """
        self.history.update_potential(potential_new)
        self.history.update_position(pos_new)
        self.potential = potential_new
        self.pos = pos_new

    def calculate_adaptation(self, mu, lambda_, h):
        """
        Calculate the adaptation coefficient and the resetting force based on the history.

        :param mu: Adjusting parameter for the adaptation coefficient.
        :param lambda_: Adjusting parameter for the resetting force.
        :param h: The number of historical steps to consider for adaptation.
        """
        # Ensure we have enough history to calculate adaptation
        if len(self.history.potential) >= h:
            recent_history = self.history.potential[-h:]  # Get the last h elements from the history

            # Calculate the adaptation coefficient using the formula from the paper

            adap_co_temp = 1 - math.log(
                1 + mu * sum(k * abs(potential_diff) for k, potential_diff in enumerate(recent_history, 1)) / sum(
                    range(1, h + 1)))
            '''

            # new formula for adaptation
            adap_co_temp = math.exp(
                           - mu * sum(k * abs(potential_diff) for k, potential_diff in enumerate(recent_history, 1)) /
                           sum(range(1, h + 1)))
            '''

            self.adap_co = float("{:.6f}".format(adap_co_temp))


            # Calculate the resetting force
            '''
            self.reset_force_receptor = lambda_ * (self.get_start_receptor() - self.receptor_current)
            self.reset_force_ligand = lambda_ * (self.get_start_ligand() - self.ligand_current)
            '''

            # Calculate resetting force depending on rho
            self.reset_force = lambda_ * (1 - self.rho_current)

        self.history.update_adap_co(self.adap_co)

        '''
        self.history.update_reset_force_receptor(self.reset_force_receptor)
        self.history.update_reset_force_ligand(self.reset_force_ligand)
        '''

        self.history.update_reset_force(self.reset_force)

    def apply_adaptation(self):
        """
        Apply the adaptation coefficient and resetting force to the ligand and receptor values.
        """

        '''
        ligand_temp = self.ligand_current * self.adap_co
        receptor_temp = self.receptor_current * self.adap_co
        ligand_temp = max(0, ligand_temp + self.reset_force_ligand)
        receptor_temp = max(0, receptor_temp + self.reset_force_receptor)

        self.ligand_current = float("{:.6f}".format(ligand_temp))
        self.receptor_current = float("{:.6f}".format(receptor_temp))

        self.history.update_ligand(self.ligand_current)
        self.history.update_receptor(self.receptor_current)
        '''

        # calculate rho
        rho_temp = self.rho_current * self.adap_co
        rho_temp = max(0, rho_temp + self.reset_force)

        # apply new rho to current and history
        self.rho_current = float("{:.6f}".format(rho_temp))
        self.history.update_rho(self.rho_current)

        # eventuell die nächsten 10 Zeilen in eine Funktion
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

        # Das eventuell in eine Funktion
        # update history
        self.history.update_outer_ligand(self.outer_ligand_current)
        self.history.update_outer_receptor(self.outer_receptor_current)
        self.history.update_inner_ligand(self.inner_ligand_current)
        self.history.update_inner_receptor(self.inner_receptor_current)



    ''' -> see later how to implement with new adaptation
    def mutate(self, knock_in):
        """
        Mutate the growth cones. Used for knock-in experiment.
        """
        self.receptor_current += knock_in
        self.ligand_current = 0.35 / self.receptor_current 
    '''

    def get_start_pos(self):
        return self.history.position[0]

    '''
    def get_start_ligand(self):
        return self.history.ligand[0]

    def get_start_receptor(self):
        return self.history.receptor[0]
    '''


class History:
    """
    Represents a history of the Growth Cone object by storing all the past data
    """
    def __init__(self, potential_ini, adap_co_ini, position_ini, outer_ligand_ini, outer_receptor_ini,
                 inner_ligand_ini, inner_receptor_ini, rho_ini, reset_force_ini):
        self.potential = [potential_ini]
        self.adap_co = [adap_co_ini]
        self.position = [position_ini]
        self.outer_ligand = [outer_ligand_ini]
        self.outer_receptor = [outer_receptor_ini]
        self.inner_ligand = [inner_ligand_ini]
        self.inner_receptor = [inner_receptor_ini]
        self.rho = [rho_ini]
        '''
        self.reset_force_receptor = [reset_force_receptor_ini]
        self.reset_force_ligand = [reset_force_ligand_ini]
        '''
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
    '''
    def update_reset_force_receptor(self, reset_force_receptor_new):
        self.reset_force_receptor.append(reset_force_receptor_new)

    def update_reset_force_ligand(self, reset_force_ligand_new):
        self.reset_force_ligand.append(reset_force_ligand_new)
    '''

    def update_rho(self, rho_new):
        self.rho.append(rho_new)

    def update_reset_force(self, reset_force_new):
        self.reset_force.append(reset_force_new)
