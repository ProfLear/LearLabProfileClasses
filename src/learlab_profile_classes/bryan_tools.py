import numpy as np
from pathlib import Path
from typing import Union, Tuple, List

def process_bryan_xyz(xyzfile: Union[str, Path]) -> Tuple[List, List, np.ndarray, float]:
    """
    Parses a Bryan-format profilometry file into vertices, quad faces, 2D height array, and spatial scale.

    Parameters
    ----------
    xyzfile : str or Path
        Path to the Bryan .xyz / .txt file.

    Returns
    -------
    verts : list of (x, y, z) vertices
    faces : list of 4-tuples for mesh faces
    xyz_array : 2D numpy array of z heights in microns
    xy_scale : float, spatial resolution in microns per pixel
    """
    zs_rows = []
    total_width = 1.0
    total_height = 1.0
    z_scale = 1e6  # default from m to microns

    with open(xyzfile, 'r', encoding='utf-8', errors='ignore') as xyz:
        for line in xyz:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                parts = line.split()
                if "Width" in line:
                    val = float(parts[-2])
                    unit = parts[-1]
                    total_width = val * 1e3 if unit == "mm" else (val * 1e6 if unit == "m" else val)
                elif "Height" in line:
                    val = float(parts[-2])
                    unit = parts[-1]
                    total_height = val * 1e3 if unit == "mm" else (val * 1e6 if unit == "m" else val)
                elif "Value units" in line:
                    unit = parts[-1]
                    z_scale = 1e6 if unit == "m" else (1e3 if unit == "mm" else 1.0)
            else:
                row_vals = [float(v) * z_scale for v in line.split("\t") if v.strip()]
                if row_vals:
                    zs_rows.append(row_vals)

    zs_array = np.array(zs_rows, dtype=np.float64)
    n_y, n_x = zs_array.shape

    xs = np.linspace(0, total_width, n_x)
    ys = np.linspace(0, total_height, n_y)

    x_scale = (xs[1] - xs[0]) if n_x > 1 else 1.0
    y_scale = (ys[1] - ys[0]) if n_y > 1 else 1.0
    xy_scale = float((x_scale + y_scale) / 2.0)

    mean_z = np.nanmean(zs_array) if zs_array.size > 0 else 0.0
    zs_corr = zs_array - mean_z

    # Construct vertices and quad faces for 3D/Blender meshes
    verts = []
    for r_idx, y_val in enumerate(ys):
        for c_idx, x_val in enumerate(xs):
            verts.append((x_val, y_val, float(zs_corr[r_idx, c_idx])))

    faces = []
    for r in range(n_y - 1):
        for c in range(n_x - 1):
            tl = r * n_x + c
            tr = r * n_x + (c + 1)
            br = (r + 1) * n_x + (c + 1)
            bl = (r + 1) * n_x + c
            faces.append((tl, tr, br, bl))

    return verts, faces, zs_array, xy_scale
