"""
Module providing the Substrate class for substrate representation and initialization.
"""

import numpy as np
import pandas as pd

from build import config


class BaseSubstrate:
    def __init__(self, rows, cols, offset, **kwargs):
        """
        Initialize the base Substrate object with common parameters.

        :param rows: Number of rows in the substrate grid.
        :param cols: Number of columns in the substrate grid.
        :param offset: Offset value used to calculate the substrate boundaries.

        :param custom_first: Has different roles based on the substrate type
        WEDGE: small edge length ; STRIPE: - ; GAP: last column of first part

        :param custom_second: Has different roles based on the substrate type
        WEDGE: big edge length ; STRIPE: stripe width ; GAP: first column of last part
        """
        self.rows = rows + offset * 2
        self.cols = cols + offset * 2
        self.offset = offset  # is equal to gc_size

        # Set extra attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.ligands = np.zeros((self.rows, self.cols), dtype=float)
        self.receptors = np.zeros((self.rows, self.cols), dtype=float)

    def initialize_substrate(self):
        """
        Abstract method to initialize the substrate.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def __str__(self):
        """
        Return a string representation of the ligand and receptor grids in the substrate.
        """
        # Create a string representation of the substrate

        ligands_df = pd.DataFrame(self.ligands)
        receptors_df = pd.DataFrame(self.receptors)

        result = "Ligands:\n"
        result += str(ligands_df) + "\n\n"
        result += "Receptors:\n"
        result += str(receptors_df)
        return result

    def set_col_ligand_only(self, col):
        self.ligands[:, col] = np.ones(self.rows)
        self.receptors[:, col] = np.zeros(self.rows)

    def set_col_receptor_only(self, col):
        self.ligands[:, col] = np.zeros(self.rows)
        self.receptors[:, col] = np.ones(self.rows)

    def set_col_empty(self, col):
        self.ligands[:, col] = np.zeros(self.rows)
        self.receptors[:, col] = np.zeros(self.rows)

    def set_row_ligand_only(self, row):
        self.ligands[row, :] = np.ones(self.cols)
        self.receptors[row, :] = np.zeros(self.cols)

    def set_row_receptor_only(self, row):
        self.ligands[row, :] = np.zeros(self.cols)
        self.receptors[row, :] = np.ones(self.cols)

    def set_row_empty(self, row):
        self.ligands[row, :] = np.zeros(self.cols)
        self.receptors[row, :] = np.zeros(self.cols)


class ContinuousGradientSubstrate(BaseSubstrate):
    def __init__(self, rows, cols, offset, **kwargs):
        # Initialize the superclass with all given keyword arguments
        super().__init__(rows, cols, offset, **kwargs)
        self.ligand_signal_start = kwargs.get('cont_grad_l_min')
        self.ligand_signal_end = kwargs.get('cont_grad_l_max')
        self.receptor_signal_start = kwargs.get('cont_grad_r_min')
        self.receptor_signal_end = kwargs.get('cont_grad_r_max')
        self.cont_grad_r_steepness = kwargs.get('cont_grad_r_steepness')
        self.cont_grad_l_steepness = kwargs.get('cont_grad_l_steepness')

    def initialize_substrate(self):
        """
        Initialize the substrate using continuous gradients of ligand and receptor values.
        """
        # New calculation with exponentiality
        ligand_gradient = np.linspace(self.ligand_signal_start, self.ligand_signal_end,
                                      self.cols - (2 * self.offset)) ** self.cont_grad_l_steepness
        receptor_gradient = np.linspace(self.receptor_signal_end, self.receptor_signal_start,
                                        self.cols - (2 * self.offset)) ** self.cont_grad_r_steepness

        # Scale the resulting gradients to the desired range
        # Step 1: Normalize values to range [0, 1]
        receptor_gradient = ((receptor_gradient - self.receptor_signal_end ** self.cont_grad_r_steepness)
                             / (self.receptor_signal_start ** self.cont_grad_r_steepness - self.receptor_signal_end ** self.cont_grad_r_steepness))
        ligand_gradient = ((ligand_gradient - self.ligand_signal_start ** self.cont_grad_l_steepness)
                             / (self.ligand_signal_end ** self.cont_grad_l_steepness - self.ligand_signal_start ** self.cont_grad_l_steepness))

        # Step 2: Scale normalized values to users range
        receptor_gradient = self.receptor_signal_end + (self.receptor_signal_start - self.receptor_signal_end) * receptor_gradient
        ligand_gradient = self.ligand_signal_start + (self.ligand_signal_end - self.ligand_signal_start) * ligand_gradient

        # Append offset on both ends
        low_end_ligand = np.full(self.offset, self.ligand_signal_start)
        high_end_ligand = np.full(self.offset, self.ligand_signal_end)
        low_end_receptor = np.full(self.offset, self.receptor_signal_start)
        high_end_receptor = np.full(self.offset, self.receptor_signal_end)

        # concatenate offsets and gradient
        ligand_gradient = np.concatenate([low_end_ligand, ligand_gradient, high_end_ligand])
        receptor_gradient = np.concatenate([high_end_receptor, receptor_gradient, low_end_receptor])

        for row in range(self.rows):
            self.ligands[row, :] = ligand_gradient
            self.receptors[row, :] = receptor_gradient


class WedgeSubstrate(BaseSubstrate):
    def __init__(self, rows, cols, offset, **kwargs):
        # Initialize the superclass with all given keyword arguments
        super().__init__(rows, cols, offset, **kwargs)
        self.narrow_edge = kwargs.get('narrow_edge')
        self.wide_edge = kwargs.get('wide_edge')

    def initialize_substrate(self):
        """
        Initialize the substrate using wedge-shaped patterns of ligand and receptor values.
        """
        # Set for readability
        rows, cols, = self.rows, self.cols
        min_edge_length = self.narrow_edge
        max_edge_length = self.wide_edge
        receptors = np.zeros((rows, cols), dtype=float)
        ligands = np.ones((rows, cols), dtype=float)

        # Calculate the number of wedges that fit in the substrate along the x-axis
        num_wedges_x = rows // (max_edge_length + min_edge_length)

        # Slope of upper and lower triangle hypotenuse
        ratio = (cols / max_edge_length) * 2

        # TODO: @Fix Fit extra cones to bottom, test ligands and receptors separately!
        for n in range(num_wedges_x):

            # Make upper triangle
            start_row_upperhalf = n * (max_edge_length + min_edge_length) + 1  # Adjust the start_row calculation
            end_row_upperhalf = start_row_upperhalf + (max_edge_length // 2)  # Adjust the end_row calculation
            for i in range(start_row_upperhalf, end_row_upperhalf):
                fill_until = int((i - start_row_upperhalf + 1) * ratio)
                receptors[i, :fill_until] = 1.0  # Adjust the slicing to fill only up to 'fill_until'
                ligands[i, :fill_until] = 0.0

            # Make the rectangle in the middle
            if min_edge_length > 1:
                for i in range(end_row_upperhalf, end_row_upperhalf + min_edge_length - 1):
                    receptors[i, :] = 1.0
                    ligands[i, :] = 0.0
                end_row_upperhalf += min_edge_length - 1

            # Make lower triangle
            start_row_lowerhalf = end_row_upperhalf - 1
            end_row_lowerhalf = start_row_lowerhalf + (max_edge_length // 2)
            for i in range(start_row_lowerhalf, end_row_lowerhalf + 1):
                fill_until = int((end_row_lowerhalf - i + 1) * ratio)
                receptors[i, :fill_until] = 1.0  # Adjust the slicing to fill only up to 'fill_until'
                ligands[i, :fill_until] = 0.0

        self.receptors, self.ligands = receptors, ligands


class StripeSubstrate(BaseSubstrate):
    def __init__(self, rows, cols, offset, **kwargs):
        # Initialize the superclass with all given keyword arguments
        super().__init__(rows, cols, offset, **kwargs)
        self.fwd = kwargs.get('fwd')
        self.rew = kwargs.get('rew')
        self.conc = kwargs.get('conc')  # TODO: @Feature implement concentration
        self.width = kwargs.get('width')

    def initialize_substrate(self):
        for row in range(self.rows):
            if (row // self.width) % 2 == 0:
                # Even stripe: Set ligands and clear receptors
                if self.fwd:
                    self.set_row_ligand_only(row)
            else:
                # Odd stripe: Clear ligands and set receptors
                if self.rew:
                    self.set_row_receptor_only(row)


class GapSubstrate(BaseSubstrate):
    def __init__(self, rows, cols, offset, **kwargs):
        # Initialize the superclass with all given keyword arguments
        super().__init__(rows, cols, offset, **kwargs)
        self.begin = kwargs.get('begin')
        self.end = kwargs.get('end')
        self.first_block = kwargs.get('first_block')
        self.second_block = kwargs.get('second_block')

    def initialize_substrate(self):
        first_part = int(self.cols * self.begin)
        second_part = first_part + int(self.cols * self.end)

        # First third: Filled with Signals
        for col in range(first_part):
            if self.first_block == config.LIGAND:
                self.set_col_ligand_only(col)
            else:
                self.set_col_receptor_only(col)

        # Second third: Empty
        for col in range(first_part, second_part):
            self.set_col_empty(col)

        # Final third: Filled with Signals
        for col in range(second_part, self.cols):
            if self.second_block == config.LIGAND:
                self.set_col_ligand_only(col)
            else:
                self.set_col_receptor_only(col)


class GapSubstrateInverted(GapSubstrate):
    def initialize_substrate(self):
        first_part = int(self.cols * self.begin)
        second_part = first_part + int(self.cols * self.end)
        for col in range(first_part, second_part):
            self.set_col_receptor_only(col)
