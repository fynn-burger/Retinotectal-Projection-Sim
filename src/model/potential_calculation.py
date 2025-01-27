"""
Module providing all methods needed for guidance potential calculation.
"""

import math
import numpy as np


def calculate_potential(gc, pos, gcs, substrate, forward_on, reverse_on, ff_inter_on, ft_inter_on, cis_inter_on,
                        step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height):
    """
    Calculate guidance potential for a growth cone (gc) in a model.
    """

    # Initialize interaction values
    ft_ligands, ft_receptors = (0, 0)
    ff_ligands, ff_receptors = (0, 0)
    ff_coef = 0

    gc_outer_receptor_sum = gc.outer_receptor_current * gc.radius * gc.radius * math.pi
    gc_outer_ligand_sum = gc.outer_ligand_current * gc.radius * gc.radius * math.pi
    gc_inner_receptor_sum = gc.inner_receptor_current * gc.radius * gc.radius * math.pi
    gc_inner_ligand_sum = gc.inner_ligand_current * gc.radius * gc.radius * math.pi

    # Compute interactions only if needed
    if ft_inter_on:
        ft_ligands, ft_receptors = ft_interaction(gc, pos, substrate)
    if ff_inter_on:
        ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
        ff_ligands, ff_receptors = ff_interaction(gc, pos, gcs)

    # Calculate the forward and reverse signals based on flags
    forward_sig = reverse_sig = 0
    if forward_on:
        trans_sig = gc_outer_receptor_sum * ft_ligands
        cis_sig = gc_inner_receptor_sum * gc_inner_ligand_sum if cis_inter_on else 0
        ff_sig = gc_outer_receptor_sum * ff_coef * ff_ligands
        forward_sig = trans_sig + cis_sig + ff_sig
        # forward_sig = gc_outer_receptor_sum * (ft_ligands + (gc_inner_ligand_sum if cis_inter_on else 0) + (ff_coef * ff_ligands))
    if reverse_on:
        trans_sig = gc_outer_ligand_sum * ft_receptors
        cis_sig = gc_inner_ligand_sum * gc_inner_receptor_sum if cis_inter_on else 0
        ff_sig = gc_outer_ligand_sum * ff_coef * ff_receptors
        reverse_sig = trans_sig + cis_sig + ff_sig
        # reverse_sig = gc_outer_ligand_sum * (ft_receptors + (gc_inner_receptor_sum if cis_inter_on else 0) + (ff_coef * ff_receptors))

    # Round and calculate the potential
    forward_sig = float("{:.6f}".format(forward_sig))
    reverse_sig = float("{:.6f}".format(reverse_sig))

    # Ensure signals are strictly positive
    forward_sig = max(forward_sig, 0.0001)
    reverse_sig = max(reverse_sig, 0.0001)

    # Calculate and return the potential
    return abs(math.log(reverse_sig) - math.log(forward_sig))


def ft_interaction(gc, pos, substrate):
    """
    Calculate fiber-target interaction between a growth cone and a substrate.
    """

    borders = bounding_box(pos, gc.radius, substrate)

    # Needed to ensure the circular modelling of growth cones
    edge_length = abs(borders[2] - borders[3])
    center = (borders[2] + borders[3]) / 2, (borders[0] + borders[1]) / 2

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


def ff_interaction(gc1, pos, gcs):
    """
    Calculate the fiber-fiber interaction between a growth cone (gc1) and a list of other growth cones (gcs).
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


def calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height=1):
    """
    Calculate the ratio of steps taken using a sigmoid function, scaled by sigmoid_gain.
    """

    step += (num_steps * 0.01)  # such that with shift = 100 immediate activation
    step_ratio = step / num_steps
    sigmoid_adjustment = (step_ratio * sigmoid_shift) ** sigmoid_steepness
    safe_sigmoid = np.clip(sigmoid_adjustment, a_min=1e-10, a_max=None)  # Prevent log(0) which results in -inf

    return (-np.exp(-safe_sigmoid) + 1) * sigmoid_height


def bounding_box(gc_pos, gc_size, substrate):
    """
    Calculate the boundaries of the bounding box for a growth cone (used in fiber-target interaction).
    """
    # Calculate the bounds of the bounding box
    x_min = max(0, gc_pos[0] - gc_size)
    x_max = min(substrate.cols - 1, gc_pos[0] + gc_size)
    y_min = max(0, gc_pos[1] - gc_size)
    y_max = min(substrate.rows - 1, gc_pos[1] + gc_size)

    return x_min, x_max, y_min, y_max


def euclidean_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points in a 2-dimensional space.
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def intersection_area(gc1_pos, gc2_pos, radius):
    """
    Calculate the area of intersection between two circles (circumscribed around growth cones).
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
        sector = radius ** 2 * math.acos(d / (2 * radius))
        triangle = 0.5 * d * math.sqrt(4 * radius ** 2 - d ** 2)
        return (sector - triangle) * 2

