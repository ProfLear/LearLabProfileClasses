# Profilometry Data-Class Pipeline

A modular, object-oriented Python library for optical profilometry and surface metrology data processing.

Designed for surface analysis workflows (e.g., Zygo optical interferometers and tabular `.xyz` datasets), this library uses a **data-class and provenance-tracking architecture** to decompose and analyze 2D surface topographies ($z(x, y)$) and 1D line profiles ($z(x)$) non-destructively.

---

## Key Features

* **Non-Destructive Provenance Tracking**: Processing steps create branching nodes that record operations, results (form/nominal shape), and residuals (roughness/waviness) without altering raw data.
* **Instrument Importers**: Built-in parsers for Zygo `.xyz` files and tabular profilometry exports with automatic physical unit scaling ($\mu\text{m}$).
* **Surface Metrology Metrics**: Plane tilt correction, areal RMS roughness ($S_q$), skewness ($S_{sk}$), kurtosis ($S_{ku}$), and 1D profile roughness ($R_a$).
* **Iterative NaN Inpainting**: Intelligent 3x3 local neighborhood averaging to handle missing interferometric points.
* **Multi-Scale Filtering**: 2D bivariate spline fitting (`RectBivariateSpline`) to decompose form, waviness, and roughness.
* **Interactive & Photorealistic 3D Visualizations**: Plotly-based interactive 3D surface views and realistic rendered topography with calibrated scale bars.
* **Notebook-Optimized (Marimo & Jupyter)**: Automatic dynamic downsampling ensures Plotly figures stay under notebook output limits (default 1 MB).

---

## Core Architecture & Mental Model

```
                    ┌───────────────────────────────┐
                    │            Sample             │
                    │ (file, date, xy_scale, mask)  │
                    └──────────────┬────────────────┘
                                   │ .raw
                                   ▼
                         ┌───────────────────┐
                         │     ArealData     │ ◄──────────────────┐
                         │   (zs: ArealArray)│                    │
                         └─────────┬─────────┘                    │
                                   │ .fitRectbiSpline()           │
                                   ▼                              │
                    ┌───────────────────────────────┐             │
                    │         ArealProcess          │             │
                    │    (details, parent, ...)     │             │
                    └───────┬───────────────┬───────┘             │
                     .result│               │.residual            │
                            ▼               ▼                     │
                     ┌─────────────┐ ┌─────────────┐              │
                     │  ArealData  │ │  ArealData  │──────────────┘
                     │ (Form/Trend)│ │ (Roughness) │ (Can chain next process)
                     └─────────────┘ └─────────────┘
```

1. **`Sample`**: The top-level container for a physical measurement. Holds metadata (`date`, `file`, `instrument`, `xy_scale`, `mask`) and the initial `raw` data.
2. **`ArealData`**: Represents a 2D surface height map (`zs: ArealArray`). Computes surface parameters (`getArealRoughness()`) and spawns new processing steps.
3. **`ArealProcess`**: The transformation node. Stores the operation `.details`, the low-frequency fitted component (`.result`), and the high-frequency residual (`.residual`).
4. **`ProfileData`**: Container for 1D cross-sectional profiles and 1D profile metrics ($R_a$).

---

## Installation & Setup

### Prerequisites
* Python 3.9+
* Required packages: `numpy`, `scipy`, `plotly`

### Installation
Clone the repository and install dependencies using `pip` or `uv`:

```bash
git clone https://github.com/ProfLear/Photothermal.git
cd Photothermal/zygoprocessing/dataClassApproach
pip install numpy scipy plotly
```

Or using `uv`:
```bash
uv sync
```

---

## Quickstart Guide

### 1. Load Data into a `Sample`
Use `makeSample()` to parse an instrument file:

```python
import profilometryClasses as pc

# Load a Zygo optical profilometer file
sample = pc.makeSample("path/to/measurement.xyz", instrument="zygos")

# Or load a Bryan tabular profilometry file
sample = pc.makeSample("path/to/dataset.txt", instrument="bryan")
```

### 2. Visualize the Raw Topography
Plot as an interactive 3D surface or as a rendered view with a physical scale bar:

```python
# Interactive Plotly 3D surface plot
sample.raw.plot()

# Photorealistic rendered style with scale bar
sample.raw.render(xscale=1.0, yscale=1.0, zscale=10.0, zmode="relative")
```

### 3. Calculate Surface Roughness Parameters
Performs least-squares planar tilt removal and computes $S_q$ (RMS roughness), skewness, and kurtosis:

```python
sq = sample.raw.getArealRoughness()

print(f"RMS Roughness (Sq): {sample.raw.rms_roughness:.4f} µm")
print(f"Skewness (Ssk):    {sample.raw.skew:.4f}")
print(f"Kurtosis (Sku):    {sample.raw.kurtosis:.4f}")
```

### 4. Decompose Surface (Spline Smoothing & Residual)
Fit a bivariate spline to decompose the surface into low-frequency form and high-frequency roughness:

```python
# Fit spline and attach process as 'first_spline'
process = sample.raw.fitRectbiSpline(name="first_spline", s_scale=1.0)

# Compare fitted surface and residual roughness side-by-side
process.plot()

# Access the fitted and residual surfaces as ArealData objects:
form_surface = sample.raw.first_spline.result
roughness_surface = sample.raw.first_spline.residual

# Calculate roughness on the residual component
roughness_surface.getArealRoughness()
```

### 5. Inspect the Transformation History
Every processed node knows its lineage. You can inspect the entire processing pipeline:

```python
roughness_surface.pipeline()
# Output:
# ↪ Result of 9-point NaN local averaging.
# ↪ rectbivariate spline with s_scale=1.0
```

---

## Usage in Marimo / Jupyter Notebooks

### Preventing Duplicate Plot Outputs
In Marimo or Jupyter notebooks, cell outputs automatically render the returned `Figure`. To prevent the plot from rendering twice, pass `show=False`:

```python
# In a Marimo or Jupyter cell:
sample.raw.plot(show=False)
```

In standalone scripts (terminal/IDE), calling `sample.raw.plot()` defaults to `show=True` and will automatically open the plot in your browser.

### Automatic Dynamic Downsampling (1 MB Limit)
Large profilometry grids (e.g. $1024 \times 1024 = 1.05\text{M}$ points) produce multi-megabyte JSON payloads that can cause browser notebooks to lag or crash.

All `plot()` and `render()` methods automatically calculate the exact integer stride needed to keep the output payload comfortably below `max_size_mb` (default `1.0` MB) while preserving topological features and aspect ratio:

```python
# Customizing the size threshold (in megabytes)
sample.raw.plot(max_size_mb=0.5, show=False)

# Disable downsampling completely (render full resolution)
sample.raw.plot(max_size_mb=None, show=False)
```

---

## File Structure

| File | Description |
| :--- | :--- |
| `profilometryClasses.py` | Core classes: `Sample`, `ArealData`, `ArealProcess`, `ProfileData`, `ArealArray`, and `makeSample`. |
| `arealTools.py` | Mathematical algorithms: NaN gap-filling, bivariate splines, grid rasterization, and dynamic downsampling. |
| `zygosTools.py` | Parser for Zygo optical profilometer `.xyz` export files. |
| `bryanTools.py` | Parser for tabular profilometer `.txt`/`.xyz` files. |
| `demonstration.py` | Executable walkthrough demonstrating standard workflow patterns. |
| `sharedTools.py` | Re-exports common utilities for backward compatibility. |

---

## License & Attribution

Developed by the Lear Research Group for optical profilometry and photothermal surface characterization.
