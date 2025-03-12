import math
import numpy as np
import matplotlib.pyplot as plt


def potential(rho, receptor, ligand):
    """
    Calculate the potential based on the given rho, receptor, and ligand values.
    """
    # Constants
    radius = 3
    ft_ligands = 0
    ft_receptors = 54

    # Compute outer and inner contributions
    outer_receptor_current = receptor * rho
    outer_ligand_current = ligand * rho
    inner_receptor_current = receptor * (1 - rho)
    inner_ligand_current = ligand * (1 - rho)

    # Area of a circle with the given radius
    area = math.pi * radius ** 2

    gc_outer_receptor_sum = outer_receptor_current * area
    gc_outer_ligand_sum = outer_ligand_current * area
    gc_inner_receptor_sum = inner_receptor_current * area
    gc_inner_ligand_sum = inner_ligand_current * area

    # Calculate signals
    forward_sig = gc_outer_receptor_sum * ft_ligands + gc_inner_receptor_sum * gc_inner_ligand_sum
    reverse_sig = gc_outer_ligand_sum * ft_receptors + gc_inner_ligand_sum * gc_inner_receptor_sum

    # Round the signals to six decimal places
    forward_sig = float("{:.6f}".format(forward_sig))
    reverse_sig = float("{:.6f}".format(reverse_sig))

    # Ensure signals are strictly positive (to avoid taking log of 0)
    forward_sig = max(forward_sig, 0.0001)
    reverse_sig = max(reverse_sig, 0.0001)

    # Return the potential as the absolute difference of the logs
    return abs(math.log(reverse_sig) - math.log(forward_sig))


# Generate a range of rho values from 0 to 1
rho_values = np.linspace(0, 1, 200)

# Define the three cases with their corresponding receptor and ligand values
cases = [
    {'receptor': 1, 'ligand': 0.01, 'label': 'Receptor = 1, Ligand = 0.01', 'color': 'blue'},
    {'receptor': 10, 'ligand': 0.1, 'label': 'Receptor = 10, Ligand = 0.1', 'color': 'black'},
    {'receptor': 0.01, 'ligand': 1, 'label': 'Receptor = 0.01, Ligand = 1', 'color': 'red'},
    {'receptor': 0.1, 'ligand': 10, 'label': 'Receptor = 0.1, Ligand = 10', 'color': 'orange'},
    {'receptor': 0.37, 'ligand': 0.37, 'label': 'Receptor = 0.37, Ligand = 0.37', 'color': 'green'},
    {'receptor': 3.7, 'ligand': 3.7, 'label': 'Receptor = 3.7, Ligand = 3.7', 'color': 'purple'}
]

# Create a single plot
plt.figure(figsize=(8, 6))

for case in cases:
    receptor = case['receptor']
    ligand = case['ligand']
    color = case['color']

    # Compute potential for each rho value
    pot_values = [potential(rho, receptor, ligand) for rho in rho_values]

    # Plot all three graphs on the same figure
    plt.plot(rho_values, pot_values, label=case['label'], color=color, lw=2)

# Formatting the plot
plt.xlabel('rho', fontsize=14)
plt.ylabel('Potential', fontsize=14)
plt.title('Potential vs. rho for Different Receptor/Ligand Ratios', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
