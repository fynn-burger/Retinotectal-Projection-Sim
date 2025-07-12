"""
Guidance-Potential Module

Provides functions to compute the guidance potential for a growth cone based on
fiber-target, fiber-fiber, and cis interactions, as well as helper routines for
calculating interaction signals and geometric helpers.

This module provides the following functions:
- calculate_potential: Compute the net potential difference for a single cone.
- calculate_ft_interaction: Compute fiber-target interaction signals.
- calculate_ff_interaction: Compute fiber-fiber interaction signals.
- calculate_cis_interaction: Compute cis interaction signal.
- helper functions for calculating interaction signals and geometric helpers.
"""

import math
import numpy as np


def calculate_potential(gc, pos: tuple[int, int], substrate, forward_on: bool, reverse_on: bool,
                        ff_inter_on: bool, ft_inter_on: bool, cis_inter_on: bool, step: int, num_steps: int,
                        sigmoid_steepness: float, sigmoid_shift: float, sigmoid_height: int,
                        cis_in_fac: float, cis_out_fac: float, all_gc_lig: np.ndarray, all_gc_rec: np.ndarray,
                        mask: np.ndarray) -> float:
    """
    Compute the guidance potential for a single growth cone.

    This calculates forward and reverse contributions from fiber-target, fiber-fiber,
    and cis interactions and returns the log-ratio of reverse to forward signals.

    Args:
        gc: GrowthCone instance.
        pos: Position to check potential for.
        substrate: Substrate instance with ligand/receptor grids.
        forward_on: Enable forward signal.
        reverse_on: Enable reverse signal.
        ff_inter_on: Enable fiber-fiber interactions.
        ft_inter_on: Enable fiber-target interactions.
        cis_inter_on: Enable cis interactions.
        step: Current simulation step index.
        num_steps: Total number of simulation steps.
        sigmoid_steepness: Steepness for ff-coefficient.
        sigmoid_shift: Shift for ff-coefficient.
        sigmoid_height: Maximum height for ff-coefficient.
        cis_in_fac: Scaling for inner cis interactions.
        cis_out_fac: Scaling for outer cis interactions.
        all_gc_lig: Pre-folded ligand values of all growth cones over substrate ()
        all_gc_rec: Pre-folded receptor values of all growth cones over substrate
        mask: Array of boolean values to mask gcs

    Returns:
        float: Potential of gc at position pos.
    """

    # get outer sensor patches
    gc_lig_patch, gc_rec_patch = get_outer_patches(gc, pos, substrate, mask)

    # Calculate interactions based on toggles
    # Calculate trans-interaction
    trans_sig_fwd, trans_sig_rev = calculate_ft_interaction(substrate, gc_lig_patch, gc_rec_patch)\
        if ft_inter_on else (0, 0)

    # Calculate fiber-fiber-interaction
    ff_sig_fwd, ff_sig_rev = calculate_ff_interaction(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height,
                                                      all_gc_lig, all_gc_rec, gc_lig_patch, gc_rec_patch) \
        if ff_inter_on else (0, 0)

    # Calculate cis-interaction
    cis_sig_fwd = cis_sig_rev = calculate_cis_interaction(cis_in_fac, cis_out_fac, gc_lig_patch, gc_rec_patch, gc,
                                                          mask) if cis_inter_on else 0

    # Calculate forward and reverse signals based on flags
    forward_sig = trans_sig_fwd + ff_sig_fwd + cis_sig_fwd if forward_on else 0
    reverse_sig = trans_sig_rev + ff_sig_rev + cis_sig_rev if reverse_on else 0

    # Use non-zero values for forward and reverse sig and format value
    forward_sig = max(float("{:.6f}".format(forward_sig)), 0.0001)
    reverse_sig = max(float("{:.6f}".format(reverse_sig)), 0.0001)

    # Calculate and return the potential
    return abs(math.log(reverse_sig) - math.log(forward_sig))


def calculate_ft_interaction(substrate, gc_lig_patch: np.ndarray, gc_rec_patch: np.ndarray) -> tuple[float, float]:
    """ Compute fiber-target interaction by multiplying gc-receptors with substrate-ligands and vice versa.

    Args:
        substrate: Substrate instance holding the sensor values
        gc_lig_patch: Array of gc-ligand-values for every coordinate
        gc_rec_patch: Array of gc-receptor-values for every coordinate

    Returns:
        float: Fiber-target interaction signal of gc at position pos (forward, reverse).
    """
    trans_sig_fwd = (gc_rec_patch * substrate.ligands).sum()
    trans_sig_rev = (gc_lig_patch * substrate.receptors).sum()
    return trans_sig_fwd, trans_sig_rev


def calculate_ff_interaction(step: int, num_steps: int, sigmoid_steepness: float, sigmoid_shift: float,
                             sigmoid_height: int, all_gc_lig: np.ndarray, all_gc_rec: np.ndarray,
                             gc_lig_patch: np.ndarray, gc_rec_patch: np.ndarray) -> tuple[float, float]:
    """Compute fiber-fiber interaction by multiplying gc-receptors with overlapping receptors of other gcs
    and vice versa, dependent on the ff-coefficient.

    Args:
        step: Current iteration step.
        num_steps: Total number of simulation steps.
        sigmoid_steepness: Steepness for ff-coefficient.
        sigmoid_shift: Shift for ff-coefficient.
        sigmoid_height: Maximum height for ff-coefficient.
        all_gc_lig: Array of all gc-ligand-values for every coordinate
        all_gc_rec: Array of all gc-receptor-values for every coordinate
        gc_lig_patch: Array of gc-ligand-values for current gc for every coordinate
        gc_rec_patch: Array of gc-receptor-values for current gc for every coordinate

    Returns:
        ff_sig_fwd: ff forward signal
        ff_sig_rev: ff reverse signal
    """
    ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
    other_lig_patch = all_gc_lig - gc_lig_patch
    other_rec_patch = all_gc_rec - gc_rec_patch
    ff_sig_fwd = (other_lig_patch * gc_rec_patch * ff_coef).sum()
    ff_sig_rev = (other_rec_patch * gc_lig_patch * ff_coef).sum()
    return ff_sig_fwd, ff_sig_rev


def calculate_cis_interaction(cis_in_fac: float, cis_out_fac: float, outer_gc_lig_patch: np.ndarray,
                              outer_gc_rec_patch: np.ndarray, gc, mask: np.ndarray) -> float:
    """ Compute cis interaction, by adding forward and reverse interaction of inner sensors and outer
     sensors. Two factors are used to represent binding constants for inner and outer interactions.

    Args:
        cis_in_fac: Binding constant for inner interaction.
        cis_out_fac: Binding constant for outer interaction.
        outer_gc_lig_patch: Array of outer gc-ligand-values for every coordinate
        outer_gc_rec_patch: Array of outer gc-receptor-values for every coordinate
        gc: GrowthCone instance to calculate the interaction signals for.
        mask: Array of booleans to determine used sensors

    Returns:
        float: Cis interaction.
    """
    inner_gc_lig_patch, inner_gc_rec_patch = get_inner_patches(gc, mask)
    return cis_in_fac * (inner_gc_lig_patch * inner_gc_rec_patch).sum() + \
        cis_out_fac * (outer_gc_lig_patch * outer_gc_rec_patch).sum()


def calculate_ff_coef(step: int, num_steps: int, sigmoid_steepness: float, sigmoid_shift: float,
                      sigmoid_height: int = 1) -> float:
    """ Compute fiber-fiber coefficient, to determine strength of fiber-fiber-interaction based on the ratio of steps
        taken and total number of steps.

    Args:
        step: Number of current iteration.
        num_steps: Total number of iterations.
        sigmoid_steepness: Steepness of the sigmoid function modelling the ff-coefficient.
        sigmoid_shift: Shift of the sigmoid function modelling the ff-coefficient.
        sigmoid_height: Height of the sigmoid function modelling the ff-coefficient.

    Returns:
        coeff: Coefficient of fiber-fiber interaction.
    """

    step += (num_steps * 0.01)  # such that with shift = 100 immediate activation
    step_ratio = step / num_steps
    sigmoid_adjustment = (step_ratio * sigmoid_shift) ** sigmoid_steepness
    safe_sigmoid = np.clip(sigmoid_adjustment, a_min=1e-10, a_max=None)  # Prevent log(0) which results in -inf
    coeff = max((-np.exp(-safe_sigmoid) + 1) * sigmoid_height, 0)

    return coeff


def get_outer_patches(gc, pos: tuple[int, int], substrate, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """ Create a 2D-Array in Shape of the Substrate consisting of outer Sensor values of the growth cone
    for every unit square.

    Args:
        gc: growth cone instance to calculate the sensors signals for.
        pos: center of the growth cone
        substrate: substrate instance containing the substrates shape
        mask: 2D-Array of booleans to determine used sensors

    Returns:
        lig_patch: 2D-Array of all gc-ligand-values for every coordinate
        rec_patch: 2D-Array of all gc-receptor-values for every coordinate
    """
    radius = gc.radius
    x, y = pos[0], pos[1]
    x0, x1 = x - radius, x + radius + 1
    y0, y1 = y - radius, y + radius + 1

    lig_patch = np.zeros_like(substrate.ligands)
    rec_patch = np.zeros_like(substrate.receptors)
    lig_patch_values = mask * gc.outer_ligand_current
    rec_patch_values = mask * gc.outer_receptor_current

    lig_patch[y0:y1, x0:x1] += lig_patch_values
    rec_patch[y0:y1, x0:x1] += rec_patch_values

    return lig_patch, rec_patch


def get_inner_patches(gc, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Create a 2D-Array holding inner growth cone sensor values for every unit square of the growth cone

    Args:
        gc: growth cone instance to calculate the sensors for.
        mask: 2D-Array of booleans to determine used sensors

    Returns:
        inner_gc_lig_patch: 2D-Array of all inner gc-ligand-values for every coordinate
        inner_gc_rec_patch: 2D-Array of all inner gc-receptor-values for every coordinate
    """
    inner_gc_lig_patch = mask * gc.inner_ligand_current
    inner_gc_rec_patch = mask * gc.inner_receptor_current
    return inner_gc_lig_patch, inner_gc_rec_patch
