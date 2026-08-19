from dataclasses import dataclass, field
from typing import Optional, Dict, List, Union
import numpy as np
import datetime
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.stats import linregress, skew, kurtosis
from . import areal_tools as arealTools
from .areal_tools import downsample_surface_for_plot

class ProfileArray:
    """
    1D array wrapper representing a line profile with visualization helpers.
    """
    def __init__(self, data: np.ndarray, parent=None):
        self.data = np.asarray(data)
        self.parent = parent

    def __array__(self, dtype=None):
        return np.asarray(self.data, dtype=dtype)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return self.data.ndim

    def plot(self, scale: float = 1.0, max_size_mb: float = 1.0, show: bool = True):
        data = self.data
        if max_size_mb is not None and max_size_mb > 0:
            # 1D line downsample if excessive
            max_pts = int(max_size_mb * 50_000)
            if len(data) > max_pts:
                step = int(np.ceil(len(data) / max_pts))
                data = data[::step]
                scale = scale * step

        x = np.arange(len(data)) * scale
        fig = go.Figure(data=go.Scatter(x=x, y=data, mode='lines', name='Profile'))
        fig.update_layout(
            xaxis_title="Distance (\u03bcm)",
            yaxis_title="Height (\u03bcm)",
            width=700,
            height=400,
            margin=dict(l=50, r=30, b=50, t=50)
        )
        if show:
            fig.show()
        return fig

    def __repr__(self):
        return f"ProfileArray(shape={self.data.shape}, parent={type(self.parent).__name__})"


class ArealArray:
    """
    2D array wrapper representing surface topography with 3D visualization and downsampling.
    """
    def __init__(self, data: np.ndarray, parent=None):
        self.data = np.asarray(data)
        self.parent = parent

    def __array__(self, dtype=None):
        return np.asarray(self.data, dtype=dtype)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return self.data.ndim

    @property
    def size(self):
        return self.data.size

    def to_blender(self):
        print("Sending data to Blender...")

    def plot(self, max_size_mb: float = 1.0, show: bool = True):
        """
        Plots the surface as an interactive 3D surface plot.
        Automatically downsamples if payload would exceed max_size_mb (default 1 MB).
        """
        z_sub, x_sub, y_sub = downsample_surface_for_plot(
            self.data,
            max_size_mb=max_size_mb,
            n_surfaces=1
        )

        fig = make_subplots(specs=[[{'type': 'surface'}]])
        fig.add_trace(go.Surface(
            z=z_sub,
            x=x_sub,
            y=y_sub
        ))
        fig.update_layout(
            autosize=False,
            width=600,
            height=600,
            margin=dict(l=40, r=40, b=40, t=60),
            dragmode="turntable"
        )
        if show:
            fig.show()
        return fig

    def render(
        self,
        xscale: float = 1.0,
        yscale: float = 1.0,
        zscale: float = 10.0,
        zmode: str = "relative",
        max_size_mb: float = 1.0,
        show: bool = True
    ):
        """
        Renders surface topography in a photorealistic style with calibrated aspect ratios and a scale bar.
        Automatically downsamples if payload exceeds max_size_mb.
        """
        ny, nx = self.data.shape
        x_length = nx * xscale
        y_length = ny * yscale

        z_min = float(np.nanmin(self.data))
        z_max = float(np.nanmax(self.data))

        if zmode == "relative":
            z_range = abs(z_max - z_min)
            max_size = max(x_length, y_length, z_range)
            z_axis_size = (z_range * zscale) / max_size if max_size > 0 else 1.0
            z_scale_bar_height = float(np.nanstd(self.data))
        elif zmode == "absolute":
            z_range = zscale
            max_size = max(x_length, y_length)
            z_axis_size = 1.0
            z_scale_bar_height = zscale / 10.0
        else:
            raise ValueError("zmode must be either 'relative' or 'absolute'.")

        x_axis_size = x_length / max_size if max_size > 0 else 1.0
        y_axis_size = y_length / max_size if max_size > 0 else 1.0

        # Downsample for display if needed
        x_coords = np.linspace(0, x_length, nx)
        y_coords = np.linspace(0, y_length, ny)
        z_sub, x_sub, y_sub = downsample_surface_for_plot(
            self.data,
            x=x_coords,
            y=y_coords,
            max_size_mb=max_size_mb,
            n_surfaces=1
        )

        fig = make_subplots(specs=[[{'type': 'surface'}]])
        fig.add_trace(go.Surface(
            z=z_sub,
            x=x_sub,
            y=y_sub,
            colorscale=[[0, "lightgrey"], [1, "lightgrey"]],
            showscale=False,
            lighting=dict(
                ambient=0.2,
                roughness=1,
                diffuse=1,
                fresnel=0,
                specular=0
            )
        ))

        # Scale bar
        sub_nx = len(x_sub)
        scalebar_array = np.array([[z_max] * sub_nx, [z_max + z_scale_bar_height] * sub_nx])
        fig.add_trace(go.Surface(
            z=scalebar_array,
            x=x_sub,
            y=[0, 0],
            colorscale=[[0, "red"], [1, "red"]],
            showscale=False,
            lighting=dict(
                ambient=1,
                roughness=1,
                diffuse=1,
                fresnel=0,
                specular=0
            )
        ))

        fig.update_layout(
            autosize=False,
            width=600,
            height=600,
            margin=dict(l=0, r=0, b=0, t=0),
            dragmode="turntable",
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(
                    x=x_axis_size,
                    y=y_axis_size,
                    z=z_axis_size
                ),
                xaxis=dict(visible=False, showticklabels=False, title=''),
                yaxis=dict(visible=False, showticklabels=False, title=''),
                zaxis=dict(visible=False, showticklabels=False, title='', range=[z_min, z_min + z_range]),
                annotations=[
                    dict(
                        x=x_length / 2,
                        y=0,
                        z=z_max + z_scale_bar_height,
                        text=f"{nx * xscale:.1f} \u03bcm wide, {z_scale_bar_height:.1f} \u03bcm scale bar",
                        font=dict(size=12, color="red"),
                        showarrow=False,
                        xanchor="center",
                        yanchor="bottom"
                    )
                ]
            )
        )
        if show:
            fig.show()
        return fig

    def __repr__(self):
        return f"ArealArray(shape={self.data.shape}, parent={type(self.parent).__name__})"


class ChildAttachableMixin:
    def add_child(self, name: str, value: object) -> None:
        setattr(self, name, value)

    def has_child(self, name: str) -> bool:
        return hasattr(self, name)

    def get_child(self, name: str) -> object:
        return getattr(self, name, None)


@dataclass
class ProfileData:
    zs: ProfileArray
    roughness: Optional[float] = None

    def getProfileRoughness(self, mask: Optional[np.ndarray] = None, fit: bool = True, scale: float = 1.0) -> float:
        """
        Calculates roughness Ra of a 1D profile with optional linear baseline subtraction.
        """
        xz = np.asarray(self.zs.data, dtype=float)
        if mask is None:
            mask = ~np.isnan(xz)

        x_temp = np.arange(len(xz)) * scale
        x = x_temp[mask]
        y = xz[mask]

        if fit:
            slope, intercept, _, _, _ = linregress(x, y)
            fitted_values = slope * x + intercept
            residuals = y - fitted_values
            calc_roughness = float(np.nanmean(np.abs(residuals)))
        else:
            calc_roughness = float(np.nanmean(np.abs(y - np.nanmean(y))))

        self.roughness = calc_roughness
        return calc_roughness

    def getProfileAutocorrelation(self):
        pass

    def plot(self, scale: float = 1.0, max_size_mb: float = 1.0, show: bool = True):
        return self.zs.plot(scale=scale, max_size_mb=max_size_mb, show=show)


@dataclass
class AngularRoughness:
    angles: List[float] = field(default_factory=list)
    min_roughnesses: List[float] = field(default_factory=list)
    min_roughness_profile: Optional[ProfileData] = None
    lower_quartile_roughnesses: List[float] = field(default_factory=list)
    mean_roughnesses: List[float] = field(default_factory=list)
    median_roughnesses: List[float] = field(default_factory=list)
    upper_quartile_roughnesses: List[float] = field(default_factory=list)
    max_roughnesses: List[float] = field(default_factory=list)


@dataclass
class ArealStats:
    rms_roughness: float      # Sq (RMS Roughness)
    skew: float               # Ssk (Skewness)
    kurtosis: float           # Sku (Kurtosis)
    mean: float               # Mean height
    peak_to_valley: float     # Sz (Max peak to min valley height)
    data_ref: object = field(repr=False) # Reference back to the parent ArealData

    def __init__(self, areal_data: "ArealData"):
        z_data = areal_data.zs.data
        mask = ~np.isnan(z_data)
        valid_z = z_data[mask]
        self.data_ref = areal_data

        if valid_z.size == 0:
            self.rms_roughness = 0.0
            self.skew = 0.0
            self.kurtosis = 0.0
            self.mean = 0.0
            self.peak_to_valley = 0.0
            return

        self.mean = float(np.mean(valid_z))
        
        # Center data around mean for standard roughness calculations
        centered_z = valid_z - self.mean
        self.rms_roughness = float(np.sqrt(np.mean(centered_z ** 2)))
        
        # Calculate skewness and kurtosis
        self.skew = float(skew(valid_z, nan_policy='omit'))
        self.kurtosis = float(kurtosis(valid_z, nan_policy='omit'))

        # Peak-to-Valley (Sz) is the absolute range between max and min height
        z_min = float(np.nanmin(z_data))
        z_max = float(np.nanmax(z_data))
        self.peak_to_valley = z_max - z_min

    def print(self):
        """Prints a clean, formatted metrology report."""
        print("┌────────────────────────────────────────┐")
        print("│       Areal Surface Statistics         │")
        print("├────────────────────────────────────────┤")
        print(f"│ Sq (RMS Roughness):  {self.rms_roughness:8.4f} µm  │")
        print(f"│ Ssk (Skewness):      {self.skew:8.4f}     │")
        print(f"│ Sku (Kurtosis):      {self.kurtosis:8.4f}     │")
        print(f"│ Sz (Peak-to-Valley): {self.peak_to_valley:8.4f} µm  │")
        print("└────────────────────────────────────────┘")

    def plot_histogram(self, show: bool = True):
        """Generates and returns a Plotly figure of the height distribution."""
        import plotly.graph_objects as go
        z_data = self.data_ref.zs.data
        valid_z = z_data[~np.isnan(z_data)]

        # Pre-calculate histogram bins in Python using numpy
        # This reduces 1,000,000 raw values to 100 values, saving megabytes of payload
        counts, bin_edges = np.histogram(valid_z, bins=100)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        fig = go.Figure(data=[go.Bar(
            x=bin_centers,
            y=counts,
            width=bin_edges[1] - bin_edges[0],
            name="Heights"
        )])
        
        fig.update_layout(
            title="Surface Height Distribution",
            xaxis_title="Height (µm)",
            yaxis_title="Count",
            bargap=0,  # Removes space between bars so it looks like a histogram
            template="plotly_white"
        )
        if show:
            fig.show()
        return fig


@dataclass
class ArealData:
    zs: ArealArray
    stats: ArealStats = field(init=False)

    def __post_init__(self):
        self.stats = ArealStats(self)

    def fitRectbiSpline(self, name: str = "rectbi_spline", s_scale: float = 1.0) -> "ArealProcess":
        """
        Fits a bivariate spline across the 2D surface, storing the smoothed result
        and residual surface into a new ArealProcess.
        """
        spline, residual = arealTools.generate_subtract_rectBiSpline(self.zs.data, s_scale=s_scale)

        result_data = ArealData(zs=ArealArray(spline, parent=self))
        residual_data = ArealData(zs=ArealArray(residual, parent=self))

        process = ArealProcess(
            details=f"rectbivariate spline with s_scale={s_scale}",
            result=result_data,
            residual=residual_data,
            parent=self
        )

        setattr(self, name, process)
        return process

    def remove_planar_tilt(self, name: str = "leveled") -> "ArealProcess":
        """
        Fits a plane (Z = aX + bY + c) to the valid points and subtracts it.
        Decomposes the surface into a fitted plane (result) and residual (leveled).
        """
        z_data = np.asarray(self.zs.data, dtype=float)
        mask = ~np.isnan(z_data)
        
        rows, cols = z_data.shape
        x_coords = np.arange(cols, dtype=float)
        y_coords = np.arange(rows, dtype=float)
        X, Y = np.meshgrid(x_coords, y_coords)
        
        X_valid = X[mask]
        Y_valid = Y[mask]
        Z_valid = z_data[mask]
        
        if Z_valid.size < 3:
            raise ValueError(f"Need at least 3 valid data points to fit a plane, found {Z_valid.size}.")
            
        A = np.column_stack([X_valid, Y_valid, np.ones_like(X_valid)])
        coeffs, _, _, _ = np.linalg.lstsq(A, Z_valid, rcond=None)
        a, b, c = coeffs
        
        plane_fit = a * X + b * Y + c
        z_corrected = z_data - plane_fit
        
        result_data = ArealData(zs=ArealArray(plane_fit, parent=self))
        residual_data = ArealData(zs=ArealArray(z_corrected, parent=self))
        
        process = ArealProcess(
            details="Planar tilt removal (Z = aX + bY + c)",
            result=result_data,
            residual=residual_data,
            parent=self
        )
        
        setattr(self, name, process)
        return process

    def plot(self, max_size_mb: float = 1.0, show: bool = True):
        return self.zs.plot(max_size_mb=max_size_mb, show=show)

    def render(
        self,
        xscale: float = 1.0,
        yscale: float = 1.0,
        zscale: float = 10.0,
        zmode: str = "relative",
        max_size_mb: float = 1.0,
        show: bool = True
    ):
        return self.zs.render(
            xscale=xscale,
            yscale=yscale,
            zscale=zscale,
            zmode=zmode,
            max_size_mb=max_size_mb,
            show=show
        )

    def getRepresentativeProfiles(self, direction: str = "x", median: bool = True, mean: bool = False):
        pass

    def getAngularProfiles(self):
        pass

    def getArealAutocorrelation(self):
        pass

    def pipeline(self):
        """
        Prints the processing history chain from raw data to this node.
        """
        path = []
        current = self

        while True:
            parent = getattr(current, 'parent', None)
            if not parent or not isinstance(parent, ArealProcess):
                break
            path.append(f"{parent.details}")
            current = parent.parent

        if not path:
            print("Pipeline: Root raw data (no prior transformations)")
        else:
            for step in reversed(path):
                print("\u21aa", step)


@dataclass
class ArealProcess:
    details: str
    result: ArealData
    residual: ArealData
    parent: Optional[ArealData] = None

    def plot(self, max_size_mb: float = 1.0, show: bool = True):
        """
        Plots both the smoothed result and residual surfaces side-by-side.
        Automatically applies downsampling to stay under the max_size_mb notebook limit.
        """
        res_z, res_x, res_y = downsample_surface_for_plot(
            self.result.zs.data,
            max_size_mb=max_size_mb,
            n_surfaces=2
        )
        rem_z, rem_x, rem_y = downsample_surface_for_plot(
            self.residual.zs.data,
            max_size_mb=max_size_mb,
            n_surfaces=2
        )

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'surface'}, {'type': 'surface'}]],
            subplot_titles=["Fitted / Result Surface", "Residual / Roughness Surface"]
        )

        fig.add_trace(
            go.Surface(z=res_z, x=res_x, y=res_y, colorscale='Viridis', name='Result'),
            row=1, col=1
        )
        fig.add_trace(
            go.Surface(z=rem_z, x=rem_x, y=rem_y, colorscale='RdBu', name='Residual'),
            row=1, col=2
        )

        fig.update_layout(
            autosize=False,
            width=900,
            height=500,
            margin=dict(l=40, r=40, b=40, t=60),
            dragmode="turntable"
        )
        if show:
            fig.show()
        return fig


@dataclass
class Sample(ChildAttachableMixin):
    date: datetime.date
    file: Path
    instrument: str
    xy_scale: float
    raw: ArealData
    mask: np.ndarray
    missing_frac: float

    def import_from_zygos_xyz(self):
        from . import zygos_tools as zygosTools
        verts, faces, xyz_array, xy_scale = zygosTools.process_zygos_xyz(self.file)
        self.xy_scale = xy_scale
        raw_data = ArealData(zs=ArealArray(xyz_array, parent=self))
        self.mask = ~np.isnan(xyz_array)
        self.missing_frac = float(np.mean(~self.mask))

        averaged_array = arealTools.average_all_nan_values(xyz_array)
        result = ArealData(zs=ArealArray(averaged_array, parent=raw_data))
        residual = ArealData(zs=ArealArray(np.zeros_like(averaged_array), parent=raw_data))

        averaged_process = ArealProcess(
            details="Result of 9-point NaN local averaging.",
            result=result,
            residual=residual,
            parent=raw_data
        )

        setattr(raw_data, "averaged", averaged_process)
        self.raw = raw_data

    def import_from_bryan(self):
        from . import bryan_tools as bryanTools
        verts, faces, xyz_array, xy_scale = bryanTools.process_bryan_xyz(self.file)
        self.xy_scale = xy_scale
        raw_data = ArealData(zs=ArealArray(xyz_array, parent=self))
        self.mask = ~np.isnan(xyz_array)
        self.missing_frac = float(np.mean(~self.mask))

        averaged_array = arealTools.average_all_nan_values(xyz_array)
        result = ArealData(zs=ArealArray(averaged_array, parent=raw_data))
        residual = ArealData(zs=ArealArray(np.zeros_like(averaged_array), parent=raw_data))

        averaged_process = ArealProcess(
            details="Result of 9-point NaN local averaging.",
            result=result,
            residual=residual,
            parent=raw_data
        )

        setattr(raw_data, "averaged", averaged_process)
        self.raw = raw_data

    def import_from_Bryan(self):
        """Backward compatibility alias for import_from_bryan."""
        return self.import_from_bryan()


def makeSample(file: Union[str, Path], instrument: str = "zygos") -> Sample:
    """
    Factory function to initialize a Sample object from an instrument file.
    """
    dummy_array = np.array([[np.nan]])
    dummy_data = ArealData(zs=ArealArray(dummy_array, parent=None))
    sample = Sample(
        date=datetime.date.today(),
        file=Path(file),
        instrument=instrument,
        xy_scale=1.0,
        raw=dummy_data,
        mask=dummy_array.astype(bool),
        missing_frac=0.0
    )

    inst_clean = instrument.strip().lower()
    if inst_clean in ("zygos", "zygo"):
        sample.import_from_zygos_xyz()
    elif inst_clean == "bryan":
        sample.import_from_bryan()
    else:
        raise ValueError(f"Unsupported instrument '{instrument}'. Supported instruments: 'zygos', 'bryan'.")

    print(f"Sample successfully imported from {file} using '{instrument}' parser.")
    return sample
