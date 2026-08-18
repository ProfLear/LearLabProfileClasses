"""
learlab-profile-classes: A dataclass-based profilometry analyzer.
"""

from .profilometry_classes import (
    ProfileArray,
    ArealArray,
    ProfileData,
    AngularRoughness,
    ArealData,
    ArealProcess,
    Sample,
    makeSample
)

from .areal_tools import (
    downsample_surface_for_plot,
    generate_subtract_rectBiSpline,
    verts_to_xyz,
    xyz_average_out_nanvalues,
    average_all_nan_values
)

__version__ = "0.1.0"

__all__ = [
    "ProfileArray",
    "ArealArray",
    "ProfileData",
    "AngularRoughness",
    "ArealData",
    "ArealProcess",
    "Sample",
    "makeSample",
    "downsample_surface_for_plot",
    "generate_subtract_rectBiSpline",
    "verts_to_xyz",
    "xyz_average_out_nanvalues",
    "average_all_nan_values",
]
