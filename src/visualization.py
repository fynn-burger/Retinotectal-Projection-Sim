import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from matplotlib.figure import Figure
from scipy.stats import linregress
import base64
import io
from model.substrate import ContinuousGradientSubstrate

def get_images_pre(simulation):
    return {
        # Pre-Simulation visualizations
        "growth_cones_pre": generate_image(visualize_growth_cones, simulation.growth_cones),
        "substrate": generate_image(visualize_substrate, simulation.substrate),
        "substrate_separate": generate_image(visualize_substrate_separately, simulation.substrate),
    }


def get_images_post(simulation, result):
    """
    Generates visualizations and encodes them as base64 strings for frontend display.
    """
    return {
        # Post-simulation visualizations
        "growth_cones_post": generate_image(visualize_growth_cones, simulation.growth_cones),
        "projection_linear": generate_image(visualize_projection, result, simulation.substrate),
        "results_on_substrate": generate_image(visualize_results_on_substrate, result,
                                               simulation.substrate),
        "trajectory_on_substrate": generate_image(visualize_trajectory_on_substrate, result,
                                                  simulation.substrate, simulation.growth_cones),
        "trajectories": generate_image(visualize_trajectories, simulation.growth_cones),
        "adaptation": generate_image(visualize_adaptation_1, simulation.growth_cones)

    }


def visualize_image(image, title, rect=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(image)
    ax.set_title(title)
    if rect:
        ax.add_patch(plt.Rectangle(*rect, fill=False, edgecolor='black', lw=2))
    ax.set_ylim(ax.get_ylim()[::-1])  # Flip y-axis
    return fig


def visualize_data_points(x, y, x_label, y_label, title, **kwargs):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(x, y, '*', **kwargs)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    return fig


def visualize_substrate(substrate):
    blended_colors = create_blended_colors(substrate.ligands, substrate.receptors)
    rect = ((substrate.offset - 0.5, substrate.offset - 0.5),
            substrate.cols - 2 * substrate.offset, substrate.rows - 2 * substrate.offset)
    return visualize_image(blended_colors, "Combined Ligands and Receptors", rect)


def visualize_substrate_separately(substrate):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    images = [
        (create_blended_colors(substrate.ligands, np.zeros_like(substrate.ligands)), "Ligands"),
        (create_blended_colors(np.zeros_like(substrate.receptors), substrate.receptors), "Receptors")
    ]
    for ax, (img, title) in zip(axes, images):
        ax.imshow(img)
        ax.set_title(title)
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_xlabel("n-t Axis of Retina")
        ax.set_ylabel("d-v Axis of Retina")
    return fig


def visualize_growth_cones(gcs):
    # ToDo should be the sum of inner and outer receptors -> this does only work if rho = 1
    receptors = np.array([gc.outer_receptor_current for gc in gcs])
    ligands = np.array([gc.outer_ligand_current for gc in gcs])

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(range(len(gcs)), receptors, 'o-', label='Receptors')
    ax.plot(range(len(gcs)), ligands, 'o-', label='Ligands', color='red')

    ax.set_xlabel('Growth Cone ID')
    ax.set_ylabel('Signal Value')
    ax.set_title('Growth Cone Signal Values')
    ax.legend()

    return fig


def visualize_results_on_substrate(result, substrate):
    blended_colors = create_blended_colors(substrate.ligands, substrate.receptors)
    fig = visualize_image(blended_colors, "Tectum End-positions on Color-Mixed Substrate")
    x_values, y_values = result.get_final_positioning()
    plt.plot(x_values, y_values, '*', color='orange', label='Tectum End-positions')
    plt.legend()
    plt.xlabel("n-t Axis of Retina")
    plt.ylabel("d-v Axis of Retina")
    return fig


def visualize_projection(result, substrate, fit_type="linear", gc_scope="full", substrate_scope="full"
                         , mutated_indexes=None):
    # get values
    ap_values, nt_values = result.get_projection_id()
    # normalize values
    ap_values_normalized = normalize_mapping(ap_values, substrate.offset, substrate.cols - substrate.offset - 1)
    nt_values_normalized = normalize_mapping(nt_values, nt_values[0], nt_values[-1])

    # create figure
    fig = visualize_data_points(nt_values_normalized, ap_values_normalized,
                                "% n-t Axis of Retina","% a-p Axis of Target", "Projection Mapping")
    # calculate regression
    try:
        if fit_type == "linear":
            add_linear_regression(nt_values_normalized, ap_values_normalized)
        elif fit_type == "polyfit":
            add_polynomial_fit(nt_values_normalized, ap_values_normalized, mutated_indexes)
    except ValueError as e:
        print("could not calculate linear regression")

    if gc_scope != "full" or substrate_scope != "full" and isinstance(substrate, ContinuousGradientSubstrate):
        create_halved_projection(gc_scope, substrate_scope)

    plt.legend()
    return fig


def add_linear_regression(x, y):
    try:
        slope, intercept, r_value, *_ = linregress(x, y)
        regression_line = slope * x + intercept
        correlation = r_value ** 2  # R² value
        null_point_x = -intercept / slope if slope != 0 else None

        # Plot the regression line
        plt.plot(x, regression_line, 'r-',
                 label=f'Linear Regression\nSlope: {slope:.2f}\n'
                       f'R²: {correlation:.2f}\nNull Point X: {null_point_x:.2f}\nNull Point Y: {intercept:.2f}')

    except (ValueError, TypeError) as e:
        print ("could not calculate linear regression", e)


def add_polynomial_fit(x, y, mutated_indexes):
    coeffs = np.polyfit(x, y, 3)
    poly = np.poly1d(coeffs)
    plt.plot(x, poly(x), 'b-', label="Cubic Fit")


def visualize_trajectories(growth_cones, trajectory_freq=50):
    fig, ax = plt.subplots(figsize=(10, 10))
    for idx, gc in enumerate(growth_cones):
        trajectory_x, trajectory_y = zip(*gc.history.position[::trajectory_freq])
        ax.plot(trajectory_x, trajectory_y, label=f'Growth Cone {idx}')
    ax.set_title('Growth Cone Trajectories')
    # ax.legend()
    plt.xlabel("n-t Axis of Retina")
    plt.ylabel("d-v Axis of Retina")
    return fig


def visualize_trajectory_on_substrate(result, substrate, growth_cones, trajectory_freq=50):
    blended_colors = create_blended_colors(substrate.ligands, substrate.receptors)
    fig = visualize_image(blended_colors, "Tectum End-positions and Growth Cone Trajectories on Substrate")
    x_values, y_values = result.get_final_positioning()
    plt.plot(x_values, y_values, '*', color='orange', label='Tectum End-positions')

    for idx, gc in enumerate(growth_cones):
        trajectory_x, trajectory_y = zip(*gc.history.position[::trajectory_freq])
        plt.plot(trajectory_x, trajectory_y, label=f'Growth Cone {idx}')

    # plt.legend()
    plt.xlabel("n-t Axis of Retina")
    plt.ylabel("d-v Axis of Retina")
    return fig


def visualize_adaptation_metrics(growth_cones):
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    # max_steps = max(len(gc.history.potential) for gc in growth_cones)
    metrics = [
        (axs[0, 0], "Potential", "Guidance Potentials", 'potential', 'linear'),
        (axs[0, 1], "Adaptation Coefficient", "Adaptation Coefficients", 'adap_co', 'linear'),
        (axs[1, 0], "Rho", "Rho", 'rho', 'linear'),
        (axs[1, 1], "Reset Force", "Reset Force", 'reset_force', 'log')
    ]
    for ax, ylabel, title, metric, scale in metrics:
        for gc in growth_cones:
            ax.plot(getattr(gc.history, metric), label=f"Growth Cone {gc.id}")
        ax.set_xlabel('Step')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        #ax.set_xlim(0, max_steps)
        ax.set_yscale(scale)

    plt.tight_layout()
    return fig


def visualize_receptor_adaptation(growth_cones):
    # max_steps = max(len(gc.history.potential) for gc in growth_cones)

    # Outer receptors plot
    fig_outer, ax_outer = plt.subplots(figsize=(12, 6))
    for gc in growth_cones:
        ax_outer.plot(getattr(gc.history, 'outer_receptor'), label=f"Growth Cone {gc.id}")
    ax_outer.set_xlabel('Step')
    ax_outer.set_ylabel('Outer Receptor Level')
    ax_outer.set_title('Outer Receptors')
    # ax_outer.set_xlim(0, max_steps)
    ax_outer.set_yscale('log')  # If you want a logarithmic scale
    #ax_outer.legend()
    plt.tight_layout()

    # Inner receptors plot
    fig_inner, ax_inner = plt.subplots(figsize=(12, 6))
    for gc in growth_cones:
        ax_inner.plot(getattr(gc.history, 'inner_receptor'), label=f"Growth Cone {gc.id}")
    ax_inner.set_xlabel('Step')
    ax_inner.set_ylabel('Inner Receptor Level')
    ax_inner.set_title('Inner Receptors')
    # ax_inner.set_xlim(0, max_steps)
    ax_inner.set_yscale('log')
    #ax_inner.legend()
    plt.tight_layout()

    return fig_outer, fig_inner


def create_blended_colors(ligands, receptors):
    # Normalize ligands and receptors to the range [0, 1] if they exceed 1
    # Normalization changed, such that it normalizes depending on the absolute max value, for both sensor types
    total_max = max(ligands.max(), receptors.max(), 1)

    # Normalize both arrays using the total maximum
    ligands = ligands / total_max
    receptors = receptors / total_max

    blended_colors = np.ones(ligands.shape + (3,))
    blended_colors[..., 0] -= ligands * 0.1 + receptors * 0.9
    blended_colors[..., 1] -= ligands * 0.9 + receptors * 0.6
    blended_colors[..., 2] -= ligands * 0.6 + receptors * 0.1

    # Clip values to ensure they remain in the valid color range [0, 1]
    blended_colors = np.clip(blended_colors, 0, 1)
    return blended_colors


def normalize_mapping(values, min_val, max_val):
    return (values - min_val) / (max_val - min_val) * 100


def _generate_base64_image(figure: Figure) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG image."""
    output = io.BytesIO()
    figure.savefig(output, format='png', transparent=False)
    output.seek(0)
    return base64.b64encode(output.getvalue()).decode('utf8')


def generate_image(visualization_func, *args):
    """
    Generates a visualization with the provided function and encodes it in base64.
    """
    fig = visualization_func(*args)
    return _generate_base64_image(fig)


def create_halved_projection(gc_scope, substrate_scope):
    ax = plt.gca()
    y_min, y_max = ax.get_ylim()
    x_min, x_max = ax.get_xlim()
    if gc_scope == "nasal":
        ax.set_xlim(x_min, x_max * 2)
    elif gc_scope == "temporal":
        ax.set_xlim(- (x_max - x_min), x_max)

    if substrate_scope == "anterior":
        ax.set_ylim(y_min, y_max * 2)
    elif substrate_scope == "posterior":
        ax.set_ylim(- (y_max - y_min), y_max)

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    x_ticks = np.linspace(x_min, x_max, 6)
    y_ticks = np.linspace(y_min, y_max, 6)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    def full_y_range_percentage(x, pos):
        # Linear mapping: x = y_min -> 0%, x = y_max -> 100%
        pct = (x - y_min) / (y_max - y_min) * 100
        return f"{pct:.0f}%"
    def full_x_range_percentage(x, pos):
        # Linear mapping: x = y_min -> 0%, x = y_max -> 100%
        pct = (x - x_min) / (x_max - x_min) * 100
        return f"{pct:.0f}%"

    ax.yaxis.set_major_formatter(mtick.FuncFormatter(full_y_range_percentage))
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(full_x_range_percentage))