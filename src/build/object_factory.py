"""
Module for constructing simulation environments and growth cones for the retinotectal projection model.

This builder module provides:
- `build_default()`: Create a Simulation using the current global configuration.
- `build_simulation(config)`: Build a Simulation instance from an arbitrary config dictionary.
- `build_substrate(config)`: Instantiate the appropriate Substrate subclass based on config.
- `initialize_growth_cones(config)`: Create and configure a list of GrowthCone objects.
"""

import numpy as np

from build import config as cfg
from model.growth_cone import GrowthCone
from model.simulation import Simulation
from model.substrate import (ContinuousGradientSubstrate, WedgeSubstrate,
                             StripeSubstrate, GapSubstrate, GapSubstrateInverted)


def build_default() -> Simulation:
    """
    Construct a Simulation using the global `cfg.current_config` settings.

    Returns:
        Simulation: A fully initialized Simulation instance based on the current config.
    """
    return build_simulation(cfg.current_config)


def build_simulation(config) -> Simulation:
    """
    Build a Simulation object from a configuration dictionary.

    This function:
    1. Builds the substrate instance.
    2. Initializes growth cones.
    3. Extracts simulation parameters from `config`.
    4. Instantiates and returns a `Simulation`.

    Args:
        config (dict): Configuration mapping parameter keys to values.

    Returns:
        Simulation: The configured simulation ready to run.
    """
    # Build other parts
    substrate = build_substrate(config)
    growth_cones = initialize_growth_cones(config)

    # Extract attributes from the configuration
    step_size = config.get(cfg.STEP_SIZE)
    num_steps = config.get(cfg.STEP_NUM)

    x_step_p = config.get(cfg.X_STEP_POSSIBILITY)
    y_step_p = config.get(cfg.Y_STEP_POSSIBILITY)
    sigmoid_steepness = config.get(cfg.SIGMOID_STEEPNESS)
    sigmoid_shift = config.get(cfg.SIGMOID_SHIFT)
    sigmoid_height = config.get(cfg.SIGMOID_HEIGHT)
    cis_in_fac = config.get(cfg.CIS_IN_FAC)
    cis_out_fac = config.get(cfg.CIS_OUT_FAC)
    sigma = config.get(cfg.SIGMA)
    force = config.get(cfg.FORCE)
    forward_sig = config.get(cfg.FORWARD_SIG)
    reverse_sig = config.get(cfg.REVERSE_SIG)
    ff_inter = config.get(cfg.FF_INTER)
    ft_inter = config.get(cfg.FT_INTER)
    cis_inter = config.get(cfg.CIS_INTER)

    adaptation = config.get(cfg.ADAPTATION_ENABLED)
    mu = config.get(cfg.ADAPTATION_MU) if adaptation else 0
    lambda_ = config.get(cfg.ADAPTATION_LAMBDA) if adaptation else 0
    history_length = config.get(cfg.ADAPTATION_HISTORY) if adaptation else 0

    interim_results = config.get(cfg.INTERIM_RESULTS)
    gc_scope = config.get(cfg.GC_SCOPE)
    substrate_scope = config.get(cfg.SUBSTRATE_SCOPE)

    # Initialize the Simulation object with the new parameters
    simulation = Simulation(config, substrate, growth_cones, adaptation, step_size, num_steps, x_step_p, y_step_p,
                            sigmoid_steepness, sigmoid_shift, sigmoid_height, cis_in_fac, cis_out_fac,
                            sigma, force, forward_sig, reverse_sig, ff_inter, ft_inter, cis_inter, mu, lambda_,
                            history_length, interim_results, gc_scope, substrate_scope)
    return simulation


def build_substrate(config):
    """
    Instantiate the correct Substrate subclass based on config type.

    Args:
        config (dict): Configuration mapping parameter keys to values.

    Returns:
        Substrate: A configured substrate instance.

    Raises:
        ValueError: If the substrate type is unrecognized.
    """
    # Extract attributes from the configuration
    rows = config.get(cfg.ROWS)
    cols = config.get(cfg.COLS)
    offset = config.get(cfg.GC_SIZE)
    substrate_type = config.get(cfg.SUBSTRATE_TYPE)

    if substrate_type == cfg.CONTINUOUS_GRADIENTS:
        cont_grad_r_factor = config.get(cfg.CONT_GRAD_R_FACTOR)
        cont_grad_l_factor = config.get(cfg.CONT_GRAD_L_FACTOR)
        cont_grad_r_shift = config.get(cfg.CONT_GRAD_R_SHIFT)
        cont_grad_l_shift = config.get(cfg.CONT_GRAD_L_SHIFT)
        cont_grad_r_decay = config.get(cfg.CONT_GRAD_R_DECAY)
        cont_grad_l_decay = config.get(cfg.CONT_GRAD_L_DECAY)
        substrate = ContinuousGradientSubstrate(rows, cols, offset, cont_grad_r_factor=cont_grad_r_factor,
                                                cont_grad_l_factor=cont_grad_l_factor,
                                                cont_grad_r_shift=cont_grad_r_shift,
                                                cont_grad_l_shift=cont_grad_l_shift,
                                                cont_grad_r_decay=cont_grad_r_decay,
                                                cont_grad_l_decay=cont_grad_l_decay)

    elif substrate_type == cfg.WEDGES:
        wedge_narrow_edge = config.get(cfg.WEDGE_NARROW_EDGE)
        wedge_wide_edge = config.get(cfg.WEDGE_WIDE_EDGE)
        substrate = WedgeSubstrate(rows, cols, offset, narrow_edge=wedge_narrow_edge, wide_edge=wedge_wide_edge)

    elif substrate_type == cfg.STRIPE:
        stripe_fwd = config.get(cfg.STRIPE_FWD)
        stripe_rew = config.get(cfg.STRIPE_REW)
        stripe_ligand_conc = config.get(cfg.STRIPE_LIGAND_CONC)
        stripe_receptor_conc = config.get(cfg.STRIPE_RECEPTOR_CONC)
        stripe_width = config.get(cfg.STRIPE_WIDTH)
        substrate = StripeSubstrate(rows, cols, offset, fwd=stripe_fwd, rew=stripe_rew, ligand_conc=stripe_ligand_conc,
                                    receptor_conc=stripe_receptor_conc, width=stripe_width)

    elif substrate_type == cfg.GAP:
        gap_begin = config.get(cfg.GAP_BEGIN)
        gap_end = config.get(cfg.GAP_END)
        gap_first_block = config.get(cfg.GAP_FIRST_BLOCK)
        gap_second_block = config.get(cfg.GAP_SECOND_BLOCK)
        gap_first_block_conc = config.get(cfg.GAP_FIRST_BLOCK_CONC)
        gap_second_block_conc = config.get(cfg.GAP_SECOND_BLOCK_CONC)
        substrate = GapSubstrate(rows, cols, offset, begin=gap_begin, end=gap_end, first_block=gap_first_block,
                                 second_block=gap_second_block, first_block_conc=gap_first_block_conc,
                                 second_block_conc=gap_second_block_conc)

    elif substrate_type == cfg.GAP_INV:
        gap_begin = config.get(cfg.GAP_BEGIN)
        gap_end = config.get(cfg.GAP_END)
        gap_first_block = config.get(cfg.GAP_FIRST_BLOCK)
        gap_first_block_conc = config.get(cfg.GAP_FIRST_BLOCK_CONC)
        substrate = GapSubstrateInverted(rows, cols, offset, begin=gap_begin, end=gap_end, first_block=gap_first_block,
                                         first_block_conc=gap_first_block_conc)

    else:
        raise ValueError("SubstrateType unknown")

    substrate.initialize_substrate()
    return substrate


def initialize_growth_cones(config):
    """
    Create and initialize all GrowthCone instances based on config gradients and scope.

    Args:
        config (dict): Configuration mapping parameter keys to values.

    Returns:
        List[GrowthCone]: A list of configured GrowthCone objects.
    """

    # Extract parameters from the configuration
    growth_cones = []
    gc_count = config.get(cfg.GC_COUNT)
    size = config.get(cfg.GC_SIZE)
    rows = config.get(cfg.ROWS)
    rho = config.get(cfg.RHO)
    cols = config.get(cfg.COLS)
    gc_r_factor = config.get(cfg.GC_R_FACTOR)
    gc_l_factor = config.get(cfg.GC_L_FACTOR)
    gc_r_shift = config.get(cfg.GC_R_SHIFT)
    gc_l_shift = config.get(cfg.GC_L_SHIFT)
    gc_r_decay = config.get(cfg.GC_R_DECAY)
    gc_l_decay = config.get(cfg.GC_L_DECAY)
    knock_in = config.get(cfg.KNOCK_IN)
    fsfac = 50/cols # Normalize gradient, to be the same independent on col-number

    # Initialize sensor gradients
    x_positions = np.linspace(1, cols, gc_count)
    center = (cols + 1) / 2

    receptors = []
    ligands = []
    for position in x_positions:
        receptors.append(gc_r_factor * np.exp(gc_r_decay * (fsfac * (position - center) + gc_r_shift)))
        ligands.append(gc_l_factor * np.exp(-gc_l_decay * (fsfac * (position - center) + gc_l_shift)))

    # Create an array of evenly distributed y-positions for the growth cones
    y_positions = np.linspace(size, rows - 1 + size, gc_count, dtype=int)

    for i in range(gc_count):
        # Create a GrowthCone instance and initialize it
        pos_y = y_positions[i]
        gc = GrowthCone((int(size), int(pos_y)), size, ligands[i], receptors[i], i, rho, knock_in)
        growth_cones.append(gc)

    # Get growth cone scope from config and take the appropriate part of the growth cones
    if cfg.current_config.get(cfg.GC_SCOPE) != "full":
        gc_len = int(len(growth_cones))
        half_len = int(gc_len / 2)
        if cfg.current_config.get(cfg.GC_SCOPE) == "nasal":
            good_gcs = growth_cones[0:half_len]
        elif cfg.current_config.get(cfg.GC_SCOPE) == "temporal":
            good_gcs = growth_cones[half_len:gc_len]
        else:
            raise Exception("Unknown half gradient type")

        growth_cones = good_gcs  # only use "good gcs for simulation"

    return growth_cones
