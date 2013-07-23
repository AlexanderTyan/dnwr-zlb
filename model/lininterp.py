# Filename: lininterp.py
# Author: John Stachurski
# Date: August 2009
# Corresponds to: Listing 6.4

from scipy import interp
import numpy as np
import matplotlib.pyplot as plt


class LinInterp:
    "Provides linear interpolation in one dimension."

    def __init__(self, X, Y):
        """Parameters: X and Y are sequences or arrays
        containing the (x,y) interpolation points.
        """
        self.X = np.sort(X)
        self.Y = Y

    def __call__(self, z):
        """Parameters: z is a number, sequence or array.
        This method makes an instance f of LinInterp callable,
        so f(z) returns the interpolation value(s) at z.
        """
        return interp(z, self.X, self.Y)

    def __add__(self, other):
        assert (self.X == other.X).all()
        return self.Y + other.Y

    def __sub__(self, other):
        assert (self.X == other.X).all()
        return self.Y - other.Y

    def plot(self):
        return plt.plot(self.X, self.Y)

    def inverse(self, z):
        return interp(z, self.Y, self.X)
