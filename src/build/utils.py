import os
import build.config as cfg
import datetime


def create_simulation_folder():
    basedir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir
        )
    )
    results_dir = os.path.join(basedir, "Retinotectal_Simulation_Results")

    # Bereits in der Konfiguration hinterlegten Pfad (relativ) einfügen
    existing_subpath = cfg.current_config.get(cfg.FOLDER_PATH, "")
    target_base = os.path.join(results_dir, existing_subpath)

    if cfg.current_config[cfg.FOLDER_NAME] != "":
        folder_name = cfg.current_config[cfg.FOLDER_NAME]
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"simulation_run_{timestamp}"
    new_folder_path = os.path.join(target_base, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    cfg.current_config[cfg.FOLDER_PATH] = new_folder_path
    return new_folder_path


def write_config_to_text(folder_path):
    file_path = os.path.join(folder_path, "config.txt")
    with open(file_path, 'w') as f:
        for key, value in cfg.current_config.items():
            f.write(f"{key}: {value}\n")


def build_kernel(a, threshold):
    """
    Build unnormalized 2D Gaussian kernel with decay a and threshold cutoff.
    Returns kernel array.
    """
    radius = math.floor(math.sqrt(-math.log(threshold) / a))
    size = 2 * radius + 1
    x_array = np.arange(size) - radius
    y_array = x_array.copy()
    X, Y = np.meshgrid(x_array, y_array, indexing='ij')
    G = np.exp(-a * (X**2 + Y**2))
    G[G < threshold] = 0.0
    return G