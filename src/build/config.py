"""
Retinotectal Projection Model - Configuration Module

This module defines constants, parameter presets, and utility functions for configuring simulations
of the retinotectal projection model. It supports several substrate types (e.g. continuous gradients,
wedges, stripe assays, gap assays) and provides default and custom parameter sets.

Sections:
- CONFIGURATION KEYS: Names for all parameters used across the model.
- CONFIGURATION MODULES: Default parameter sets grouped by model component or substrate.
- DEFAULT CONFIGURATIONS: Canonical configurations for specific experimental setups.
- CUSTOM CONFIGURATION: A user-defined custom parameter dictionary.
- CURRENT CONFIGURATION: The configuration currently in use.
- get_default_config(): Helper to retrieve defaults by substrate type.
"""


"""
--------------------------------------
        CONFIGURATION KEYS
--------------------------------------
"""

# Simulation Basic Parameters
GC_COUNT = "gc_count"                           # Number of growth cones
GC_SIZE = "gc_size"                             # For FT-Interaction diameter is 2 * gc_size + 1 for FF 2 * gc_size
STEP_SIZE = "step_size"                         # Step size per iteration
STEP_NUM = "step_num"                           # Number of iterations

# Simulation Advanced Parameters
X_STEP_POSSIBILITY = "x_step_possibility"       # Likelihood of growth cone to step in positive x-direction
Y_STEP_POSSIBILITY = "y_step_possibility"       # Likelihood of growth cone to step in y-direction
SIGMOID_STEEPNESS = "sigmoid_steepness"         # Steepness of FF-Coefficient Curve
SIGMOID_SHIFT = "sigmoid_shift"                 # Shift of FF-Coefficient Curve
SIGMOID_HEIGHT = "sigmoid_height"               # Maximum Value for FF-Coefficient
CIS_IN_FAC = "cis_in_fac"                       # Factor for intracellular cis-interaction
CIS_OUT_FAC = "cis_out_fac"                     # Factor for surface cis-interaction
SIGMA = "sigma"                                 # Standard deviation of gaussian curve determining step decision noise
FORCE = "force"                                 # Toggle to force growth cone to take every step
FORWARD_SIG = "forward_sig"                     # Toggle for forward signalling
REVERSE_SIG = "reverse_sig"                     # Toggle for reverse signalling
FF_INTER = "ff_inter"                           # Toggle for FF-interaction
FT_INTER = "ft_inter"                           # Toggle for FT-interaction
CIS_INTER = "cis_inter"                         # Toggle for cis-interaction

# Growth Cones
GC_R_DECAY = "receptor_decay"                   # Decay of exponential receptor gradient of growth cones
GC_L_DECAY = "ligand_decay"                     # Decay of exponential ligand gradient of growth cones
GC_R_FACTOR = "gc_r_factor"                     # Factor to move whole receptor gradient of growth cones up or down
GC_L_FACTOR = "gc_l_factor"                     # Factor to move whole ligand gradient of growth cones up or down
GC_R_SHIFT = "gc_r_shift"                       # Shift receptor gradient of growth cones
GC_L_SHIFT = "gc_l_shift"                       # Shift ligand gradient of growth cones
KNOCK_IN = "knock_in"                           # Number by which to increase receptors in knock-in experiment
RHO = "rho"                                     # Start value for adaptation/ Fraction of sensors on growth cone surface
GC_SCOPE = "gc_scope"                           # Enum to decide if whole, nasal, temporal part of gradient is used

# Adaptation
ADAPTATION_ENABLED = "adaptation_enabled"       # Toggle for adaptation
ADAPTATION_MU = "adaptation_mu"                 # Factor for adaptation
ADAPTATION_LAMBDA = "adaptation_lambda"         # Factor for resetting force
ADAPTATION_HISTORY = "adaptation_history"       # Number of previous steps to influence adaptation calculation

# Substrate Types
CONTINUOUS_GRADIENTS = "continuous_gradients"   # Substrate Type: Continuous gradient for tectal simulation
WEDGES = "wedges"                               # Substrate Type: Wedges to simulate in vitro reconstruction of contin.
STRIPE = "stripe"                               # Substrate Type: Stripe to simulate stripe assays
GAP = "gap"                                     # Substrate Type: Gap to simulate gap assays
GAP_INV = "gap_inv"                             # Substrate Type: Gap-inv to simulate barrier without pre-adaptation


# Substrate Parameters
SUBSTRATE_TYPE = "substrate_type"               # Enum to decide which substrate type to use
ROWS = "rows"                                   # Number of rows of substrate
COLS = "cols"                                   # Number of columns of substrate

# Parameters for Saving
FOLDER_PATH = "folder_path"                     # Folder path to save results to
FOLDER_NAME = "folder_name"                     # Folder name to save results to
SHOW_FIGURES = "show_figures"                   # Toggle to show figures directly in addition to saving
INTERIM_RESULTS = "interim_results"             # List of steps where projection-visualization should be created

# -----------   Continuous  -----------
CONT_GRAD_R_DECAY = "continuous_receptor_decay" # Decay of exponential receptor gradient of continuous substrate
CONT_GRAD_L_DECAY = "continuous_ligand_decay"   # Decay of exponential ligand gradient of continuous substrate
CONT_GRAD_R_FACTOR = "cont_grad_r_factor"       # Factor to move whole receptor gradient of cont substrate up or down
CONT_GRAD_L_FACTOR = "cont_grad_l_factor"       # Factor to move whole ligand gradient of cont substrate up or down
CONT_GRAD_R_SHIFT = "cont_grad_r_shift"         # Shift receptor gradient of substrate
CONT_GRAD_L_SHIFT = "cont_grad_l_shift"         # Shift ligand gradient of substrate
SUBSTRATE_SCOPE = "substrate_scope"             # Enum to decide if whole, nasal, temporal part of gradient is used
# -----------   Wedges  -----------
WEDGE_NARROW_EDGE = "wedge_narrow_edge"         # Minimal width of wedge
WEDGE_WIDE_EDGE = "wedge_wide_edge"             # Maximal width of wedge
# -----------   Stripe Assay  -----------
STRIPE_FWD = "stripe_fwd"                       # Toggle for ligand filled stripes
STRIPE_REW = "stripe_rew"                       # Toggle for receptor filled stripes
STRIPE_LIGAND_CONC = "stripe_ligand_conc"       # Concentration of ligands on stripes
STRIPE_RECEPTOR_CONC = "stripe_receptor_conc"   # Concentration of receptors on stripes
STRIPE_WIDTH = "stripe_width"                   # Width of stripes in units
# -----------   Gap Assay   -----------
GAP_BEGIN = "gap_begin"                         # Fraction of columns where sensor gap begins
GAP_END = "gap_end"                             # Fraction of columns after Gap-begin where sensors start again
GAP_FIRST_BLOCK = "gap_first_block"             # Enum to decide between ligand and receptor on first block
GAP_SECOND_BLOCK = "gap_second_block"           # Enum to decide between ligand and receptor on first block
LIGAND = "ligand"                               # Used for Gap-first-block/second-block
RECEPTOR = "receptor"                           # Used for Gap-first-block/second-block
GAP_FIRST_BLOCK_CONC = "gap_first_block_conc"   # Sensor concentration of first block
GAP_SECOND_BLOCK_CONC = "gap_second_block_conc" # Sensor concentration of second block

"""
--------------------------------------
        CONFIGURATION MODULES
--------------------------------------
"""

# Standard parameters that are used for all substrates including gc params, interaction toggles and params etc
standard_parameters = {
    # gc params
    GC_COUNT: 200,
    GC_SIZE: 2,
    GC_R_DECAY: 0.03,
    GC_L_DECAY: 0.03,
    GC_R_FACTOR: 1,
    GC_L_FACTOR: 1,
    GC_R_SHIFT: 0,
    GC_L_SHIFT: 0,
    KNOCK_IN: 0,
    RHO: 1,
    GC_SCOPE: "full",

    # interaction toggles
    FORWARD_SIG: True,
    REVERSE_SIG: True,
    FF_INTER: True,
    FT_INTER: True,
    CIS_INTER: True,

    # interaction params
    SIGMOID_STEEPNESS: 5,
    SIGMOID_SHIFT: 1.75,
    SIGMOID_HEIGHT: 100,
    CIS_IN_FAC: 10,
    CIS_OUT_FAC: 0.1,

    # adaptation params
    ADAPTATION_ENABLED: True,
    ADAPTATION_MU: 0.005,
    ADAPTATION_LAMBDA: 0.001,
    ADAPTATION_HISTORY: 10,

    # stepping params
    STEP_SIZE: 1,
    STEP_NUM: 8000,
    X_STEP_POSSIBILITY: 0.50,
    Y_STEP_POSSIBILITY: 0.50,
    SIGMA: 0.12,
    FORCE: False,

    # result params
    INTERIM_RESULTS: [1, 100, 500, 1000, 2000, 3000, 4000, 5000, 7500],
    FOLDER_PATH: "",
    FOLDER_NAME: "",
    SHOW_FIGURES: False,
}


# Parameters for specific substrates
continuous_substrate = {
    SUBSTRATE_TYPE: CONTINUOUS_GRADIENTS,
    ROWS: 8,
    COLS: 50,
    CONT_GRAD_R_FACTOR: 1,
    CONT_GRAD_L_FACTOR: 1,
    CONT_GRAD_R_SHIFT: 0,
    CONT_GRAD_L_SHIFT: 0,
    CONT_GRAD_R_DECAY: 0.03,
    CONT_GRAD_L_DECAY: 0.03,
    SUBSTRATE_SCOPE: "full",
}

wedges_substrate = {
    SUBSTRATE_TYPE: WEDGES,
    ROWS: 96,
    COLS: 96,
    WEDGE_NARROW_EDGE: 1,
    WEDGE_WIDE_EDGE: 12
}

stripe_substrate = {
    SUBSTRATE_TYPE: STRIPE,
    ROWS: 100,
    COLS: 100,
    STRIPE_FWD: True,
    STRIPE_REW: True,
    STRIPE_LIGAND_CONC: 1,
    STRIPE_RECEPTOR_CONC: 1,
    STRIPE_WIDTH: 5,
}

gap_substrate = {
    SUBSTRATE_TYPE: GAP,
    ROWS: 200,
    COLS: 200,
    GAP_BEGIN: 0.4,
    GAP_END: 0.075,
    GAP_FIRST_BLOCK: RECEPTOR,
    GAP_SECOND_BLOCK: RECEPTOR,
    GAP_FIRST_BLOCK_CONC: 1,
    GAP_SECOND_BLOCK_CONC: 1,
}

gap_inv_substrate = {
    SUBSTRATE_TYPE: GAP_INV,
    ROWS: 200,
    COLS: 200,
    GAP_BEGIN: 0.4,
    GAP_END: 0.3,
    GAP_FIRST_BLOCK: RECEPTOR,
    GAP_FIRST_BLOCK_CONC: 1,
}
"""
--------------------------------------
        DEFAULT_CONFIGURATIONS
--------------------------------------
"""
normal_mapping_config = {
    **standard_parameters,
    **continuous_substrate
}
single_mapping_config = {
    **standard_parameters,
    **continuous_substrate,
    FF_INTER: False
}

expansion_config = {
    **standard_parameters,
    **continuous_substrate,
    GC_SCOPE: "nasal"
}

compression_config = {
    **standard_parameters,
    **continuous_substrate,
    SUBSTRATE_SCOPE: "anterior",
}

mismatch_config = {
    **standard_parameters,
    **continuous_substrate,
    GC_SCOPE: "nasal",
    SUBSTRATE_SCOPE: "anterior",
    STEP_NUM: 30000
}

knock_in_hom_config = {
    **standard_parameters,
    **continuous_substrate,
    KNOCK_IN: 1
}

knock_in_het_config = {
    **standard_parameters,
    **continuous_substrate,
    KNOCK_IN: 0.5
}

double_stripe_config = {
    **standard_parameters,
    **stripe_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 50,
    INTERIM_RESULTS: [],
}

receptor_stripe_config = {
    **standard_parameters,
    **stripe_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 50,
    STRIPE_FWD: False,
    INTERIM_RESULTS: [],
}

ligand_stripe_config = {
    **standard_parameters,
    **stripe_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 50,
    STRIPE_REW: False,
    INTERIM_RESULTS: [],
}

gap_config = {
    **standard_parameters,
    **gap_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 12,
    INTERIM_RESULTS: [],
}

gap_inv_config = {
    **standard_parameters,
    **gap_inv_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 12,
    INTERIM_RESULTS: [],
}

wedges_config = {
    **standard_parameters,
    **wedges_substrate,
    X_STEP_POSSIBILITY: 0.65,
    SIGMOID_HEIGHT: 1,
    GC_COUNT: 12
}

"""
--------------------------------------
        CUSTOM CONFIGURATION
--------------------------------------
"""

custom_config = {
    # Choose Substrate
    **normal_mapping_config,
    # **stripe_config,
    # **gap_config,
    # **gap_inv_config,
    # **wedges_config,

    # Implement custom changes, by re-declaring keys
}

"""
--------------------------------------
        CURRENT CONFIGURATION
--------------------------------------
"""

current_config = custom_config

"""
-------------------------------------------------
        DEFAULT CONFIGURATIONS FOR WEBAPP
-------------------------------------------------
"""

default_configs = {
    # use this name in to be congruent with frontend
    "CONTINUOUS_GRADIENTS": {
        **normal_mapping_config
    },
    "WEDGES": {
        **wedges_config
    },
    #  use this name to be congruent with frontend
    "STRIPE": {
        **double_stripe_config
    },
    "GAP": {
        **gap_config
    },
    "GAP_INV": {
        **gap_inv_config
    },
    "SINGLE_MAPPING_CONFIG": {
        **single_mapping_config
    },
    "EXPANSION_CONFIG": {
        **expansion_config
    },
    "COMPRESSION_CONFIG": {
        **compression_config
    },
    "MISMATCH_CONFIG": {
        **mismatch_config
    },
    "KNOCK_IN_HOM_CONFIG": {
        **knock_in_hom_config
    },
    "KNOCK_IN_HET_CONFIG": {
        **knock_in_het_config
    },
    "RECEPTOR_STRIPE_CONFIG": {
        **receptor_stripe_config
    },
    "LIGAND_STRIPE_CONFIG": {
        **ligand_stripe_config
    }
}


def get_default_config(experiment_type):
    return default_configs.get(experiment_type.upper(), {})





