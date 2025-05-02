import os
from visualization import visualizations as vz
from build import config as cfg


def save_and_show(fig, path: str, show: bool = True):
    """Save figure to disk and optionally display it."""
    fig.savefig(path)
    if show:
        fig.show()


def plot_growth_cones(cones, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "growth_cones.png")
    fig = vz.visualize_growth_cones(cones)
    save_and_show(fig, path, show)
    return fig


def plot_substrate(substrate, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "substrate.png")
    fig = vz.visualize_substrate(substrate)
    save_and_show(fig, path, show)
    return fig


def plot_substrate_separate(substrate, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "substrate_separate.png")
    fig = vz.visualize_substrate_separately(substrate)
    save_and_show(fig, path, show)
    return fig


def plot_projection(result, substrate, cones, show: bool = True, fit_type: str = "linear", current_step: int = 0):
    # choose filename based on fit type
    filename = "projection.png" if fit_type == "linear" else f"projection_{fit_type}.png"
    if current_step in cfg.current_config.get(cfg.INTERIM_RESULTS):
        filename = f"projection_step{current_step}.png"
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), filename)
    fig = vz.visualize_projection(
        result,
        substrate,
        fit_type=fit_type,
        gc_scope=cfg.current_config.get(cfg.GC_SCOPE),
        substrate_scope=cfg.current_config.get(cfg.SUBSTRATE_SCOPE),
        growth_cones=cones
    )
    save_and_show(fig, path, show)
    return fig


def plot_results_on_substrate(result, substrate, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "results_on_substrate.png")
    fig = vz.visualize_results_on_substrate(result, substrate)
    save_and_show(fig, path, show)
    return fig


def plot_trajectories_on_substrate(result, substrate, cones, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "trajectories_on_substrate.png")
    fig = vz.visualize_trajectory_on_substrate(result, substrate, cones)
    save_and_show(fig, path, show)
    return fig


def plot_trajectories(cones, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "trajectories.png")
    fig = vz.visualize_trajectories(cones)
    save_and_show(fig, path, show)
    return fig


def plot_adaptation_metrics(cones, show: bool = True):
    path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "adaptation_metrics.png")
    fig = vz.visualize_adaptation_metrics(cones)
    save_and_show(fig, path, show)
    return fig


def plot_receptor_adaptation(cones, show: bool = True):
    outer_path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "outer_receptors.png")
    inner_path = os.path.join(cfg.current_config.get(cfg.FOLDER_PATH), "inner_receptors.png")
    fig_outer, fig_inner = vz.visualize_receptor_adaptation(cones)
    save_and_show(fig_outer, outer_path, show)
    save_and_show(fig_inner, inner_path, show)
    return fig_outer, fig_inner
