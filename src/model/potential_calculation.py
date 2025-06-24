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


def calculate_potential(gc, pos: tuple[int, int], gcs: list, substrate, forward_on: bool, reverse_on: bool,
                        ff_inter_on: bool, ft_inter_on: bool, cis_inter_on: bool, step: int, num_steps: int,
                        sigmoid_steepness: float, sigmoid_shift: float, sigmoid_height: int,
                        cis_in_fac: float, cis_out_fac: float) -> float:
    """
    Compute the guidance potential for a single growth cone.

    This calculates forward and reverse contributions from fiber-target, fiber-fiber,
    and cis interactions and returns the log-ratio of reverse to forward signals.

    Args:
        gc: GrowthCone instance.
        pos: Position to check potential for.
        gcs: List of all GrowthCone instances.
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

    Returns:
        float: Potential of gc at position pos.
    """

    # get sensor sums
    gc_outer_receptor_sum, gc_outer_ligand_sum, gc_inner_receptor_sum, gc_inner_ligand_sum = get_sensor_sums(gc)

    # Calculate interactions based on toggles
    # Calculate trans-interaction
    trans_sig_fwd, trans_sig_rev = calculate_ft_interaction(gc, pos, substrate, gc_outer_receptor_sum,
                                                            gc_outer_ligand_sum) if ft_inter_on else (0, 0)

    # Calculate fiber-fiber-interaction
    ff_sig_fwd, ff_sig_rev = calculate_ff_interaction(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height,
                                                      gc, pos, gcs, gc_outer_receptor_sum, gc_outer_ligand_sum) \
        if ff_inter_on else (0, 0)

    # Calculate cis-interaction
    cis_sig_fwd = cis_sig_rev = calculate_cis_interaction(cis_in_fac, cis_out_fac, gc_outer_receptor_sum,
                                                          gc_outer_ligand_sum, gc_inner_receptor_sum,
                                                          gc_inner_ligand_sum) if cis_inter_on else 0

    # Calculate forward and reverse signals based on flags
    forward_sig = trans_sig_fwd + ff_sig_fwd + cis_sig_fwd if forward_on else 0
    reverse_sig = trans_sig_rev + ff_sig_rev + cis_sig_rev if reverse_on else 0

    # Use non-zero values for forward and reverse sig and format value
    forward_sig = max(float("{:.6f}".format(forward_sig)), 0.0001)
    reverse_sig = max(float("{:.6f}".format(reverse_sig)), 0.0001)

    # Calculate and return the potential
    return abs(math.log(reverse_sig) - math.log(forward_sig))


def calculate_ft_interaction(gc, pos: tuple[int, int], substrate, gc_outer_receptor_sum: float,
                             gc_outer_ligand_sum: float) -> tuple[float, float]:
    """ Compute fiber-target interaction by multiplying gc-receptors with substrate-ligands and vice versa.

    Args:
        gc: GrowthCone instance to calculate the interaction signals for.
        pos: Position to check potential for.
        substrate: Substrate instance holding the sensor values
        gc_outer_receptor_sum: Sum of outer receptors of the growth cone.
        gc_outer_ligand_sum: Sum of outer ligands of the growth cone.

    Returns:
        float: Fiber-target interaction signal of gc at position pos (forward, reverse).
    """
    ft_ligands, ft_receptors = get_ft_sensors(gc, pos, substrate)
    return gc_outer_receptor_sum * ft_ligands, gc_outer_ligand_sum * ft_receptors


def calculate_ff_interaction(step: int, num_steps: int, sigmoid_steepness: float, sigmoid_shift: float,
                             sigmoid_height: int, gc, pos: tuple[int, int], gcs: list,
                             gc_outer_receptor_sum: float, gc_outer_ligand_sum: float) -> tuple[float, float]:
    """Compute fiber-fiber interaction by multiplying gc-receptors with overlapping receptors of other gcs
    and vice versa, dependent on the ff-coefficient.

    Args:
        step: Current iteration step.
        num_steps: Total number of simulation steps.
        sigmoid_steepness: Steepness for ff-coefficient.
        sigmoid_shift: Shift for ff-coefficient.
        sigmoid_height: Maximum height for ff-coefficient.
        gc: GrowthCone instance to calculate the interaction signals for.
        pos: Position to check potential for.
        gcs: List of all GrowthCone instances.
        gc_outer_receptor_sum: Sum over outer receptors of the growth cone.
        gc_outer_ligand_sum: Sum over outer ligands of the growth cone.

    Returns:
        Forward and reverse fiber-fiber interaction signal.
    """
    ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
    ff_ligands, ff_receptors = get_ff_sensors(gc, pos, gcs)
    return gc_outer_receptor_sum * ff_coef * ff_ligands, gc_outer_ligand_sum * ff_coef * ff_receptors


def calculate_cis_interaction(cis_in_fac: float, cis_out_fac: float, gc_outer_receptor_sum: float,
                              gc_outer_ligand_sum: float, gc_inner_receptor_sum: float, gc_inner_ligand_sum: float)\
        -> float:
    """ Compute cis interaction, by adding forward and reverse interaction of inner sensors and outer
     sensors. Two factors are used to represent binding constants for inner and outer interactions.

    Args:
        cis_in_fac: Binding constant for inner interaction.
        cis_out_fac: Binding constant for outer interaction.
        gc_outer_receptor_sum: Sum of outer receptors of the growth cone.
        gc_outer_ligand_sum: Sum of outer ligands of the growth cone.
        gc_inner_receptor_sum: Sum of inner receptors of the growth cone.
        gc_inner_ligand_sum: Sum of inner ligands of the growth cone.

    Returns:
        float: Cis interaction.
    """
    return cis_in_fac * (gc_inner_receptor_sum * gc_inner_ligand_sum) \
        + cis_out_fac * (gc_outer_receptor_sum * gc_outer_ligand_sum)


def get_ft_sensors(gc, pos: tuple[int, int], substrate) -> tuple[float, float]:
    """Calculate the number of ligands and receptors on the substrate, that interact with the growth cone.

    Args:
        gc: GrowthCone instance to calculate the interacting sensors for.
        pos: Center of the growth cone instance.
        substrate: Substrate instance holding the sensor values.

    Returns:
        tuple[float, float]: Number of ligands and receptors on the substrate that interact with the growth cone.
    """

    borders = bounding_box(pos, gc.radius, substrate)

    # Needed to ensure the circular modelling of growth cones
    edge_length = abs(borders[2] - borders[3])
    center = int((borders[2] + borders[3]) / 2), int((borders[0] + borders[1]) / 2)

    sum_ligands = 0
    sum_receptors = 0

    for i in range(borders[2], borders[3]):
        for j in range(borders[0], borders[1]):
            d = euclidean_distance(center, (i, j))
            if d > edge_length / 2:
                # Eliminate cells outside of the circle, as borders define a square matrix
                continue
            sum_ligands += substrate.ligands[i, j]
            sum_receptors += substrate.receptors[i, j]

    return sum_ligands, sum_receptors


def get_ff_sensors(gc1, pos: tuple[int, int], gcs) -> tuple[float, float]:
    """Calculate the number of ligands and receptors on other growth cones that interact with the growth cone.

    Args:
        gc1: Growth cone instance to calculate the interacting sensors for.
        pos: Center of the growth cone instance.
        gcs: List of all growth cone instances.

    Returns:
        tuple[float, float]: Number of ligands and receptors on other growth cones that interact with the growth cone.
    """
    sum_ligands = 0
    sum_receptors = 0

    for gc2 in gcs:
        if gc1 == gc2:
            # TODO: @Performance Sort GCs based on location and use pruning algorithms
            # Eliminate self from the gcs list, as self-comparison always matches
            continue
        d = euclidean_distance(gc2.pos, pos)
        if d < gc1.radius * 2:
            area = intersection_area(pos, gc2.pos, gc1.radius)
            sum_ligands += area * gc2.outer_ligand_current
            sum_receptors += area * gc2.outer_receptor_current

    return sum_ligands, sum_receptors


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


def bounding_box(gc_pos: tuple[int, int], gc_size: [int], substrate) -> tuple[int, int, int, int]:
    """ Calculate the boundaries of the bounding box for a growth cone (used in fiber-target interaction).

    Args:
        gc_pos: Center of growth cone instance.
        gc_size: Radius of the growth cone instance is gc_size * 2 + 1
        substrate: Substrate instance holding grid-structure

    Returns:
        x_min, y_min, x_max, y_max: Bounding box of the growth cone.
    """
    # Calculate the bounds of the bounding box
    x_min = max(0, gc_pos[0] - gc_size)
    x_max = min(substrate.cols - 1, gc_pos[0] + gc_size)
    y_min = max(0, gc_pos[1] - gc_size)
    y_max = min(substrate.rows - 1, gc_pos[1] + gc_size)

    return x_min, x_max, y_min, y_max


def euclidean_distance(point1: tuple[int, int], point2: tuple[int, int]) -> float:
    """ Calculate the Euclidean distance between two points on a 2D-grid.

    Args:
        point1: Center of the first growth cone instance.
        point2: Center of another growth cone instance

    Returns:
        float: Euclidean distance between two points on a 2D-grid.
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def intersection_area(gc1_pos: tuple[int, int], gc2_pos: tuple[int, int], radius: int) -> float:
    """ Calculate the intersection area between two growth cones

    Args:
        gc1_pos: Center of one growth cone instance.
        gc2_pos: Center of another growth cone instance.
        radius: Radius of both growth cones.

    Returns:
        float: Intersection area between the two growth cones.
    """
    d = euclidean_distance(gc1_pos, gc2_pos)  # Distance between the centers of the circles

    if d == 0:
        # Total overlap
        return radius * radius * math.pi
    elif d > radius * 2:
        # No overlap
        return 0
    else:
        # Check figure intersection_area for visualization: sector = PBDC, triangle = PBEC
        sector = 2 * radius ** 2 * math.acos(d / (2 * radius))
        triangle = 0.5 * d * math.sqrt(4 * radius ** 2 - d ** 2)
        if sector < triangle:
            print(sector, triangle)
        return (sector - triangle) * 2


def get_sensor_sums(gc) -> tuple[float, float, float, float]:
    """Calculate the sums of inner and outer ligands and receptors on a given growth cone instance

    Args:
        gc: Growth cone instance.

    Returns:
        outer_r_sum, outer_l_sum, inner_r_sum, inner_l_sum: Sums of sensors
    """
    gc_area = gc.radius * gc.radius * math.pi
    outer_r_sum = gc.outer_receptor_current * gc_area
    outer_l_sum = gc.outer_ligand_current * gc_area
    inner_r_sum = gc.inner_receptor_current * gc_area
    inner_l_sum = gc.inner_ligand_current * gc_area
    return outer_r_sum, outer_l_sum, inner_r_sum, inner_l_sum
