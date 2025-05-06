import math
import numpy as np

def make_gauss_kernel(a, threshold):
    """
    Build unnormalized 2D Gaussian kernel with decay a and threshold cutoff.
    Returns kernel array and its sum.
    """
    r_exact = math.sqrt(-math.log(threshold) / a)
    radius = math.ceil(r_exact)
    size = 2 * radius + 1
    x_array = np.arange(size) - radius
    y_array = x_array.copy()
    X, Y = np.meshgrid(x_array, y_array, indexing='ij')
    G = np.exp(-a * (X**2 + Y**2))
    G[G < threshold] = 0.0
    kernel_sum = G.sum()
    return G, kernel_sum