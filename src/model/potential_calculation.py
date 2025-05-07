"""
Module for computing guidance potential in retinotectal growth cone mapping.

This module provides functions to calculate fiber–target (FT), fiber–fiber (FF), and
cis interaction signals, and combine them into a single guidance potential value per cone.
"""

import math
import numpy as np


def calculate_potential(gc, pos, substrate, forward_on, reverse_on, ff_inter_on, ft_inter_on, cis_inter_on,
                        step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height, all_gc_lig, all_gc_rec):
    """
    Compute the guidance potential for a growth cone at a given position.

    This sums the forward and reverse signals from fiber–target (FT), fiber–fiber (FF)
    and cis interactions (as enabled), then takes the absolute difference of their logarithms

    Args:
        gc (GrowthCone): GrowthCone instance to calculate the potential for.
        pos (tuple): x and y coordinates of the GrowthCone instance
        substrate (Substrate): Contains ligand and receptor-values in a 2D-Array
        forward_on (Boolean): True if forward signal is enabled, False otherwise
        reverse_on (Boolean): True if reverse signal is enabled, False otherwise:
        ff_inter_on (Boolean): True if fiber-fiber interaction is enabled, False otherwise:
        ft_inter_on (Boolean): True if fiber-target interaction is enabled, False otherwise:
        cis_inter_on (Boolean): True if cis interaction is enabled, False otherwise:
        step (int): Current step in the simulation iteration
        num_steps (int): Number of steps the simulation will run. Used to calculate ff-coefficient
        sigmoid_steepness (float): Determines steepness of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_shift (float): Determines shift of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_height (int): Max value for ff-coefficient
        all_gc_lig (np.ndarray): Pre-folded ligand values of all growth cones over substrate ()
        all_gc_rec (np.ndarray): Pre-folded receptor values of all growth cones over substrate

    Returns:
        float: Guidance potential for a given growth cone at a given position.

    Example:
        >>> D = calculate_potential(gc, (10,5), substrate, True, True, True, True, True, 0, 1000, 4.0, 4.0, 15,
        ...                         all_gc_lig, all_gc_rec)
        >>> isinstance(D, float)
        True
    """
    outer_lig_patch, outer_rec_patch = create_outer_patches(gc, pos, substrate)

    # Initialize interaction values
    forward_sig = reverse_sig = 0

    # Calculate and add fiber-target interaction
    if ft_inter_on:
        trans_sig_fwd, trans_sig_rev = calculate_ft_inter(outer_lig_patch, outer_rec_patch,
                                                          substrate.ligands, substrate.receptors)
        forward_sig += trans_sig_fwd
        reverse_sig += trans_sig_rev
    # Calculate and add fiber-fiber interaction
    if ff_inter_on:
        ff_sig_fwd, ff_sig_rev = calculate_ff_inter(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height,
                                                    all_gc_lig, all_gc_rec, outer_lig_patch, outer_rec_patch)
        forward_sig += ff_sig_fwd
        reverse_sig += ff_sig_rev
    # Calculate and add cis interaction
    if cis_inter_on:
        cis_sig = calculate_cis_inter(gc)
        forward_sig += cis_sig
        reverse_sig += cis_sig

    # Check for forward and reverse flags
    forward_sig = forward_sig if forward_on else 0
    reverse_sig = reverse_sig if reverse_on else 0

    # Ensure signals are strictly positive and rounded
    forward_sig = max(float(f"{forward_sig:.6f}"), 1e-4)
    reverse_sig = max(float(f"{reverse_sig:.6f}"), 1e-4)

    # Calculate and return the potential
    return abs(math.log(reverse_sig) - math.log(forward_sig))


def calculate_ft_inter(lig_patch, rec_patch, substrate_ligands, substrate_receptors):
    """
    Calculate fiber-target interaction by multiplying growth-cone gaussian patches with substrate and summing the result

    Args:
        lig_patch (np.ndarray): Pre-folded ligand values over substrate:
        rec_patch (np.ndarray): Pre-folded receptor values over substrate:
        substrate_ligands (np.ndarray): 2D-Array of ligand values over substrate:
        substrate_receptors (np.ndarray): 2D-Array of receptor values over substrate:

    Returns:
        trans_sig_fwd (float): Scalar of total trans forward signal
        trans_sig_rev (float): Scalar of total trans reverse signal

    """
    trans_sig_fwd = (rec_patch * substrate_ligands).sum()
    trans_sig_rev = (lig_patch * substrate_receptors).sum()
    return trans_sig_fwd, trans_sig_rev


def calculate_ff_inter(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height, all_gc_lig, all_gc_rec,
                       lig_patch, rec_patch):
    """
    Calculate fiber-fiber interaction

    Multiplies the current growth cones' sensor patches with the corresponding patch of the pre-folded other
    growth-cones, sums this, and multiplies the scalar with the ff-coefficient

    Args:
        step (int): Current step in the simulation iteration
        num_steps (int): Number of steps the simulation will run. Used to calculate ff-coefficient
        sigmoid_steepness (float): Determines steepness of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_shift (float): Determines shift of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_height (int): Max value for ff-coefficient
        all_gc_lig (np.ndarray): Pre-folded ligand values of all growth cones over substrate
        all_gc_rec (np.ndarray): Pre-folded receptor values of all growth cones over substrate
        lig_patch (np.ndarray): Pre folded ligand values of current growth cone
        rec_patch (np.ndarray): Pre folded receptor values of current growth cone:

    Returns:
        ff_sig_fwd (float): Scalar of total ff-coefficient forward signal
        ff_sig_rev (float): Scalar of total ff-coefficient reverse signal

    """
    ff_coef = calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height)
    other_gc_lig_patch = all_gc_lig - lig_patch
    other_gc_rec_patch = all_gc_rec - rec_patch
    ff_sig_fwd = (other_gc_lig_patch * rec_patch * ff_coef).sum()
    ff_sig_rev = (other_gc_rec_patch * lig_patch * ff_coef).sum()
    return ff_sig_fwd, ff_sig_rev

def calculate_cis_inter(gc):
    """
    Calculate cis interaction, by multiplying the folded patches of inner sensors and taking the sum
    Args:
        gc (GrowthCone): GrowthCone instance of the current growth cone.

    Returns:
        cis_sig (float): Scalar of total cis interaction signal

    """
    inner_lig_patch, inner_rec_patch = create_inner_patches(gc)
    cis_sig = (inner_lig_patch * inner_rec_patch).sum()
    return cis_sig


def calculate_ff_coef(step, num_steps, sigmoid_steepness, sigmoid_shift, sigmoid_height=1):
    """
    Calculate iteration-dependent coefficient to determine strength of fiber-fiber interaction

    The coefficient has a sigmoid like shape

    Args:
        step (int): Current step in the simulation iteration
        num_steps (int): Number of steps the simulation will run. Used to calculate ff-coefficient
        sigmoid_steepness (float): Determines steepness of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_shift (float): Determines shift of sigmoid-curve determining fiber-fiber interaction strength
        sigmoid_height (int): Max value for ff-coefficient

    Returns:
        float: Coefficient of fiber interaction

    """

    step += (num_steps * 0.01)  # such that with shift = 100 immediate activation
    step_ratio = step / num_steps
    sigmoid_adjustment = (step_ratio * sigmoid_shift) ** sigmoid_steepness
    safe_sigmoid = np.clip(sigmoid_adjustment, a_min=1e-10, a_max=None)  # Prevent log(0) which results in -inf

    return (-np.exp(-safe_sigmoid) + 1) * sigmoid_height


def create_outer_patches(gc, pos, substrate):
    """
    Calculate sensor patches for growth cone using gaussian kernel on outer sensor values

    Args:
        gc (GrowthCone): GrowthCone instance of the current growth cone.:
        pos (tuple): Position of the current growth cone.:
        substrate (Substrate): Contains 2D-Arrays of sensor values

    Returns:
        lig_patch (np.ndarray): 2D-Array of zeros with gaussian kernel applied growth cone outer ligand values
                                at correct pos
        rec_patch (np.ndarray): 2D-Array of zeros with gaussian kernel applied growth cone outer sensor values
                                at correct pos

    """
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
    """
    Calculate gaussian kernel weighted sensor patches using inner sensor values

    Args:
        gc (GrowthCone): GrowthCone instance of the current growth cone.:

    Returns:
        lig_patch (np.ndarray): 2D-Array of zeros with gaussian kernel applied growth cone inner ligand values
                                at correct pos
        rec_patch (np.ndarray): 2D-Array of zeros with gaussian kernel applied growth cone inner sensor values
                                at correct pos

    """
    lig_patch = gc.gauss_kernel * gc.inner_ligand_current
    rec_patch = gc.gauss_kernel * gc.inner_receptor_current

    return lig_patch, rec_patch
