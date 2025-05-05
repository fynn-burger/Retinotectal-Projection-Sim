"""
Module providing all methods needed for guidance potential calculation.
"""

import math
import numpy as np
from build import config as cfg
from visualization import utils as vz


def calculate_potential(gc, pos, gcs, substrate, forward_on, reverse_on, ff_inter_on, ft_inter_on, cis_inter_on,
                        step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height):
    """
    Calculate guidance potential for a growth cone (gc) in a model.
    """

    # Precompute Gaussian kernel sum for cis-interaction (always available)
    a = cfg.current_config[cfg.GC_GAUSS_DECAY]
    thr = cfg.current_config[cfg.GC_GAUSS_THRESHOLD]
    _, kernel_sum = make_gauss_kernel(a, thr)

    # Initialize interaction values
    trans_sig_fwd = trans_sig_rev = 0
    ff_sig_fwd = ff_sig_rev = 0
    cis_sig_fwd = cis_sig_rev = 0
    forward_sig = reverse_sig = 0

    # Compute interactions only if needed
    if ft_inter_on:
        ft_ligands, ft_receptors = ft_interaction(gc, pos, substrate)
        trans_sig_fwd = gc.outer_receptor_current * ft_ligands
        trans_sig_rev = gc.outer_ligand_current * ft_receptors
    if ff_inter_on:
        ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
        ff_ligands, ff_receptors = ff_interaction(gc, pos, gcs)
        ff_sig_fwd = gc.outer_receptor_current * ff_coef * ff_ligands
        ff_sig_rev = gc.outer_ligand_current * ff_coef * ff_receptors
    if cis_inter_on:
        cis_sig_fwd = cis_sig_rev = gc.inner_ligand_current * gc.inner_receptor_current * kernel_sum

    # Calculate the forward and reverse signals based on flags
    if forward_on:
        forward_sig = trans_sig_fwd + cis_sig_fwd + ff_sig_fwd
    if reverse_on:
        reverse_sig = trans_sig_rev + cis_sig_rev + ff_sig_rev

    # Ensure signals are strictly positive and rounded
    forward_sig = max(float(f"{forward_sig:.6f}"), 1e-4)
    reverse_sig = max(float(f"{reverse_sig:.6f}"), 1e-4)

    # Calculate and return the potential
    return abs(math.log(reverse_sig) - math.log(forward_sig))


def make_gauss_kernel(a, threshold):
    """
    Build unnormalized 2D Gaussian kernel with decay a and threshold cutoff.
    Returns kernel array and its sum.
    """
    r_exact = math.sqrt(-math.log(threshold) / a)
    radius = math.ceil(r_exact)
    size = 2 * radius + 1
    x_array = np.arange(size) - radius
    y_array = x_array.copy()
    X, Y = np.meshgrid(x_array, y_array, indexing='ij')
    G = np.exp(-a * (X**2 + Y**2))
    G[G < threshold] = 0.0
    kernel_sum = G.sum()
    return G, kernel_sum


def ft_interaction(gc, pos, substrate):
    """
    Fiber-target: Gaussian-weighted sum over substrate around pos.
    Returns ligand_sum, receptor_sum.
    """
    a = cfg.current_config[cfg.GC_GAUSS_DECAY]
    thr = cfg.current_config[cfg.GC_GAUSS_THRESHOLD]
    G, _ = make_gauss_kernel(a, thr)
    radius = G.shape[0] // 2
    x, y = int(pos[0]), int(pos[1])
    x0, x1 = x - radius, x + radius + 1
    y0, y1 = y - radius, y + radius + 1
    sub_lig = substrate.ligands[y0:y1, x0:x1]
    sub_rec = substrate.receptors[y0:y1, x0:x1]
    # bounds check
    if sub_lig.shape != G.shape:
        raise IndexError(f"FT interaction patch out-of-bounds at pos {pos} with kernel size {G.shape}")
    ligand_sum = (G * sub_lig).sum()
    receptor_sum = (G * sub_rec).sum()
    return ligand_sum, receptor_sum


def ff_interaction(gc1, pos, gcs):
    """
    Fiber-fiber: Gaussian-weighted sum over other growth cones' outer sensors.
    Returns ligand_sum, receptor_sum.
    """
    a = cfg.current_config[cfg.GC_GAUSS_DECAY]
    thr = cfg.current_config[cfg.GC_GAUSS_THRESHOLD]
    ligand_sum = receptor_sum = 0.0

    for gc2 in gcs:
        if gc1 == gc2:
            # TODO: @Performance Sort GCs based on location and use pruning algorithms
            # Eliminate self from the gcs list, as self-comparison always matches
            continue
        d = math.dist(gc2.pos, pos)
        w = math.exp(-a * d * d)
        if w < thr:
            continue
        area = intersection_area(pos, gc2.pos, gc1.radius)
        ligand_sum += w * gc2.outer_ligand_current * area
        receptor_sum += w * gc2.outer_receptor_current * area
    return ligand_sum, receptor_sum


def calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height=1):
    """
    Calculate the ratio of steps taken using a sigmoid function, scaled by sigmoid_gain.
    """

    step += (num_steps * 0.01)  # such that with shift = 100 immediate activation
    step_ratio = step / num_steps
    sigmoid_adjustment = (step_ratio * sigmoid_shift) ** sigmoid_steepness
    safe_sigmoid = np.clip(sigmoid_adjustment, a_min=1e-10, a_max=None)  # Prevent log(0) which results in -inf

    return (-np.exp(-safe_sigmoid) + 1) * sigmoid_height


def intersection_area(gc1_pos, gc2_pos, radius):
    """
    Calculate the area of intersection between two circles (circumscribed around growth cones).
    """
    d = math.dist(gc1_pos, gc2_pos)  # Distance between the centers of the circles

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


