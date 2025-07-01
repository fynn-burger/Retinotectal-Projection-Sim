import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os

def make_boxplots(csv_path: str, out_dir: str=None, y_limit=(0, 100)):
    """
    Reads the “long” CSV at csv_path, then makes one boxplot per substrate_type.
    Saves PNGs into out_dir (defaults to same folder).
    """
    df = pd.read_csv(csv_path)
    df_long = df.melt(
        id_vars=["substrate_type", "gc_type", "start_from_top", "run_id"],
        value_vars=[c for c in df.columns if c.startswith("cone_")],
        var_name="cone_index", value_name="value"
    )

    # ——— NEW: compute one median per run ———
    df_medians = (
        df_long
        .groupby(["substrate_type","gc_type","start_from_top","run_id"], as_index=False)
        .value
        .median()
        .rename(columns={"value": "median_value"})
    )

    if out_dir is None:
        out_dir = os.path.dirname(csv_path)
    os.makedirs(out_dir, exist_ok=True)

    sns.set(style="whitegrid")
    for stype, subdf in df_medians.groupby("substrate_type"):
        # ——— create a figure+axes ———
        fig, ax = plt.subplots(figsize=(6, 4))

        # ——— draw the boxplot ———
        sns.boxplot(
            data=subdf,
            x="start_from_top",
            y="median_value",
            hue="gc_type",
            palette="Set1",
            ax=ax
        )
        ax.set_ylim(*y_limit)
        fig.suptitle(f"Substrate: {stype}", x=0.5, y=0.94, fontsize=14)
        ax.set_xlabel("")
        ax.set_ylabel("Endpositions on Substrate in %")
        ax.legend(loc="best")

        # ——— carve out only 80% of the figure for tight_layout, so 20% remains on the right ———
        plt.tight_layout(rect=(0, 0, 0.85, 1))
        bbox = ax.get_position()

        # ——— inset into that right‐hand 20% (all coords in figure space) ———
        inset = inset_axes(
            ax,
            width="100%",    # fill the 20% strip
            height="100%",
            bbox_to_anchor=(0.87, bbox.y0, 0.16, bbox.height),  # x0, y0, w, h in fig coords
            bbox_transform=fig.transFigure,
            loc="lower left",
            borderpad=0
        )
        inset.axis("off")

        # ——— draw your gradient triangles as before ———
        if stype == "Double":
            coords_red  = [(0.0, 0.0), (0.5, 0.0), (0.0, 1.0)]
            coords_blue = [(0.05, 1.0), (0.55, 1.0), (0.55, 0.0)]
            inset.add_patch(Polygon(coords_red,  closed=True,
                                    transform=inset.transAxes,
                                    color="red",   alpha=0.3))
            inset.add_patch(Polygon(coords_blue, closed=True,
                                    transform=inset.transAxes,
                                    color="blue",  alpha=0.3))

        elif stype == "ephrin-A":
            coords = [(0.0, 0.0), (0.0, 1.0), (0.5, 1.0)]
            inset.add_patch(Polygon(coords, closed=True,
                                    transform=inset.transAxes,
                                    color="red", alpha=0.3))

        elif stype == "EphA":
            coords = [(0.0, 0.0), (0.0, 1.0), (0.5, 1.0)]
            inset.add_patch(Polygon(coords, closed=True,
                                    transform=inset.transAxes,
                                    color="blue", alpha=0.3))

        # ——— save and clean up ———
        fn = os.path.join(out_dir, f"boxplot_{stype}.png")
        fig.savefig(fn, dpi=300)
        plt.close(fig)