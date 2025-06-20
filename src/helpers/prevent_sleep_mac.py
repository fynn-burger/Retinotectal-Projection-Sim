"""
Utilities to prevent macOS from sleeping during long-running simulations.

This module defines:

- PreventSleep: Context manager that uses the Amphetamine app via AppleScript
  to inhibit and restore display sleep on macOS.

- prevent_sleep_mac(): Helper to start an Amphetamine session and block sleep.

- let_mac_sleep(): Helper to end the Amphetamine session and re-enable sleep.

If run on non-macOS platforms or without Amphetamine installed, all operations
are no-ops (errors are caught and suppressed).
"""

import subprocess


class PreventSleep:
    """Context manager to inhibit and restore macOS sleep using Amphetamine.

    On enter: calls `prevent_sleep_mac()` to start Amphetamine session.
    On exit:  calls `let_mac_sleep()`,to end the session even if an exception is raised.
    """
    def __enter__(self):
        prevent_sleep_mac()

    def __exit__(self, exc_type, exc, tb):
        let_mac_sleep()


def prevent_sleep_mac():
    """Prevents mac from sleep using the app amphetamine and osascript

    Catches errors if user is not on mac, does not have amphetamine or else
    """
    try:
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
    except (FileNotFoundError, subprocess.CalledProcessError):
        return


def let_mac_sleep():
    """Stops Amphetamine session and lets mac sleep again

    Catches errors if user is not on mac, does not have amphetamine or else
    """
    try:
        subprocess.run([
            "osascript",
            "-e",
            'tell application "Amphetamine" to end session'
        ])  # :contentReference[oaicite:1]{index=1}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return
