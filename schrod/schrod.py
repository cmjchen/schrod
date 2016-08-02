import numpy as np
from scipy.integrate import simps


class Schrod:
    """
    A class for representing and solving the time-independent schrodinger
    equation.
    """
    x = None
    V = None
    n_basis = None
    eigvals = None
    eigvecs = None

    x_min = None
    x_max = None
    box_size = None
    _x_center = None

    def __init__(self, x, V, n_basis=20):
        """
        Initialize a time independent schrodinger equation
        :param x: an ndarray. The coordinates at which the potential is evaluated.
        :param V: the potential or potentials to solve. An ndarray
        of shape (n_V, n_x) where n_V is the number of potentials
        and n_x is the length of x.
        :param n_basis:
        """
        self.x = x
        self.V = V
        self.n_basis = n_basis

        self.x_min = x[0]
        self.x_max = x[-1]
        self.box_size = np.abs(self.x_max - self.x_min)
        self._x_center = self.x_min + self.box_size / 2.

    def solve(self, verbose=False):
        if verbose:
            print("Calculating the Hamiltonian matrices...")
        Hs = self._H(verbose)

        if verbose:
            print("Diagonalizing the Hamiltonian matrices...")

        self.eigvals, self.eigvecs = np.linalg.eigh(Hs, UPLO='L')

        return self.eigvals, self.eigvecs

    def psi(self):
        basis_vec = np.arange(1, self.eigvecs.shape[-1] + 1)

        return np.dot(self.eigvecs.transpose((0, 2, 1)),
                      self._psi0(basis_vec, self.x))

    def prob(self):
        return self.psi() ** 2

    # Get functions
    def get_x(self):
        return self.x

    def get_V(self):
        return self.V

    def get_n_basis(self):
        return self.n_basis

    def get_eigvals(self):
        return self.eigvals

    def get_eigvecs(self):
        return self.eigvecs

    # Set functions
    def set_x(self, x):
        self.x = x
        self.x_min = x[0]
        self.x_max = x[-1]
        self.box_size = self.x_max = self.x_min
        self._x_center = self.x_min + self.box_size / 2.

    def set_V(self, V):
        self.V = V

    def set_n_basis(self, n_basis):
        self.n_basis = n_basis

    # Private functions:
    def _H(self, verbose=False):
        n_matels = self.n_basis * (self.n_basis + 1) / 2
        h = np.zeros((self.V.shape[0], self.n_basis, self.n_basis))
        for m in range(self.n_basis):
            for n in range(m + 1):
                h[:, m, n] = self._Vmn(m, n)

                # Print a status
                n_sofar = (m + 1) * m / 2 + n + 1
                percent = n_sofar / n_matels * 100

                if verbose:
                    print("\r  Status: %0.2f %% complete" % percent, end='')

        if verbose:
            print("")

        return h + np.diag(self._E0(np.arange(1, self.n_basis + 1)))

    def _psi0(self, n, x):
        """
        Evaluate the nth box state at x
        :param n: array-like, 1-indexed state labels
        :param x: array-like, positions between -1 and 1
        :return: an array of shape (len(n), len(x))
        """
        kn = n * np.pi / self.box_size

        return np.sqrt(2 / self.box_size) * \
               np.sin(np.outer(kn, x - self._x_center + self.box_size / 2))

    def _E0(self, n):
        """
        The nth energy level in the box
        :param n: the state label
        :return: the energy
        """
        return n ** 2 * np.pi ** 2 / (2. * self.box_size ** 2)

    def _matel_integrand(self, m, n):
        """
        The n,m matrix element of the V potential evaluated at the x coordinates
        :param n:   the row index
        :param m:   the column index
        :param x:   array-like, a vector of x coordinates
        :param V:   array-like, an array of potential values. The rows correspond to
                    the entries in x. The columns correspond to different potentials
        :return:    the integrand of the matrix element
        """
        return self._psi0(m + 1, self.x) * self._psi0(n + 1, self.x) * self.V

    def _Vmn(self, m, n):
        return simps(x=self.x, y=self._matel_integrand(m, n), axis=1)


if __name__ == "__main__":
    # Import
    import time

    # The harmonic oscillator
    x_vec = np.linspace(-1, 1, 200)
    V_vec = np.asarray(([1000 * x ** 2 for x in x_vec],))

    # TISE
    tiseq = Schrod(x_vec, V_vec, 200)

    t0 = time.time()
    tiseq._H()
    print("For loop time: %0.3f seconds" % (time.time() - t0))