# batch.py
import itertools
import subprocess

from build import config as cfg
import main  # assumes main.py has a run() function
from experiments.two_phase import two_phase_experiments

subprocess.run([
    "osascript",
    "-e",
    'tell application "Amphetamine" to enable closed display mode'
])  # :contentReference[oaicite:0]{index=0}

subprocess.run([
    "osascript",
    "-e",
    'tell application "Amphetamine" to start new session with options {displaySleepAllowed:false}'
])  # :contentReference[oaicite:0]{index=0}

cfg.current_config[cfg.FOLDER_PATH] = ("Knock_In") # what name should your folder have
# 1) define your sweep
sweeps = {
    cfg.SUBSTRATE_TYPE: [cfg.GAP],
    cfg.CONT_GRAD_R_DECAY: [0.03],
    cfg.CONT_GRAD_L_DECAY: [0.03],
    cfg.GAP_FIRST_BLOCK_CONC: [0],
    cfg.GAP_SECOND_BLOCK_CONC:[5, 7, 10],
    cfg.X_STEP_POSSIBILITY: [0.65],
    cfg.FF_INTER: [False]
}


# 2) cache your “base” config
base = cfg.current_config.copy()
keys, values = zip(*sweeps.items())


selected_combos = [
]


for combo in itertools.product(*values):
    if selected_combos and combo not in selected_combos:
        continue
    # 3) reset to base, then apply this combination
    cfg.current_config = base.copy()
    for k, v in zip(keys, combo):
        cfg.current_config[k] = v

    # 4) build a unique folder-name tag
    combo_tag = "__".join(
        f"{k.split('_')[-1]}={v}" for k, v in zip(keys, combo)
    )
    # store folder name in config
    cfg.current_config[cfg.FOLDER_NAME] = combo_tag

    # 5) run it
    main.run()
    # two_phase_experiments.run()


# 3) Beende die Amphetamine-Session
subprocess.run([
    "osascript",
    "-e",
    'tell application "Amphetamine" to end session'
])  # :contentReference[oaicite:1]{index=1}
