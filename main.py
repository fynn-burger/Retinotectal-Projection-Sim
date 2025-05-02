from build import object_factory
import visualization as vz
import os
import datetime
from build import config as cfg


def run():
    folder_path = create_simulation_folder()
    write_config_to_text(folder_path)

    simulation = object_factory.build_default()

    visualize_start_values(simulation, folder_path)

    result = simulation.run()

    visualize_results(result, simulation, folder_path)

def create_simulation_folder():
    basedir = os.path.abspath(os.path.dirname(__file__))
    results_dir = os.path.join(basedir, "Retinotectal_Simulation_Results")

    # Bereits in der Konfiguration hinterlegten Pfad (relativ) einfügen
    existing_subpath = cfg.current_config.get(cfg.FOLDER_PATH, "")
    target_base = os.path.join(results_dir, existing_subpath)

    if cfg.FOLDER_NAME != "":
        folder_name = cfg.current_config[cfg.FOLDER_NAME]
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"simulation_run_{timestamp}"
    new_folder_path = os.path.join(target_base, folder_name)
    os.makedirs(new_folder_path)
    cfg.current_config[cfg.FOLDER_PATH] = new_folder_path
    return new_folder_path


def write_config_to_text(folder_path):
    file_path = os.path.join(folder_path, "config.txt")
    with open(file_path, 'w') as f:
        for key, value in cfg.current_config.items():
            f.write(f"{key}: {value}\n")

def visualize_start_values(simulation, folder_path):
    gcs = vz.visualize_growth_cones(simulation.growth_cones)
    gcs.savefig(os.path.join(folder_path, "growth_cones.png"))
    gcs.show()

    substrate = vz.visualize_substrate(simulation.substrate)
    substrate.savefig(os.path.join(folder_path, "substrate.png"))
    substrate.show()

    separate_substrates = vz.visualize_substrate_separately(simulation.substrate)
    separate_substrates.savefig(os.path.join(folder_path, "substrate_separate.png"))
    separate_substrates.show()


def visualize_results(result, simulation, folder_path):
    projection = vz.visualize_projection(result, simulation.substrate, gc_scope=cfg.current_config.get(cfg.GC_SCOPE),
                                         substrate_scope=cfg.current_config.get(cfg.SUBSTRATE_SCOPE))
    projection.savefig(os.path.join(folder_path, "projection.png"))
    projection.show()

    results_on_substrate = vz.visualize_results_on_substrate(result, simulation.substrate)
    results_on_substrate.savefig(os.path.join(folder_path, "results_on_substrate.png"))
    results_on_substrate.show()

    trajectories_on_substrate = vz.visualize_trajectory_on_substrate(result, simulation.substrate,
                                                                     simulation.growth_cones)
    trajectories_on_substrate.savefig(os.path.join(folder_path, "trajectories_on_substrate.png"))
    trajectories_on_substrate.show()

    trajectories = vz.visualize_trajectories(simulation.growth_cones)
    trajectories.savefig(os.path.join(folder_path, "trajectories.png"))
    trajectories.show()

    adaptation_metrics = vz.visualize_adaptation_metrics(simulation.growth_cones)
    adaptation_metrics.savefig(os.path.join(folder_path, "adaptation_metrics.png"))
    adaptation_metrics.show()

    outer, inner = vz.visualize_receptor_adaptation(simulation.growth_cones)
    outer.savefig(os.path.join(folder_path, "outer_receptors.png"))
    outer.show()
    inner.savefig(os.path.join(folder_path, "inner_receptors.png"))
    inner.show()


if __name__ == '__main__':
    run()



