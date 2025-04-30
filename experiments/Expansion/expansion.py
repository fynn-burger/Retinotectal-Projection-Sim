from build.config import SUBSTRATE_TYPE, CONTINUOUS_GRADIENTS, GC_L_DECAY, GC_R_DECAY, ROWS, COLS, GC_COUNT, \
    GC_SIZE, STEP_SIZE, GC_R_FACTOR, GC_R_SHIFT, GC_L_FACTOR, GC_L_SHIFT, RHO, \
    STEP_NUM, X_STEP_POSSIBILITY, Y_STEP_POSSIBILITY, SIGMA, FORCE, ADAPTATION_ENABLED, ADAPTATION_MU, SIGMOID_SHIFT, \
    ADAPTATION_LAMBDA, ADAPTATION_HISTORY, SIGMOID_STEEPNESS, FORWARD_SIG, REVERSE_SIG, FF_INTER, FT_INTER,  \
    CIS_INTER, SIGMOID_HEIGHT, INTERIM_RESULTS, CONT_GRAD_L_DECAY, CONT_GRAD_R_DECAY, CONT_GRAD_L_FACTOR, \
    CONT_GRAD_R_FACTOR, CONT_GRAD_R_SHIFT, CONT_GRAD_L_SHIFT, GC_SCOPE, SUBSTRATE_SCOPE
from build import object_factory
import visualization as vz
import numpy as np

expansion_config = {
    # GC Parameters
    GC_COUNT: 200,  # use double the gcs you want
    GC_SIZE: 2,
    GC_R_DECAY: 0.1,
    GC_L_DECAY: 0.1,
    GC_R_FACTOR: 1,
    GC_L_FACTOR: 1,
    GC_R_SHIFT: 0,
    GC_L_SHIFT: 0,
    RHO: 0.7,
    GC_SCOPE: "full",

    # Interaction Toggles
    FORWARD_SIG: True,
    REVERSE_SIG: True,
    FF_INTER: False,
    FT_INTER: True,
    CIS_INTER: True,

    # Interaction Parameters
    SIGMOID_STEEPNESS: 4,
    SIGMOID_SHIFT: 1.75,
    SIGMOID_HEIGHT: 50,

    # Adaptation
    ADAPTATION_ENABLED: False,
    ADAPTATION_MU: 0.1,
    ADAPTATION_LAMBDA: 0.001,
    ADAPTATION_HISTORY: 10,

    # Step Parameters
    STEP_SIZE: 1,
    STEP_NUM: 5000,
    X_STEP_POSSIBILITY: 0.50,
    Y_STEP_POSSIBILITY: 0.50,
    SIGMA: 0.08,
    FORCE: False,

    INTERIM_RESULTS: [i for i in range(1000, 5000, 1000)],

    # Substrate Basics
    SUBSTRATE_TYPE: CONTINUOUS_GRADIENTS,
    ROWS: 8,
    COLS: 50,

    # Continuous substrate values
    CONT_GRAD_R_DECAY: 0.1,
    CONT_GRAD_L_DECAY: 0.1,
    CONT_GRAD_R_FACTOR: 2,
    CONT_GRAD_L_FACTOR: 2,
    CONT_GRAD_R_SHIFT: 0,
    CONT_GRAD_L_SHIFT: 0,
    SUBSTRATE_SCOPE: "full"

}


def create_gradient(type, simulation):
    gc_len = int(len(simulation.growth_cones))
    half_len = int(gc_len / 2)
    if type == "nasal":
        freeze_gcs = simulation.growth_cones[half_len:gc_len]
        good_gcs = simulation.growth_cones[0:half_len]
    elif type == "temporal":
        freeze_gcs = simulation.growth_cones[0:half_len]
        good_gcs = simulation.growth_cones[half_len:gc_len]
    elif type == "full":
        freeze_gcs = []
        good_gcs = simulation.growth_cones
    else:
        raise Exception("Unknown half gradient type")
    for gc in freeze_gcs:
        gc.freeze = True
    simulation.growth_cones = good_gcs # only use "good gcs for simulation"
    vz.visualize_growth_cones(simulation.growth_cones).show()
    return simulation

def create_substrate(type, simulation):
    if type == "full":
        vz.visualize_substrate(simulation.substrate).show()
        return simulation
    cols = (int((simulation.substrate.cols - simulation.substrate.offset*2)/2)
                                 + 2*simulation.substrate.offset)
    simulation.substrate.cols = cols
    if type == "anterior":
        ligand_gradient = simulation.substrate.ligands[0][:cols]
        receptor_gradient = simulation.substrate.receptors[0][:cols]
    elif type == "posterior":
        ligand_gradient = simulation.substrate.ligands[0][(cols - simulation.substrate.offset*2):]
        receptor_gradient = simulation.substrate.receptors[0][(cols - simulation.substrate.offset*2):]
    else:
        raise Exception("Unknown substrate type")

    new_ligands = np.empty((simulation.substrate.rows, len(ligand_gradient)))
    new_receptors = np.empty((simulation.substrate.rows, len(receptor_gradient)))
    for row in range(simulation.substrate.rows):
        new_ligands[row, :] = ligand_gradient
        new_receptors[row, :] = receptor_gradient
    simulation.substrate.ligands = new_ligands
    simulation.substrate.receptors = new_receptors


    # visualization is scaled on individual max values so it does not show it correct here
    vz.visualize_substrate(simulation.substrate).show()
    return simulation


def expansion():
    simulation = object_factory.build_simulation(expansion_config)
    simulation = create_gradient(simulation.gc_scope, simulation)
    simulation = create_substrate(simulation.substrate_scope, simulation)
    result = simulation.run()
    vz.visualize_projection(result, simulation.substrate, gc_scope=simulation.gc_scope,
                            substrate_scope=simulation.substrate_scope).show()
    vz.visualize_results_on_substrate(result, simulation.substrate).show()
    vz.visualize_trajectory_on_substrate(result, simulation.substrate, simulation.growth_cones).show()
    vz.visualize_trajectories(simulation.growth_cones).show()
    vz.visualize_adaptation_metrics(simulation.growth_cones).show()
    outer, inner = vz.visualize_receptor_adaptation(simulation.growth_cones)
    outer.show()
    inner.show()

def run():
    expansion()


if __name__ == '__main__':
    run()
