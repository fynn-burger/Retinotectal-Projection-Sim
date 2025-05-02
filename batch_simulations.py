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

cfg.current_config[cfg.FOLDER_PATH] = "Polarity_Reversal_1" # what name should your folder have
# 1) define your sweep
sweeps = {
    cfg.SIGMOID_SHIFT: [4.25, 4.5, 4.75]
}


# 2) cache your “base” config
base = cfg.current_config.copy()
keys, values = zip(*sweeps.items())

for combo in itertools.product(*values):
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
    # main.run()
    two_phase_experiments.run()


# 3) Beende die Amphetamine-Session
subprocess.run([
    "osascript",
    "-e",
    'tell application "Amphetamine" to end session'
])  # :contentReference[oaicite:1]{index=1}
