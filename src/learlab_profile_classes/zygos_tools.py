import numpy as np
from pathlib import Path
from typing import Union, Tuple, List
from . import areal_tools as arealTools

def process_zygos_xyz(xyzfile: Union[str, Path]) -> Tuple[List, List, np.ndarray, float]:
    """
    Parses a Zygo .xyz file into vertices, quad faces, a 2D height array, and the spatial pixel scale.

    Parameters
    ----------
    xyzfile : str or Path
        Path to the Zygo .xyz file.

    Returns
    -------
    verts : list of tuples (x, y, z)
    faces : list of 4-tuples for mesh quad faces
    xyz_array : 2D numpy array of z heights in microns
    xy_scale : float, spatial resolution in microns per pixel
    """
    xs = []
    ys = []
    zs = []
    record = False
    n_x = 0
    n_y = 0
    xy_scale = 1.0

    with open(xyzfile, 'r', encoding='utf-8', errors='ignore') as xyz:
        for i, line in enumerate(xyz):
            line_str = line.strip()
            if i == 3 and line_str:
                parts = line_str.split()
                if len(parts) >= 3:
                    try:
                        n_x = int(parts[2])
                        n_y = int(parts[2])
                    except (ValueError, IndexError):
                        pass

            if i == 7 and line_str:
                parts = line_str.split()
                if len(parts) >= 7:
                    try:
                        xy_scale = float(parts[6]) * 1e6  # Convert to microns per pixel
                    except (ValueError, IndexError):
                        pass

            if "#" in line:
                if not record:
                    record = True
                else:
                    record = False
            elif record and line_str:
                sl = line_str.split()
                if len(sl) >= 3:
                    try:
                        y_idx = int(sl[0])
                        x_idx = int(sl[1])
                        xs.append(x_idx * xy_scale)
                        ys.append(y_idx * xy_scale)
                        try:
                            zs.append(float(sl[2]))  # Microns
                        except ValueError:
                            zs.append(np.nan)
                        except (ValueError, IndexError):
                            continue
                    except (ValueError, IndexError):
                        continue

    zs = np.array(zs, dtype=float)
    mean_z = np.nanmean(zs) if zs.size > 0 else 0.0
    zs_corr = zs - mean_z

    verts = [(x, y, z) for x, y, z in zip(xs, ys, zs_corr)]

    faces = []
    if n_x > 1 and n_y > 1:
        for x in range(1, n_x):
            for y in range(1, n_y - 1):
                faces.append((
                    (x - 1) * n_y + y,
                    (x - 1) * n_y + y + 1,
                    x * n_y + y + 1,
                    x * n_y + y
                ))

    xyz_array = arealTools.verts_to_xyz(verts, x_scale=xy_scale, y_scale=xy_scale)
    return verts, faces, xyz_array, xy_scale
