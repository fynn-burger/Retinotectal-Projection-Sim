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
    cfg.SUBSTRATE_TYPE: [cfg.GAP],
    cfg.GAP_FIRST_BLOCK_CONC: [0,4],
    cfg.GAP_SECOND_BLOCK_CONC: [4],
    cfg. X_STEP_POSSIBILITY: [0.65],
    #cfg.ADAPTATION_ENABLED: [False],
    cfg.ADAPTATION_LAMBDA: [0.0045],
    cfg.ADAPTATION_MU: [0.006],
    cfg.ADAPTATION_HISTORY: [250]
}

# --- Define specific combination of parameters you want to exclusively test
SELECTED_COMBOS = [
]


def run_batch(sim_module: object) -> None:
    """Run multiple simulations with different parameters in one batch.

    Args:
        sim_module: Module with a .run() function.
    """

    # --- Type in folder name for results
    cfg.current_config[cfg.FOLDER_PATH] = "Test old adaptation formula mirrored on yaxis"

    base = cfg.current_config.copy()
    keys, values = zip(*SWEEPS.items())

    for combo in itertools.product(*values):
        if combo not in SELECTED_COMBOS and len(SELECTED_COMBOS) != 0:
            continue
        cfg.current_config = base.copy()
        for k, v in zip(keys, combo):
            cfg.current_config[k] = v

        combo_tag = "__".join(
            f"{k.split('_')[-1]}={v}" for k, v in zip(keys, combo)
        )
        cfg.current_config[cfg.FOLDER_NAME] = combo_tag

        sim_module.run()


if __name__ == '__main__':
    with PreventSleep():
        run_batch(main)  # at the moment either two_phase_experiments or main
