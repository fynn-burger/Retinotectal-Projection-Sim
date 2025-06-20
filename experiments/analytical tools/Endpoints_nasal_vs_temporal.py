import build.config as cfg
from build import utils
from visualization import utils as vz
from build import object_factory
import csv
import os


def endpoint_analysis_run():
    """
    Polarity reversal experiment with two nasal populations as waves that grow onto substrate in sequential order.
    Each row in the CSV will contain all final_x values from one simulation run.
    """
    cfg.current_config[cfg.FOLDER_PATH] = "Analysis of Endpoints"
    cfg.current_config[cfg.FOLDER_NAME] = "nasals on double from bottom with one thirtieth gradient"
    cfg.current_config[cfg.STEP_NUM] = 30000
    cfg.current_config[cfg.SIGMOID_HEIGHT] = 1
    cfg.current_config[cfg.GC_COUNT] = 12
    cfg.current_config[cfg.ROWS] = 200
    cfg.current_config[cfg.COLS] = 200
    cfg.current_config[cfg.INTERIM_RESULTS] = []

    folder_path = utils.create_simulation_folder()
    csv_path = os.path.join(folder_path, "final_positions.csv")
    all_values = []

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        for i in range(10):  # Run 3 simulations
            simulation = object_factory.build_default()
            result = simulation.run()

            if i == 0:
                vz.visualize_start_values(simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))
                vz.visualize_results(result, simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))
            else:
                vz.plot_trajectories(result, simulation.growth_cones, show=cfg.current_config.get(cfg.SHOW_FIGURES))

            final_xs, final_ys = result.get_final_positioning()
            writer.writerow(final_xs)  # Write only x values as one row
            for value in final_xs:
                all_values.append(value)
        writer.writerow(all_values)

    utils.write_config_to_text(folder_path)


def run():
    endpoint_analysis_run()


if __name__ == '__main__':
    run()
