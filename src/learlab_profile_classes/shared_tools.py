"""
shared_tools.py - Re-exports common utilities from areal_tools for backward compatibility.
"""
from .areal_tools import verts_to_xyz, downsample_surface_for_plot

__all__ = ["verts_to_xyz", "downsample_surface_for_plot"]
