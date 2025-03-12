import numpy as np
import matplotlib.pyplot as plt

# Parameters
sigma1 = 0.09
sigma = 0.12

# Define a range of potential values.
# For the Gaussian curve with sigma=0.12, most of the density lies within about [-0.5, 0.5].
potential = np.linspace(-1, 1, 400)

# Compute the curves:
curve1 = np.exp(- (potential**2) / sigma1)
curve2 = np.exp(-potential ** 2 / (2 * sigma ** 2)) / (np.sqrt(2 * np.pi) * sigma)

# Create the plot
plt.figure(figsize=(8, 5))
plt.plot(potential, curve1, label=r'$e^{-\frac{potential^2}{\sigma_1}}, \;\sigma_1=0.09$', color='blue')
plt.plot(potential, curve2, label=r'$\frac{e^{-\frac{potential^2}{2\sigma^2}}}{\sqrt{2\pi}\sigma}, \;\sigma=0.12$', color='red', linestyle='--')

plt.xlabel('potential')
plt.ylabel('Value')
plt.title('Comparison of Two Curves')
plt.legend()
plt.grid(True)
plt.show()
