import build.config as cfg
from build import utils
from visualization import utils as vz
from build import object_factory
import csv
import os
import numpy as np
import Visualize_endpoints

ORIENTATIONS = [True, False]                        # “start_posterior” yes / no
SUBSTRATE_TYPES = ["Double", "ephrin-A", "EphA"]    # your three substrates
GC_TYPES = ["nasal", "temporal"]                    # your two growth‐cone types


def endpoint_analysis_run():
    """
    Polarity reversal experiment with two nasal populations as waves that grow onto substrate in sequential order.
    Each row in the CSV will contain all final_x values from one simulation run.
    """

    cfg.current_config = cfg.get_default_config(cfg.GAP)

    cfg.current_config[cfg.FOLDER_PATH] = "exp0033-1_8k_new"
    cfg.current_config[cfg.FOLDER_NAME] = "files"
    cfg.current_config[cfg.GC_COUNT] = 13 # use odd number!
    cfg.current_config[cfg.STEP_NUM] = 8000
    cfg.current_config[cfg.X_STEP_POSSIBILITY] = 0.5

    file_path = utils.create_simulation_folder()
    base_path = os.path.abspath(os.path.join(file_path, os.pardir))
    csv_path = os.path.join(file_path, "all_final_positions.csv")

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        header = ["substrate_type", "gc_type", "start_posterior", "run_id"]
        header += [f"cone_{i}" for i in range(cfg.current_config[cfg.GC_COUNT])]
        writer.writerow(header)
        for substrate_type in SUBSTRATE_TYPES:
            for gc_type in GC_TYPES:
                for start_posterior in ORIENTATIONS:
                    start = "p → a" if start_posterior else "a → p"
                    cfg.current_config[cfg.FOLDER_PATH] = base_path
                    cfg.current_config[cfg.FOLDER_NAME] = f"images_{substrate_type}_{gc_type}_{start}"
                    utils.create_simulation_folder()

                    for i in range(3):  # Run Simulation 10 times
                        simulation = object_factory.build_default()
                        color = manipulate_gcs(simulation.growth_cones, gc_type, start_posterior)
                        manipulate_substrate(simulation.substrate, substrate_type)

                        result = simulation.run()

                        if i == 0:
                            vz.visualize_start_values(simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))
                            # Will plot trajectories with blue once -> just ignore it for the moment
                            vz.visualize_results(result, simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))
                        vz.plot_trajectories(result, simulation.growth_cones, gc_color=color,
                                             show=cfg.current_config.get(cfg.SHOW_FIGURES))

                        final_xs, final_ys = result.get_final_positioning()
                        xs = []
                        for x in final_xs:
                            x = (x - 2) / 2
                            xs.append(x)
                        writer.writerow([substrate_type, gc_type, start, i + 1] + xs)

    utils.write_config_to_text(file_path)
    Visualize_endpoints.make_boxplots(csv_path, base_path)


def manipulate_gcs(gcs, gc_type, start_posterior=False):
    gc_num = 0
    if gc_type == "nasal":
        gc_num = int(cfg.current_config[cfg.GC_COUNT] * 0.25)
    elif gc_type == "temporal":
        gc_num = int(cfg.current_config[cfg.GC_COUNT] * 0.75)

    ligand = gcs[gc_num].ligand
    receptor = gcs[gc_num].receptor
    for gc in gcs:
        gc.ligand = gc.outer_ligand_current = ligand
        gc.receptor = gc.outer_receptor_current = receptor
        if start_posterior:
            old_x, old_y = gc.pos
            gc.pos = (int(gc.radius + cfg.current_config[cfg.COLS] - 1), old_y)
            gc.history.position[0] = gc.pos

    if gc_type == "nasal":
        return 'red'
    elif gc_type == "temporal":
        return 'blue'


def manipulate_substrate(substrate, type):
    ligand_gradient = np.zeros(substrate.cols)
    receptor_gradient = np.zeros(substrate.cols)
    # linear gradient
    if type == "Double":
        """
        ligand_gradient = np.linspace(0.033, 0.4835, substrate.cols)
        receptor_gradient = np.linspace(0.4835, 0.033, substrate.cols)
        """
        receptor_gradient = np.linspace(1, 0, substrate.cols) ** 2
        receptor_gradient = 0.033 + receptor_gradient * (1 - 0.033)

        ligand_gradient = np.linspace(0, 1, substrate.cols) ** 2
        ligand_gradient = 0.033 + ligand_gradient * (1 - 0.033)
    elif type == "ephrin-A":
        """
        ligand_gradient = np.linspace(0.033, 0.4835, substrate.cols)
        """

        ligand_gradient = np.linspace(0, 1, substrate.cols) ** 2
        ligand_gradient = 0.033 + ligand_gradient * (1 - 0.033)
    elif type == "EphA":
        """
        receptor_gradient = np.linspace(0.4835, 0.033, substrate.cols)
        """
        receptor_gradient = np.linspace(1, 0, substrate.cols) ** 2
        receptor_gradient = 0.033 + receptor_gradient * (1 - 0.033)

    for row in range(substrate.rows):
        substrate.ligands[row, :] = ligand_gradient
        substrate.receptors[row, :] = receptor_gradient


def run():
    endpoint_analysis_run()


if __name__ == '__main__':
    run()
