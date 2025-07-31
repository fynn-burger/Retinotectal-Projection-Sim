"""
Batch-run simulation experiments with parameter sweeps.

This script will iterate over all SWEEPS combos (or only SELECTED_COMBOS,
if non-empty), set cfg.current_config appropriately, and call sim_module.run().
"""

import itertools

from build import config as cfg
from helpers.prevent_sleep_mac import PreventSleep
import main
from experiments.two_phase import two_phase_experiments

# --- Define parameters you want to test ---
SWEEPS = {
    # Choose at least one sim-module and one experiment
    # Use Continuous gradients when using two-phase experiment
    'sim_module': [main],
    'experiments': [
        # "CONTINUOUS_GRADIENTS",
        # "STRIPE",
        # "GAP",
        # "GAP_INV",
        # "SINGLE_MAPPING_CONFIG",
        # "EXPANSION_CONFIG",
        # "COMPRESSION_CONFIG",
        # "MISMATCH_CONFIG",
        "KNOCK_IN_HOM_CONFIG",
        # "KNOCK_IN_HET_CONFIG",
        # "RECEPTOR_STRIPE_CONFIG",
        # "LIGAND_STRIPE_CONFIG"
    ],
    # --- Type in folder name for results
    cfg.FOLDER_PATH: ["knock_in_new_BA"],
    cfg.FF_INTER: [False]
}

# --- Define specific combination of parameters you want to exclusively test
SELECTED_COMBOS = [
]


def run_batch() -> None:
    """Run multiple simulations with different parameters in one batch.

    Args:
        sim_module: Module with a .run() function.
    """

    keys, values = zip(*SWEEPS.items())

    for combo in itertools.product(*values):
        combo_tag = ""
        if combo not in SELECTED_COMBOS and len(SELECTED_COMBOS) != 0:
            continue
        # Extract sim_module and load it
        idx_mod = keys.index('sim_module')
        sim_module = combo[idx_mod]
        idx_exp = keys.index('experiments')
        experiment = combo[idx_exp]

        if sim_module == two_phase_experiments and experiment != "CONTINUOUS_GRADIENTS":
            continue

        # Extract substrate type and load its default config depending on simulation module
        if sim_module == main:
            cfg.current_config = cfg.get_default_config(experiment).copy()
        elif sim_module == two_phase_experiments:
            combo_tag = "two_phase"
            cfg.current_config = cfg.get_default_config(cfg.CONTINUOUS_GRADIENTS).copy()

        # Apply additional parameters
        for k, v in zip(keys, combo):
            if k == 'experiments' or k == 'sim_module':
                continue
            cfg.current_config[k] = v

        combo_tag += "__".join(
            f"{k.split('_')[-1]}={v}" for k, v in zip(keys, combo) if k != 'sim_module' and k != 'folder_path'
        )
        cfg.current_config[cfg.FOLDER_NAME] = combo_tag
        sim_module.run()


if __name__ == '__main__':
    with PreventSleep():
        run_batch()