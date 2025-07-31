import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os
import numpy as np


def make_boxplots(csv_path: str, out_dir: str=None, y_limit=(0, 100)):
    """
    Reads the “long” CSV at csv_path, then makes one boxplot per substrate_type.
    Saves PNGs into out_dir (defaults to same folder).
    """
    df = pd.read_csv(csv_path)
    df_long = df.melt(
        id_vars=["substrate_type", "gc_type", "start_posterior", "run_id"],
        value_vars=[c for c in df.columns if c.startswith("cone_")],
        var_name="cone_index", value_name="value"
    )

    # ——— NEW: compute one median per run ———
    df_medians = (
        df_long
        .groupby(["substrate_type","gc_type","start_posterior","run_id"], as_index=False)
        .value
        .median()
        .rename(columns={"value": "median_value"})
    )
    df_medians["median_value"] = df_medians["median_value"] * 2

    if out_dir is None:
        out_dir = os.path.dirname(csv_path)
    os.makedirs(out_dir, exist_ok=True)
    N = df_medians['run_id'].nunique()

    all_summaries = []
    for stype, sub in df_medians.groupby("substrate_type"):
        summary = (
            sub
            .groupby(["gc_type", "start_posterior"])["median_value"]
            .describe()[["25%", "50%", "75%"]]
            .rename(columns={"25%": "Q1", "50%": "Median", "75%": "Q3"})
        )
        summary["IQR"] = summary["Q3"] - summary["Q1"]
        summary = summary.reset_index()
        summary["substrate_type"] = stype
        all_summaries.append(summary)

    # concat all and write to one CSV
    df_summary = pd.concat(all_summaries, ignore_index=True)
    out_file = os.path.join(out_dir, "endposition_summaries.csv")
    df_summary.to_csv(out_file, index=False)
    print(f"Wrote summaries to {out_file}")

    sns.set(style="whitegrid")
    for stype, subdf in df_medians.groupby("substrate_type"):
        sub = subdf.copy()

        # 1) build a combined category “gc – start”
        sub['gc_start'] = sub['gc_type'].astype(str) + "\n" + sub['start_posterior'].astype(str)

        # 2) decide the exact sequence you want on the x‐axis:
        gc_levels = sorted(sub['gc_type'].unique())  # e.g. ['highGC','lowGC']
        start_levels = sorted(sub['start_posterior'].unique())  # e.g. [False, True]
        combo_order = [f"{gc}\n{start}" for gc in gc_levels for start in start_levels]
        #          -> ['highGC – False','highGC – True','lowGC – False','lowGC – True']

        # 3) force that order on your new column
        sub['gc_start'] = pd.Categorical(sub['gc_start'],
                                         categories=combo_order,
                                         ordered=True)

        # 4) plot “gc_start” on x, but still hue on the real gc_type
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.set(style="whitegrid")
        sns.boxplot(
            data=sub,
            x="gc_start",
            y="median_value",
            hue="gc_type",
            palette="Set1",
            order=combo_order,
            hue_order=gc_levels,
            legend=False,
            ax=ax,
        )
        ax.tick_params(axis='x', labelsize=16)  # Probe mit 12–18 je nach Bedarf
        ax.tick_params(axis='y', labelsize=16)

        ax.set_ylim(*y_limit)
        ax.set_xlabel("")
        ax.set_ylabel("Endpositions on Substrate in %", fontsize=18)

        # ——— carve out only 80% of the figure for tight_layout, so 20% remains on the right ———
        fig.suptitle(f"Steep Halved {stype} Gradient", fontsize=22, fontweight="bold", y=0.95)
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
        """
        # choose a curvature parameter k (higher → more “bowed”)
        k = 5.0
        # number of points to approximate the exponential curve
        n_pts = 100

        width_factor = 1  # 50% as wide
        x_offset = 0  # shift everything right by 10% of inset width

        if stype == "Double":
            # ===== BLUE =====
            orig_blue_w = 0.5
            new_blue_w = orig_blue_w * width_factor
            xs = np.linspace(new_blue_w, 0.0, n_pts) + x_offset
            us = (new_blue_w - (xs - x_offset)) / new_blue_w
            ys = (np.exp(k * us) - 1) / (np.exp(k) - 1)
            pts_blue = [(0.0 + x_offset, 0.0)] \
                       + list(zip(xs, ys)) \
                       + [(0.0 + x_offset, 1.0)]
            inset.add_patch(Polygon(pts_blue, closed=True,
                                    transform=inset.transAxes,
                                    color="blue", alpha=1))

            # ===== RED =====
            x1 = 0.05 + x_offset
            orig_red_w = 0.55 - 0.05
            new_red_w = orig_red_w * width_factor
            xs_r = np.linspace(x1, x1 + new_red_w, n_pts)
            vs = (xs_r - x1) / new_red_w
            ys_r = 1 - (np.exp(k * vs) - 1) / (np.exp(k) - 1)
            pts_red = [(x1, 1.0)] \
                      + list(zip(xs_r, ys_r)) \
                      + [(x1 + new_red_w, 1.0)]
            inset.add_patch(Polygon(pts_red, closed=True,
                                    transform=inset.transAxes,
                                    color="red", alpha=1))

        elif stype == "ephrin-A":
            x1 = 0.05 + x_offset
            orig_red_w = 0.55 - 0.05
            new_red_w = orig_red_w * width_factor
            xs_r = np.linspace(x1, x1 + new_red_w, n_pts)
            vs = (xs_r - x1) / new_red_w
            ys_r = 1 - (np.exp(k * vs) - 1) / (np.exp(k) - 1)
            pts_red = [(x1, 1.0)] + list(zip(xs_r, ys_r)) + [(x1 + new_red_w, 1.0)]
            inset.add_patch(Polygon(pts_red, closed=True,
                                    transform=inset.transAxes,
                                    color="red", alpha=1))

        elif stype == "EphA":
            orig_blue_w = 0.5
            new_blue_w = orig_blue_w * width_factor
            xs = np.linspace(new_blue_w, 0.0, n_pts) + x_offset
            us = (new_blue_w - (xs - x_offset)) / new_blue_w
            ys = (np.exp(k * us) - 1) / (np.exp(k) - 1)
            pts_blue = [(0.0 + x_offset, 0.0)] \
                       + list(zip(xs, ys)) \
                       + [(0.0 + x_offset, 1.0)]
            inset.add_patch(Polygon(pts_blue, closed=True,
                                    transform=inset.transAxes,
                                    color="blue", alpha=1))


        """
        # ——— draw your gradient triangles as before ———
        if stype == "Double":
            # coords_blue = [(0.075, 0.0), (0.325, 0.0), (0.075, 1.0)]
            # coords_red = [(0.125, 1.0), (0.375, 1.0), (0.375, 0.0)]
            coords_blue = [(0.0, 0.0), (0.5, 0.0), (0.0, 0.5)]
            coords_red = [(0.05, 0.5), (0.55, 0.5), (0.55, 0.0)]
            inset.add_patch(Polygon(coords_red,  closed=True,
                                    transform=inset.transAxes,
                                    color="red",   alpha=1))
            inset.add_patch(Polygon(coords_blue, closed=True,
                                    transform=inset.transAxes,
                                    color="blue",  alpha=1))

        elif stype == "ephrin-A":
            # coords_red = [(0.125, 1.0), (0.375, 1.0), (0.375, 0.0)]
            coords_red = [(0.05, 0.5), (0.55, 0.5), (0.55, 0.0)]
            inset.add_patch(Polygon(coords_red, closed=True,
                                    transform=inset.transAxes,
                                    color="red", alpha=1))

        elif stype == "EphA":
            # coords_blue = [(0.075, 0.0), (0.325, 0.0), (0.075, 1.0)]
            coords_blue = [(0.0, 0.0), (0.5, 0.0), (0.0, 0.5)]
            inset.add_patch(Polygon(coords_blue, closed=True,
                                    transform=inset.transAxes,
                                    color="blue", alpha=1))

        if stype == "ephrin-A":
            # for pure ephrin, e.g. connect mid‑height of triangle out to graph
            x0, y0 = 0.05, 0.5  # triangle’s left‑mid
            x1, y1 = -0.31, 1  # out to the left
            x2, y2 = 0.55, 0.0  # triangle’s right‑mid
            x3, y3 = -0.31, 0.0  # out to the right
        else:
            # default for Double & EphA
            x0, y0 = 0.0, 0.0
            x1, y1 = -0.31, 0.0
            x2, y2 = 0.0, 0.5
            x3, y3 = -0.31, 1.0

        line1 = Line2D(
            [x0, x1],  # replace x0, x1 with your start/end x in inset.transAxes coords
            [y0, y1],  # replace y0, y1 with your start/end y in inset.transAxes coords
            linestyle='--',
            linewidth=2.0,
            color='gray',
            transform=inset.transAxes,
            clip_on=False
        )
        inset.add_line(line1)

        # dotted connector 2
        line2 = Line2D(
            [x2, x3],  # replace x2, x3
            [y2, y3],  # replace y2, y3
            linestyle='--',
            linewidth=2.0,
            color='gray',
            transform=inset.transAxes,
            clip_on = False  # <-- allow it to draw outside the inset box
        )
        inset.add_line(line2)



        # 5) add a little text‐box below the triangles
        counts_text = f"N={N}\nn=13"
        inset.text(
            0.25,  # x‐pos in inset‐axes coords (0–1)
            -0.23,  # y‐pos (just above the bottom)
            counts_text,
            ha="center",  # center horizontally
            va="bottom",  # bottom of text at y=0.05
            transform=inset.transAxes,
            fontsize=16,
        )

        # ——— save and clean up ———
        fn = os.path.join(out_dir, f"boxplot_{stype}_new_1.png")
        fig.savefig(fn, dpi=300)
        plt.close(fig)

base_path = "/Users/fynn_programming/Retinotectal_Results/implement_new_adaptation/1-155_8k_BA"
csv_path = "/Users/fynn_programming/Retinotectal_Results/implement_new_adaptation/1-155_8k_BA/files/all_final_positions.csv"
make_boxplots(csv_path, base_path)


