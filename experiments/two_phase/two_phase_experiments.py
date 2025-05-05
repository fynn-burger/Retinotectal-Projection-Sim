import build.config as cfg
from build import object_factory
from visualization import utils as vz
from build import utils


def run():
    """
    Polarity reversal experiment with two nasal populations as waves that grow onto substrate in sequential order.
    :return:
    """
    folder_path = utils.create_simulation_folder()
    utils.write_config_to_text(folder_path)

    # create config for first gcs
    cfg.current_config[cfg.GC_SCOPE] = "full"
    cfg.current_config[cfg.SUBSTRATE_SCOPE] = "full"
    cfg.current_config[cfg.FF_INTER] = False
    cfg.current_config[cfg.INTERIM_RESULTS] = []

    # run simulation with first gcs and freeze them
    simulation_1 = object_factory.build_default()
    vz.plot_growth_cones(simulation_1.growth_cones, cfg.current_config.get(cfg.SHOW_FIGURES))
    first_gc_result = simulation_1.run()
    for gc in simulation_1.growth_cones:
        gc.freeze = True
    # for polarity reversal, delete temporal gcs
    gc_len = int(len(simulation_1.growth_cones) / 2)
    first_gcs = simulation_1.growth_cones[0:gc_len]
    vz.plot_projection(first_gc_result, simulation_1.substrate, first_gcs,
                       cfg.current_config.get(cfg.SHOW_FIGURES))


    # specify parameters for second gcs
    cfg.current_config[cfg.GC_SCOPE] = "nasal"
    cfg.current_config[cfg.SUBSTRATE_SCOPE] = "full"
    cfg.current_config[cfg.FF_INTER] = True
    cfg.current_config[cfg.INTERIM_RESULTS] = [1000, 2000, 3000, 4000]

    # run simulation with first (freezed) and second gcs
    simulation_2 = object_factory.build_default()
    vz.plot_growth_cones(simulation_2.growth_cones, cfg.current_config.get(cfg.SHOW_FIGURES))
    gcs = first_gcs + simulation_2.growth_cones # for expansion!
    simulation_2.growth_cones = gcs
    # change GC_SCOPE after building simulation such that visualization shows a full tectum -> only for expansion!
    # cfg.current_config[cfg.GC_SCOPE] = "full"
    second_gc_result = simulation_2.run()
    vz.plot_projection(second_gc_result, simulation_2.substrate, simulation_2.growth_cones,
                       cfg.current_config.get(cfg.SHOW_FIGURES))
    vz.plot_adaptation_metrics(simulation_2.growth_cones, cfg.current_config.get(cfg.SHOW_FIGURES))
    vz.plot_receptor_adaptation(simulation_2.growth_cones, cfg.current_config.get(cfg.SHOW_FIGURES))

if __name__ == '__main__':
    run()
