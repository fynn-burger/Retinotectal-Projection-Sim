"""
Module providing all methods needed for guidance potential calculation.
"""

import math
import numpy as np


def calculate_potential(gc, pos, substrate, forward_on, reverse_on, ff_inter_on, ft_inter_on, cis_inter_on,
                        step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height, all_gc_lig, all_gc_rec):
    """
    Calculate guidance potential for a growth cone (gc) in a model.
    """
    outer_lig_patch, outer_rec_patch = create_outer_patches(gc, pos, substrate)

    # Initialize interaction values
    trans_sig_fwd = trans_sig_rev = 0
    ff_sig_fwd = ff_sig_rev = 0
    cis_sig_fwd = cis_sig_rev = 0
    forward_sig = reverse_sig = 0

    # Compute interactions only if needed
    if ft_inter_on:
        trans_sig_fwd = (outer_rec_patch * substrate.ligands).sum()
        trans_sig_rev = (outer_lig_patch * substrate.receptors).sum()
    if ff_inter_on:
        ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
        other_gc_lig_patch = all_gc_lig - outer_lig_patch
        other_gc_rec_patch = all_gc_rec - outer_rec_patch
        ff_sig_fwd = (other_gc_lig_patch * outer_rec_patch * ff_coef).sum()
        ff_sig_rev = (other_gc_rec_patch * outer_lig_patch * ff_coef).sum()
    if cis_inter_on:
        inner_lig_patch, inner_rec_patch = create_inner_patches(gc)
        cis_sig_fwd = cis_sig_rev = (inner_lig_patch * inner_rec_patch).sum()

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


def calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height=1):
    """
    Calculate the ratio of steps taken using a sigmoid function, scaled by sigmoid_gain.
    """

    step += (num_steps * 0.01)  # such that with shift = 100 immediate activation
    step_ratio = step / num_steps
    sigmoid_adjustment = (step_ratio * sigmoid_shift) ** sigmoid_steepness
    safe_sigmoid = np.clip(sigmoid_adjustment, a_min=1e-10, a_max=None)  # Prevent log(0) which results in -inf

    return (-np.exp(-safe_sigmoid) + 1) * sigmoid_height


def create_outer_patches(gc, pos, substrate):
    radius = math.floor(gc.radius)
    x, y = pos[0], pos[1]
    x0, x1 = x - radius, x + radius + 1
    y0, y1 = y - radius, y + radius + 1

    lig_patch = np.zeros_like(substrate.ligands)
    rec_patch = np.zeros_like(substrate.receptors)
    lig_patch_values = gc.gauss_kernel * gc.outer_ligand_current
    rec_patch_values = gc.gauss_kernel * gc.outer_receptor_current

    lig_patch[y0:y1, x0:x1] += lig_patch_values
    rec_patch[y0:y1, x0:x1] += rec_patch_values

    return lig_patch, rec_patch



def create_inner_patches(gc):
    lig_patch = gc.gauss_kernel * gc.inner_ligand_current
    rec_patch = gc.gauss_kernel * gc.inner_receptor_current

    return lig_patch, rec_patch



