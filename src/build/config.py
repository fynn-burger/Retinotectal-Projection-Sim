"""
Module providing configuration settings for a retinotectal projection model.
"""

"""
--------------------------------------
        CONFIGURATION KEYS
--------------------------------------
"""

# Simulation Basic Parameters
GC_COUNT = "gc_count"
GC_SIZE = "gc_size"
STEP_SIZE = "step_size"
STEP_NUM = "step_num"

# Simulation Advanced Parameters
X_STEP_POSSIBILITY = "x_step_possibility"
Y_STEP_POSSIBILITY = "y_step_possibility"
SIGMOID_STEEPNESS = "sigmoid_steepness"
SIGMOID_SHIFT = "sigmoid_shift"
SIGMOID_HEIGHT = "sigmoid_height"
SIGMA = "sigma"
FORCE = "force"
FORWARD_SIG = "forward_sig"
REVERSE_SIG = "reverse_sig"
FF_INTER = "ff_inter"
FT_INTER = "ft_inter"
CIS_INTER = "cis_inter"

# Growth Cones
GC_R_STEEPNESS = "receptor_steepness"
GC_L_STEEPNESS = "ligand_steepness"
GC_R_MIN = "receptor_min"
GC_L_MIN = "ligand_min"
GC_R_MAX = "receptor_max"
GC_L_MAX = "ligand_max"
RHO = "rho"

# Adaptation
ADAPTATION_ENABLED = "adaptation_enabled"
ADAPTATION_MU = "adaptation_mu"
ADAPTATION_LAMBDA = "adaptation_lambda"
ADAPTATION_HISTORY = "adaptation_history"

# Substrate Types
CONTINUOUS_GRADIENTS = "continuous_gradients"
WEDGES = "wedges"
STRIPE = "stripe"
GAP = "gap"
GAP_INV = "gap_inv"


# Substrate Parameters
SUBSTRATE_TYPE = "substrate_type"
ROWS = "rows"
COLS = "cols"
# -----------   Continuous  -----------
CONT_GRAD_R_STEEPNESS = "continuous_receptor_steepness"
CONT_GRAD_L_STEEPNESS = "continuous_ligand_steepness"
CONT_GRAD_R_MIN = "continuous_receptor_start"
CONT_GRAD_L_MIN = "continuous_ligand_start"
CONT_GRAD_R_MAX = "continuous_receptor_end"
CONT_GRAD_L_MAX = "continuous_ligand_end"
# -----------   Wedges  -----------
WEDGE_NARROW_EDGE = "wedge_narrow_edge"
WEDGE_WIDE_EDGE = "wedge_wide_edge"
# -----------   Stripe Assay  -----------
STRIPE_FWD = "stripe_fwd"
STRIPE_REW = "stripe_rew"
STRIPE_LIGAND_CONC = "stripe_ligand_conc"
STRIPE_RECEPTOR_CONC = "stripe_receptor_conc"
STRIPE_WIDTH = "stripe_width"
# -----------   Gap Assay   -----------
GAP_BEGIN = "gap_begin"
GAP_END = "gap_end"
LIGAND = "ligand"
RECEPTOR = "receptor"
GAP_FIRST_BLOCK = "gap_first_block"
GAP_SECOND_BLOCK = "gap_second_block"
GAP_FIRST_BLOCK_CONC = "gap_first_block_conc"
GAP_SECOND_BLOCK_CONC = "gap_second_block_conc"

"""
--------------------------------------
        CONFIGURATION MODULES
--------------------------------------
"""

simulation_basic = {
    GC_COUNT: 20,
    GC_SIZE: 3,
    STEP_SIZE: 1,
    STEP_NUM: 8000,
}

simulation_advanced = {
    X_STEP_POSSIBILITY: 0.55,
    Y_STEP_POSSIBILITY: 0.50,
    SIGMOID_STEEPNESS: 4,
    SIGMOID_SHIFT: 3,
    SIGMOID_HEIGHT: 1,
    SIGMA: 0.06,
    FORCE: False,
    FORWARD_SIG: True,
    REVERSE_SIG: True,
    FF_INTER: True,
    FT_INTER: True
}

adaptation = {
    ADAPTATION_ENABLED: True,
    ADAPTATION_MU: 0.01,
    ADAPTATION_LAMBDA: 0.0045,
    ADAPTATION_HISTORY: 50
}

# Substrates

continuous_substrate = {
    SUBSTRATE_TYPE: CONTINUOUS_GRADIENTS,
    ROWS: 100,
    COLS: 100,
    CONT_GRAD_R_MIN: 0.01,
    CONT_GRAD_L_MIN: 0.01,
    CONT_GRAD_R_MAX: 1,
    CONT_GRAD_L_MAX: 1,
    CONT_GRAD_R_STEEPNESS: 1,
    CONT_GRAD_L_STEEPNESS: 1,

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
    ROWS: 150,
    COLS: 150,
    STRIPE_FWD: True,
    STRIPE_REW: True,
    STRIPE_LIGAND_CONC: 1,
    STRIPE_RECEPTOR_CONC: 1,
    STRIPE_WIDTH: 12
}

gap_substrate = {
    SUBSTRATE_TYPE: GAP,
    ROWS: 96,
    COLS: 96,
    GAP_BEGIN: 0.5,
    GAP_END: 0.1,
    GAP_FIRST_BLOCK: LIGAND,
    GAP_SECOND_BLOCK: RECEPTOR,
    GAP_FIRST_BLOCK_CONC: 1,
    GAP_SECOND_BLOCK_CONC: 1,
}

gap_inv_substrate = {
    SUBSTRATE_TYPE: GAP_INV,
    ROWS: 46,
    COLS: 166,
    GAP_BEGIN: 0.4,
    GAP_END: 0.3,
    GAP_FIRST_BLOCK: RECEPTOR,
    GAP_FIRST_BLOCK_CONC: 1
}

"""
--------------------------------------
        DEFAULT CONFIGURATIONS
--------------------------------------
"""

default_configs = {
    "CONTINUOUS_GRADIENTS": {
        GC_COUNT: 15,  # 100
        GC_SIZE: 3,
        STEP_SIZE: 1,
        STEP_NUM: 5000,  # 8000
        GC_R_STEEPNESS: 1.5,
        GC_L_STEEPNESS: 1.5,
        GC_R_MIN: 0.01,
        GC_L_MIN: 0.01,
        GC_R_MAX: 2.99,
        GC_L_MAX: 2.99,
        RHO: 1,
        X_STEP_POSSIBILITY: 0.55,
        Y_STEP_POSSIBILITY: 0.50,
        SIGMOID_STEEPNESS: 4,
        SIGMOID_SHIFT: 3,
        SIGMOID_HEIGHT: 1,
        SIGMA: 0.06,
        FORCE: False,
        FORWARD_SIG: True,
        REVERSE_SIG: True,
        FF_INTER: True,
        FT_INTER: True,
        CIS_INTER: True,
        ADAPTATION_ENABLED: True,
        ADAPTATION_MU: 0.01,
        ADAPTATION_LAMBDA: 0.0045,
        ADAPTATION_HISTORY: 50,
        SUBSTRATE_TYPE: CONTINUOUS_GRADIENTS,
        ROWS: 100,
        COLS: 100,
        CONT_GRAD_R_MIN: 0.01,
        CONT_GRAD_L_MIN: 0.01,
        CONT_GRAD_R_MAX: 0.99,
        CONT_GRAD_L_MAX: 0.99,
        CONT_GRAD_R_STEEPNESS: 1.4,
        CONT_GRAD_L_STEEPNESS: 1.4
    },
    "WEDGES": {
        GC_COUNT: 10,
        GC_SIZE: 10,
        STEP_SIZE: 1,
        STEP_NUM: 8000,
        GC_R_STEEPNESS: 1.5,
        GC_L_STEEPNESS: 1.5,
        GC_R_MIN: 0.01,
        GC_L_MIN: 0.01,
        GC_R_MAX: 2.99,
        GC_L_MAX: 2.99,
        RHO: 1,
        X_STEP_POSSIBILITY: 0.55,
        Y_STEP_POSSIBILITY: 0.50,
        SIGMOID_STEEPNESS: 4,
        SIGMOID_SHIFT: 3,
        SIGMOID_HEIGHT: 1,
        SIGMA: 0.06,
        FORCE: False,
        FORWARD_SIG: True,
        REVERSE_SIG: True,
        FF_INTER: True,
        FT_INTER: True,
        CIS_INTER: True,
        ADAPTATION_ENABLED: False,
        SUBSTRATE_TYPE: WEDGES,
        ROWS: 96,
        COLS: 96,
        WEDGE_NARROW_EDGE: 1,
        WEDGE_WIDE_EDGE: 12
    },
    "STRIPE": {
        GC_COUNT: 10,
        GC_SIZE: 10,
        STEP_SIZE: 1,
        STEP_NUM: 8000,
        GC_R_STEEPNESS: 1.5,
        GC_L_STEEPNESS: 1.5,
        GC_R_MIN: 0.01,
        GC_L_MIN: 0.01,
        GC_R_MAX: 2.99,
        GC_L_MAX: 2.99,
        RHO: 1,
        X_STEP_POSSIBILITY: 0.55,
        Y_STEP_POSSIBILITY: 0.50,
        SIGMOID_STEEPNESS: 4,
        SIGMOID_SHIFT: 3,
        SIGMOID_HEIGHT: 1,
        SIGMA: 0.06,
        FORCE: False,
        FORWARD_SIG: True,
        REVERSE_SIG: True,
        FF_INTER: True,
        FT_INTER: True,
        CIS_INTER: True,
        ADAPTATION_ENABLED: False,
        SUBSTRATE_TYPE: STRIPE,
        ROWS: 150,
        COLS: 150,
        STRIPE_FWD: True,
        STRIPE_REW: True,
        STRIPE_LIGAND_CONC: 1,
        STRIPE_RECEPTOR_CONC: 1,
        STRIPE_WIDTH: 12
    },
    "GAP": {
        GC_COUNT: 5,
        GC_SIZE: 5,
        STEP_SIZE: 2,
        STEP_NUM: 8000,
        GC_R_STEEPNESS: 1.5,
        GC_L_STEEPNESS: 1.5,
        GC_R_MIN: 0.01,
        GC_L_MIN: 0.01,
        GC_R_MAX: 2.99,
        GC_L_MAX: 2.99,
        RHO: 1,
        X_STEP_POSSIBILITY: 0.55,
        Y_STEP_POSSIBILITY: 0.50,
        SIGMOID_STEEPNESS: 4,
        SIGMOID_SHIFT: 3,
        SIGMOID_HEIGHT: 1,
        SIGMA: 0.06,
        FORCE: False,
        FORWARD_SIG: True,
        REVERSE_SIG: True,
        FF_INTER: True,
        FT_INTER: True,
        CIS_INTER: True,
        ADAPTATION_ENABLED: True,
        ADAPTATION_MU: 0.01,
        ADAPTATION_LAMBDA: 0.0045,
        ADAPTATION_HISTORY: 50,
        SUBSTRATE_TYPE: GAP,
        ROWS: 96,
        COLS: 96,
        GAP_BEGIN: 0.5,
        GAP_END: 0.1,
        GAP_FIRST_BLOCK: LIGAND,
        GAP_SECOND_BLOCK: RECEPTOR,
        GAP_FIRST_BLOCK_CONC: 1,
        GAP_SECOND_BLOCK_CONC: 1
    },
}


def get_default_config(substrate_type):
    return default_configs.get(substrate_type.upper(), {})


"""
--------------------------------------
        CUSTOM CONFIGURATION
--------------------------------------
"""

custom_config = {
    GC_COUNT: 20,
    GC_SIZE: 3,
    STEP_SIZE: 1,
    STEP_NUM: 4000,
    X_STEP_POSSIBILITY: 0.55,
    Y_STEP_POSSIBILITY: 0.50,
    SIGMOID_STEEPNESS: 4,
    SIGMOID_SHIFT: 3,
    SIGMOID_HEIGHT: 1,
    GC_R_STEEPNESS: 1.4,
    GC_L_STEEPNESS: 1.4,
    GC_R_MIN: 0.01,
    GC_L_MIN: 0.01,
    GC_R_MAX: 1,
    GC_L_MAX: 1,
    RHO: 1,
    SIGMA: 0.12,
    FORCE: False,
    FORWARD_SIG: True,
    REVERSE_SIG: True,
    FF_INTER: False,
    FT_INTER: True,
    CIS_INTER: True,
    ADAPTATION_ENABLED: True,
    ADAPTATION_MU: 0.096,  # 0,006
    ADAPTATION_LAMBDA: 0.0008,  # 0.0045
    ADAPTATION_HISTORY: 10,
    SUBSTRATE_TYPE: STRIPE,
    ROWS: 100,
    COLS: 100,

    # Continuous substrate values
    CONT_GRAD_R_STEEPNESS: 1.4,
    CONT_GRAD_L_STEEPNESS: 1.4,
    CONT_GRAD_R_MIN: 0.27,
    CONT_GRAD_L_MIN: 0.27,
    CONT_GRAD_R_MAX: 27,
    CONT_GRAD_L_MAX: 27,

    # Stripe substrate values
    STRIPE_FWD: True,
    STRIPE_REW: False,
    STRIPE_LIGAND_CONC: 0.7,
    STRIPE_RECEPTOR_CONC: 0.7,
    STRIPE_WIDTH: 6.625,

    # Gap substrate Values
    GAP_BEGIN: 0.6,
    GAP_END: 0.06,
    GAP_FIRST_BLOCK: RECEPTOR,
    GAP_SECOND_BLOCK: RECEPTOR,
    GAP_FIRST_BLOCK_CONC: 0.001,
    GAP_SECOND_BLOCK_CONC: 0.1
}

"""
--------------------------------------
        CURRENT CONFIGURATION
--------------------------------------
"""

current_config = custom_config




