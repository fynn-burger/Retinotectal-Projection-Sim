# batch.py
import itertools
import subprocess

from build import config as cfg, object_factory
import main  # assumes main.py has a run() function

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

cfg.current_config[cfg.FOLDER_PATH] = "Compression_Sigmoid_Height_Test" # what name should your folder have
# 1) define your sweep
sweeps = {
    cfg.SIGMOID_HEIGHT: [3000, 6000, 30000],
    cfg.SUBSTRATE_SCOPE: ["anterior"]
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
    main.run()


# 3) Beende die Amphetamine-Session
subprocess.run([
    "osascript",
    "-e",
    'tell application "Amphetamine" to end session'
])  # :contentReference[oaicite:1]{index=1}
