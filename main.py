from build import object_factory
import os
from build import config as cfg
from build import utils
from visualization import utils as vz



def run():
    folder_path = utils.create_simulation_folder()
    utils.write_config_to_text(folder_path)

    simulation = object_factory.build_default()

    visualize_start_values(simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))

    result = simulation.run()

    visualize_results(result, simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))


def visualize_start_values(simulation, show):
    vz.plot_growth_cones(simulation.growth_cones, show=show)
    vz.plot_substrate(simulation.substrate, show=show)
    vz.plot_substrate_separate(simulation.substrate, show=show)


def visualize_results(result, simulation, show):
    vz.plot_projection(result, simulation.substrate, simulation.growth_cones, show=show)
    vz.plot_results_on_substrate(result, simulation.substrate, show=show)
    vz.plot_trajectories_on_substrate(result, simulation.substrate, simulation.growth_cones, show=show)
    vz.plot_trajectories(simulation.growth_cones, show=show)
    vz.plot_adaptation_metrics(simulation.growth_cones, show=show)
    vz.plot_receptor_adaptation(simulation.growth_cones, show=show)



if __name__ == '__main__':
    run()



