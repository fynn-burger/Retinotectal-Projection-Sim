"""
Module providing all methods needed for guidance potential calculation.
"""

import math
import numpy as np


def calculate_potential(gc, pos, gcs, substrate, forward_on, reverse_on, ff_inter_on, ft_inter_on, cis_inter_on,
                        step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height, cis_in_fac, cis_out_fac):
    """
    Calculate guidance potential for a growth cone (gc) in a model.
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


def calculate_ft_interaction(gc, pos, substrate, gc_outer_receptor_sum, gc_outer_ligand_sum):
    ft_ligands, ft_receptors = get_ft_sensors(gc, pos, substrate)
    return gc_outer_receptor_sum * ft_ligands, gc_outer_ligand_sum * ft_receptors


def calculate_ff_interaction(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height, gc, pos, gcs,
                             gc_outer_receptor_sum, gc_outer_ligand_sum):
    ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
    ff_ligands, ff_receptors = get_ff_sensors(gc, pos, gcs)
    return gc_outer_receptor_sum * ff_coef * ff_ligands, gc_outer_ligand_sum * ff_coef * ff_receptors


def calculate_cis_interaction(cis_in_fac, cis_out_fac, gc_outer_receptor_sum, gc_outer_ligand_sum,
                              gc_inner_receptor_sum, gc_inner_ligand_sum):
    return cis_in_fac * (gc_inner_receptor_sum * gc_inner_ligand_sum) \
            + cis_out_fac * (gc_outer_receptor_sum * gc_outer_ligand_sum)


def get_ft_sensors(gc, pos, substrate):
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


def get_ff_sensors(gc1, pos, gcs):
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
    coeff = max((-np.exp(-safe_sigmoid) + 1) * sigmoid_height, 0)

    return coeff


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
        sector = 2 * radius ** 2 * math.acos(d / (2 * radius))
        triangle = 0.5 * d * math.sqrt(4 * radius ** 2 - d ** 2)
        if sector < triangle:
            print(sector, triangle)
        return (sector - triangle) * 2


def get_sensor_sums(gc):
    gc_area = gc.radius * gc.radius * math.pi
    outer_r_sum = gc.outer_receptor_current * gc_area
    outer_l_sum = gc.outer_ligand_current * gc_area
    inner_r_sum = gc.inner_receptor_current * gc_area
    inner_l_sum = gc.inner_ligand_current * gc_area
    return outer_r_sum, outer_l_sum, inner_r_sum, inner_l_sum
