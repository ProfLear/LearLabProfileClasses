import numpy as np
from typing import Optional, Tuple
from scipy.interpolate import RectBivariateSpline

def downsample_surface_for_plot(
    z: np.ndarray,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    max_size_mb: float = 1.0,
    n_surfaces: int = 1,
    verbose: bool = True
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Checks if a 2D surface grid (and optional x, y coordinates) will exceed
    the maximum serialized payload size for notebook display (default 1 MB).

    If needed, downsamples the grid by uniform integer striding so that the
    generated Plotly figure stays comfortably under the limit while preserving
    aspect ratio and topological features.

    Parameters
    ----------
    z : 2D array-like
        The height map grid of shape (rows, cols).
    x : 1D or 2D array-like, optional
        The x-coordinates (columns).
    y : 1D or 2D array-like, optional
        The y-coordinates (rows).
    max_size_mb : float, default=1.0
        Maximum target payload size in megabytes (MB). If None or <= 0, no downsampling is performed.
    n_surfaces : int, default=1
        Number of surfaces in the figure sharing the budget (e.g. 2 for result+residual).
    verbose : bool, default=True
        Whether to print a notice when downsampling occurs.

    Returns
    -------
    z_sub, x_sub, y_sub : tuple of ndarrays
    """
    z_arr = np.asarray(z)
    if z_arr.ndim != 2 or max_size_mb is None or max_size_mb <= 0:
        return z_arr, x, y

    ny, nx = z_arr.shape
    total_points = ny * nx

    # Target bytes budget per surface (with safety margin for layout/coordinates/JSON metadata)
    safety_factor = 0.75
    budget_bytes = (max_size_mb * 1024 * 1024 * safety_factor) / max(1, n_surfaces)

    # Average bytes per float point in Plotly JSON is ~14.0 bytes
    bytes_per_point = 14.0
    max_allowed_points = int(budget_bytes / bytes_per_point)

    if total_points <= max_allowed_points:
        return z_arr, x, y

    # Calculate integer stride factor
    step = int(np.ceil(np.sqrt(total_points / max_allowed_points)))
    step = max(1, step)

    z_sub = z_arr[::step, ::step]

    x_sub = None
    if x is not None:
        x_arr = np.asarray(x)
        if x_arr.ndim == 1:
            x_sub = x_arr[::step] if len(x_arr) == nx else np.linspace(x_arr[0], x_arr[-1], z_sub.shape[1])
        elif x_arr.ndim == 2:
            x_sub = x_arr[::step, ::step]
        else:
            x_sub = x
    else:
        x_sub = np.linspace(0, nx - 1, z_sub.shape[1])

    y_sub = None
    if y is not None:
        y_arr = np.asarray(y)
        if y_arr.ndim == 1:
            y_sub = y_arr[::step] if len(y_arr) == ny else np.linspace(y_arr[0], y_arr[-1], z_sub.shape[0])
        elif y_arr.ndim == 2:
            y_sub = y_arr[::step, ::step]
        else:
            y_sub = y
    else:
        y_sub = np.linspace(0, ny - 1, z_sub.shape[0])

    if verbose:
        print(f"Note: Surface downsampled from {z_arr.shape} ({total_points:,} pts) to {z_sub.shape} ({z_sub.size:,} pts) [step={step}] to stay under {max_size_mb:.1f}MB notebook limit.")

    return z_sub, x_sub, y_sub


def generate_subtract_rectBiSpline(xyz_array: np.ndarray, s_scale: float = 1.0):
    """
    Fits a RectBivariateSpline to the 2D surface and computes the fitted surface and residual.
    """
    xyz_array = np.asarray(xyz_array)
    n_points = xyz_array.size
    std = np.nanstd(xyz_array)
    s_guess = n_points * (std ** 2)

    spline = RectBivariateSpline(
        np.arange(xyz_array.shape[0]),
        np.arange(xyz_array.shape[1]),
        xyz_array,
        s=s_scale * s_guess
    )

    spline_result = spline(np.arange(xyz_array.shape[0]), np.arange(xyz_array.shape[1]))
    data_minus_spline = xyz_array - spline_result

    return [spline_result, data_minus_spline]


def verts_to_xyz(verts, x_scale: float = 1.0, y_scale: float = 1.0) -> np.ndarray:
    """
    Converts a list of 3D vertices (x, y, z) into a 2D height grid.

    Parameters
    ----------
    verts : list of tuples or lists
        Each element has three entries: (x, y, z).
    x_scale : float, optional
        Distance between adjacent points along x-axis. Default is 1.0.
    y_scale : float, optional
        Distance between adjacent points along y-axis. Default is 1.0.

    Returns
    -------
    xyz : 2D numpy array containing z-values.
    """
    if x_scale == 1.0 and y_scale == 1.0:
        print("Using scale of 1. Note: x and y coordinates should already be grid indices.")

    verts_arr = np.asarray(verts)
    xs = verts_arr[:, 0]
    ys = verts_arr[:, 1]
    zs = verts_arr[:, 2]

    x_indices = np.round(xs / x_scale).astype(int)
    y_indices = np.round(ys / y_scale).astype(int)

    # Reconstruct 2D array
    xyz = np.full((np.max(x_indices) + 1, np.max(y_indices) + 1), np.nan)
    for x_idx, y_idx, z in zip(x_indices, y_indices, zs):
        xyz[x_idx, y_idx] = z

    return xyz


def xyz_average_out_nanvalues(xyz: np.ndarray) -> np.ndarray:
    """
    Replaces NaN values in a 2D array by averaging valid 8-connected neighbors in a 3x3 window.
    """
    removed = xyz.copy()
    rows, cols = xyz.shape

    for i in range(rows):
        for j in range(cols):
            if np.isnan(xyz[i, j]):
                count = 0
                value_sum = 0.0

                for k in (-1, 0, 1):
                    for l in (-1, 0, 1):
                        ni, nj = i + k, j + l
                        if 0 <= ni < rows and 0 <= nj < cols:
                            neighbor = xyz[ni, nj]
                            if not np.isnan(neighbor):
                                value_sum += neighbor
                                count += 1

                if count > 0:
                    removed[i, j] = value_sum / count

    return removed


def average_all_nan_values(xyz: np.ndarray, verbose: bool = True) -> np.ndarray:
    """
    Iteratively fills all NaN values in a 2D array using 3x3 local neighborhood averaging.
    """
    xyz = np.asarray(xyz, dtype=float).copy()
    nan_count = np.sum(np.isnan(xyz))
    if verbose and nan_count > 0:
        pct = (nan_count / xyz.size) * 100
        print(f"Removing {nan_count:,} NaN values ({pct:.1f}% of array) via local averaging.")

    while np.any(np.isnan(xyz)):
        new_xyz = xyz_average_out_nanvalues(xyz)
        # Prevent infinite loop if disconnected island of NaNs
        if np.array_equal(new_xyz, xyz, equal_nan=True):
            # Fallback for completely isolated NaN points: fill with overall mean
            xyz[np.isnan(xyz)] = np.nanmean(xyz)
            break
        xyz = new_xyz

    return xyz
