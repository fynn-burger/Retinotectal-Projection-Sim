from build import object_factory
from build import config as cfg
from build import utils
from visualization import utils as vz



def run():
    folder_path = utils.create_simulation_folder()
    utils.write_config_to_text(folder_path)

    simulation = object_factory.build_default()

    vz.visualize_start_values(simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))

    result = simulation.run()

    vz.visualize_results(result, simulation, show=cfg.current_config.get(cfg.SHOW_FIGURES))


if __name__ == '__main__':
    run()



