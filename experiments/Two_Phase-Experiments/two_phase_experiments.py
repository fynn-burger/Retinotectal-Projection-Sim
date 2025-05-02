import build.config as cfg
from build import object_factory
import visualization as vz
import main

def two_phase_run():
    """
    Polarity reversal experiment with two nasal populations as waves that grow onto substrate in sequential order.
    :return:
    """

    # create for first gcs
    cfg.current_config[cfg.GC_SCOPE] = "full"
    cfg.current_config[cfg.SUBSTRATE_SCOPE] = "full"

    # run simulation with first gcs and freeze them
    simulation_1 = object_factory.build_default()
    vz.visualize_growth_cones(simulation_1.growth_cones).show()
    first_gc_result = simulation_1.run()
    for gc in simulation_1.growth_cones:
        gc.freeze = True
    vz.visualize_projection(first_gc_result, simulation_1.substrate).show()

    # save first gcs for later
    first_gcs = simulation_1.growth_cones

    # specify parameters for second gcs
    cfg.current_config[cfg.GC_SCOPE] = "temporal"
    cfg.current_config[cfg.SUBSTRATE_SCOPE] = "full"
    print(cfg.current_config)

    # run simulation with first (freezed) and second gcs
    simulation_2 = object_factory.build_default()
    vz.visualize_growth_cones(simulation_2.growth_cones).show()
    gcs = first_gcs + simulation_2.growth_cones
    simulation_2.growth_cones = gcs
    second_gc_result = simulation_2.run()
    vz.visualize_projection(second_gc_result, simulation_2.substrate, growth_cones=simulation_2.growth_cones).show()


def run():
    two_phase_run()


if __name__ == '__main__':
    run()
