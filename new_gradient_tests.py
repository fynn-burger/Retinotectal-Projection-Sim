import numpy as np
import matplotlib.pyplot as plt

# Parameter definieren
cols = 50
gc_count = 200
gc_r_factor = 1
gc_l_factor = 1
gc_r_decay = 0.1
gc_l_decay = 0.1
gc_r_shift = 200
gc_l_shift = -200

# Wachstumspositionen der Wachstumskegel berechnen
x_positions = np.linspace(1, cols, gc_count)
gc_numbers = list(range(1, gc_count + 1))
center = (cols + 1) / 2
print(center)

receptors = []
ligands = []
for position in x_positions:
    receptors.append(gc_r_factor * np.exp(gc_r_decay * (position - center + gc_r_shift)))
    ligands.append(gc_l_factor * np.exp(-gc_l_decay * (position - center + gc_l_shift)))

print(receptors)








# Visualisierung mit einzelnen Punkten
plt.figure(figsize=(10, 6))
plt.scatter(gc_numbers, receptors, label='Rezeptoren', color='blue')
plt.scatter(gc_numbers, ligands, label='Liganden', color='red')
plt.xlabel('Wachstumskegel Position')
plt.ylabel('Signalintensität')
plt.title('Visualisierung der Wachstumskegel als Punkte')
plt.legend()
plt.grid(True)
plt.show()
