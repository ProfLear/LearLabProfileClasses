# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 14:44:40 2025

- peak to valley distances
- roughness Ra, Sq?
- blender



@author: benle
"""
import numpy as np

sampling = 10

xyz_file = "C:/Users/benle/Downloads/MiniPlateBigPre.txt"
#xyz_file = "C:/Users/benle/Downloads/MiniPlateSmallPre.txt"


def import_Bryan(xyz_file, sampling = 1):
    with open (xyz_file, "r") as xyz:
        # this block gets the information on the image width and height
        n_headers = 0
        n_data_rows = 0
        n_data_cols = 0
        zs = []
        for i, line in enumerate(xyz, start = 1):
            line = line.strip("\n")  # let us remove newline characters
            if line[0] == "#": # we are in a header
                n_headers = n_headers + 1
                if "Width" in line:
                    total_width = float(line.split(" ")[-2])
                    #print(line.split(" "))
                    if line.split(" ")[-1] == "mm":
                        total_width = total_width * 1E-3 # convert from mm to meters
                    else:
                        print("width unit is not recognized")
                if "Height" in line:
                    total_height = float(line.split(" ")[-2])
                    if line.split(" ")[-1] == "mm":
                        total_height = total_height * 1E-3 # convert from mm to meters
                    else:
                        print("height unit is not recognized")
                if "Value units" in line:
                    if line.split(" ")[-1] == "m":
                        z_scale = 1 # what we should multiply by to get to meters
            
            else: # then we are not in a header. This is data. 
                n_data_rows = n_data_rows + 1
                if (i - n_headers)%sampling == 0:# this is a row we will sample
                    temp_row = []
                    for j, value in enumerate(line.split("\t")):
                        if j%sampling == 0: # this is a point to sample
                            temp_row.append(float(value)*z_scale)
                            final_sampled_col = j
                    if n_data_cols == 0: # we haven't yet recorded the number of data points
                        n_data_cols = j # so recordit
                    zs.append(np.array(temp_row))
                    final_sampled_row = i
        
    zs = np.array(zs)
    return zs, [(total_width*final_sampled_col/n_data_cols)/len(zs[0]), (total_height*final_sampled_row/n_data_rows)/len(zs)] # also return x_scale and y_scale in xy_scales
 
    
raw_zs, xy_scales = import_Bryan(xyz_file, sampling = 10)


#%%
from scipy.ndimage import gaussian_filter
form = gaussian_filter(raw_zs, sigma=90)  #50 for small, 90 for large
raw_zs_minus_form = raw_zs - form

# then find the wave and subtract
wave = gaussian_filter(raw_zs_minus_form, sigma=3)
raw_zs_minus_form_minus_wave = raw_zs_minus_form - wave
#%

from plotly.subplots import make_subplots  
import plotly.graph_objects as go 

def multi_plot(raw, form, form_subtracted, wave, wave_subtracted, xy_scales = [1,1], z_mag = 1):
    fig = make_subplots(rows = 7, cols = 11, specs=[
        [{'type': 'surface', "colspan": 3, "rowspan": 3}, {}, {}, {}, {'type': 'surface', "colspan": 3, "rowspan": 3}, {}, {}, {}, {'type': 'surface', "colspan": 3, "rowspan": 3}, {}, {}],
        [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
        [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
        [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
        [{}, {}, {'type': 'surface', "colspan": 3, "rowspan": 3}, {}, {}, {}, {'type': 'surface', "colspan": 3, "rowspan": 3}, {}, {}, {}, {}],
        [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
        [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        ],
        vertical_spacing = 0, horizontal_spacing = 0)
    
    fig.add_trace(go.Surface(
        z=raw - np.mean(raw),
        x=np.linspace(0, len(raw), len(raw))*xy_scales[0],
        y=np.linspace(0, len(raw[0]), len(raw[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 1, col = 1,
        )
    
    fig.add_trace(go.Surface(
        z=form_subtracted - np.mean(form_subtracted),
        x=np.linspace(0, len(form_subtracted), len(form_subtracted))*xy_scales[0],
        y=np.linspace(0, len(form_subtracted[0]), len(form_subtracted[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 1, col = 5,
        )
    
    fig.add_trace(go.Surface(
        z=wave_subtracted - np.mean(wave_subtracted),
        x=np.linspace(0, len(wave_subtracted), len(wave_subtracted))*xy_scales[0],
        y=np.linspace(0, len(wave_subtracted[0]), len(wave_subtracted[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 1, col = 9,
        )
    
    
    fig.add_trace(go.Surface(
        z=form - np.mean(form),
        x=np.linspace(0, len(form), len(form))*xy_scales[0],
        y=np.linspace(0, len(form[0]), len(form[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 5, col = 3,
        )
    
    fig.add_trace(go.Surface(
        z=wave - np.mean(wave),
        x=np.linspace(0, len(wave), len(wave))*xy_scales[0],
        y=np.linspace(0, len(wave[0]), len(wave[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 5, col = 7,
        )
    
    
    fig.add_trace(go.Surface(
        z=wave_subtracted - np.mean(wave_subtracted),
        x=np.linspace(0, len(wave_subtracted), len(wave_subtracted))*xy_scales[0],
        y=np.linspace(0, len(wave_subtracted[0]), len(wave_subtracted[0]))*xy_scales[1],
        colorscale = "greys_r",
    ),
        row = 1, col = 9,
        )
    fig.update_layout(autosize=False, 
                      width=2200, height=1400,
                      margin=dict(l=65, r=50, b=65, t=90),
                      scene=dict(zaxis=dict(range = [-0.5*len(raw)*xy_scales[1]/z_mag, 0.5*len(raw)*xy_scales[1]/z_mag])),
                      scene2=dict(zaxis=dict(range = [-0.5*len(raw)*xy_scales[1]/z_mag, 0.5*len(raw)*xy_scales[1]/z_mag])),
                      scene3=dict(zaxis=dict(range = [-0.5*len(raw)*xy_scales[1]/z_mag, 0.5*len(raw)*xy_scales[1]/z_mag])),
                      )
    return fig

fig = multi_plot(raw_zs, form, raw_zs_minus_form, wave, raw_zs_minus_form_minus_wave, xy_scales = xy_scales, z_mag = 1)
fig.show("browser")


print(f"Sq = {np.std(raw_zs_minus_form - np.mean(raw_zs_minus_form))}")



#%% histograms of heights...

def remove_outliers(data, cutoff=99.9):
    # Create a mask where values are within the range
    
    p_lower = np.percentile(data, 100-cutoff)
    p_upper = np.percentile(data, cutoff)
    
    print(f"Lower limit: {p_lower}")
    print(f"Upper limit: {p_upper}")

    mask = (data >= p_lower) & (data <= p_upper)
    
    # Apply mask
    return data[mask]
    
def histogram_of_heights(data, cutoff=99.9):
    
    # Apply mask
    valid_values = remove_outliers(data, cutoff = cutoff)
    
    return qp.quickHist(valid_values.flatten(), output = None)

histogram_of_heights(raw_zs_minus_form, cutoff = 99.9)

#%% then fit the data to 3 Gaussians
from lmfit import Model
from lmfit.models import GaussianModel

def fit_Gaussians(data, cutoff = 99.9, n_Gaussians = 3):
    hist = histogram_of_heights(data, cutoff = cutoff)
    x_data = hist.data[0].x
    y_data = hist.data[0].y
    model = GaussianModel(prefix = "g1_")
    if n_Gaussians > 1:
        for n in range(2, n_Gaussians+1):
            model = model + GaussianModel(prefix = f"g{n}_")
    
    #now we have the model built out...
    # so add parameters...
    
    params = model.make_params()
    
    sigma_guess = np.std(data)
    amplitude_guess = np.sum(y_data)*sigma_guess/n_Gaussians
    center_guess = np.mean(data)
    center_start = center_guess - 2*sigma_guess
    for n in range(1, n_Gaussians+1):
        params.add_many(
            (f"g{n}_amplitude", amplitude_guess/n, True, amplitude_guess/100, None),
            (f"g{n}_center", center_start + n/n_Gaussians*3*sigma_guess, True, np.min(x_data), np.max(x_data)),
            (f"g{n}_sigma", sigma_guess, True, sigma_guess/10, 1.5*sigma_guess/n_Gaussians),
            )
    
    result = model.fit(y_data, x = x_data, params = params)
    
    return result
    
fit_result = fit_Gaussians(
    raw_zs_minus_form, 
    n_Gaussians = 2,
    )
    
qp.plotFit(fit_result, components = True, residual = True)
print(fit_result.fit_report())




#%%mFFT stuff

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import tukey

def analyze_pattern_fft(z_data, pixel_size_um=xy_scales[0]):
    """
    Performs 2D FFT on form-removed profilometry data to find pattern periodicity.
    
    Parameters:
    - z_data: 2D numpy array (must be form-subtracted/flat).
    - pixel_size_um: Physical size of one pixel (e.g., 0.5 microns).
    """
    rows, cols = z_data.shape
    
    # --- STEP 1: Pre-processing ---
    # FFT cannot handle NaNs. Replace them with 0 (the mean of form-subtracted data).
    z_clean = z_data.copy()
    z_clean[np.isnan(z_clean)] = 0
    
    # Apply a Window Function (Tukey is flatter than Hanning, preserving feature amplitude)
    # This prevents "cross" artifacts from edge discontinuities
    window_row = tukey(rows, alpha=0.1)
    window_col = tukey(cols, alpha=0.1)
    window_2d = np.outer(window_row, window_col)
    z_windowed = z_clean * window_2d

    # --- STEP 2: The FFT ---
    # Compute the 2-dimensional FFT
    f_transform = np.fft.fft2(z_windowed)
    
    # Shift the zero-frequency component to the center of the spectrum
    f_shift = np.fft.fftshift(f_transform)
    
    # Calculate Power Spectrum (Magnitude squared)
    # We add a tiny epsilon to avoid log(0) errors
    power_spectrum = 20 * np.log(np.abs(f_shift) + 1e-9)

    # --- STEP 3: Calculate Physical Frequencies ---
    # Get the frequency axes (cycles per pixel)
    freq_y = np.fft.fftshift(np.fft.fftfreq(rows, d=pixel_size_um))
    freq_x = np.fft.fftshift(np.fft.fftfreq(cols, d=pixel_size_um))

    # --- STEP 4: Find Dominant Pitch ---
    # We mask out the center (DC component) because it's always the brightest
    center_y, center_x = rows // 2, cols // 2
    mask_radius = 5 # pixels
    
    # Create a copy to find the max peak
    spectrum_for_peak = np.abs(f_shift).copy()
    y_grid, x_grid = np.ogrid[:rows, :cols]
    mask = (x_grid - center_x)**2 + (y_grid - center_y)**2 <= mask_radius**2
    spectrum_for_peak[mask] = 0 # Zero out the center DC spike
    
    # Find the indices of the brightest spot (the primary pattern frequency)
    peak_idx = np.unravel_index(np.argmax(spectrum_for_peak), spectrum_for_peak.shape)
    
    # Extract the frequency of that peak
    dom_freq_y = freq_y[peak_idx[0]]
    dom_freq_x = freq_x[peak_idx[1]]
    
    # Convert spatial frequency (1/um) to Pitch (um)
    # Pitch = 1 / Frequency
    total_freq = np.sqrt(dom_freq_x**2 + dom_freq_y**2)
    pitch_um = 1 / total_freq if total_freq > 0 else 0

    return power_spectrum, freq_x, freq_y, pitch_um

# --- EXAMPLE USAGE ---

# Assume 'corrected_data' is your Z-array from the previous step
# And let's say your pixel size is 2.5 microns
power_spec, fx, fy, pitch = analyze_pattern_fft(raw_zs_minus_form, pixel_size_um=2.5)

print(f"Detected Pattern Pitch: {pitch:.2f} microns")

# Plotting
plt.figure(figsize=(8, 6))
# We use extent to map pixels to frequency units
plt.imshow(power_spec, 
           extent=[fx.min(), fx.max(), fy.min(), fy.max()], 
           cmap='inferno')
plt.title(f"FFT Power Spectrum\nDominant Pitch: {pitch:.2f} $\mu$m")
plt.xlabel("Spatial Frequency X (1/$\mu$m)")
plt.ylabel("Spatial Frequency Y (1/$\mu$m)")
plt.colorbar(label='Log Power Magnitude')
plt.show()


#%% autocorrelation
import numpy as np
from scipy.signal import fftconvolve
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Re-using the same numpy polar transform function from before
def polar_transform_numpy(image, output_shape=(360, 500)):
    rows, cols = image.shape
    center_y, center_x = rows // 2, cols // 2
    num_angles, num_radii = output_shape
    theta = np.linspace(0, 2 * np.pi, num_angles, endpoint=False)
    r = np.linspace(0, min(center_x, center_y), num_radii)
    R, Theta = np.meshgrid(r, theta)
    X_query = R * np.cos(Theta) + center_x
    Y_query = R * np.sin(Theta) + center_y
    X_indices = np.clip(np.round(X_query).astype(int), 0, cols - 1)
    Y_indices = np.clip(np.round(Y_query).astype(int), 0, rows - 1)
    return image[Y_indices, X_indices], r, np.degrees(theta)

def analyze_and_plot_plotly_normalized(z_data):
    # --- Step 1: Pre-processing ---
    # Subtract mean (Essential for correlation to center at 0)
    data_centered = z_data - np.nanmean(z_data)
    data_centered = np.nan_to_num(data_centered)
    
    # --- Step 2: 2D Autocorrelation ---
    acf_2d = fftconvolve(data_centered, data_centered[::-1, ::-1], mode='same')
    
    # --- Step 3: NORMALIZATION ---
    # The center of the ACF represents the signal dotted with itself (Variance * N)
    # We divide by this maximum to scale everything to range [-1, 1]
    acf_max = np.max(acf_2d)
    if acf_max != 0:
        acf_2d /= acf_max
    
    # --- Step 4: Polar Transform ---
    radius_len = min(acf_2d.shape) // 2
    acf_polar, radii, angles = polar_transform_numpy(acf_2d, output_shape=(360, radius_len))

    # --- Step 5: Plotly Visualization ---
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("2D Autocorrelation (Normalized)", "Angle-Resolved Heatmap"),
        horizontal_spacing=0.15
    )

    # Plot 1: Cartesian
    fig.add_trace(
        go.Heatmap(
            z=acf_2d,
            colorscale='RdBu', # Red-Blue diverges nicely around 0
            zmid=0,            # Force 0 to be the center color (white/gray)
            zmin=-1, zmax=1,   # Lock scale to -1 to 1
            showscale=False,
            name='Cartesian'
        ),
        row=1, col=1
    )

    # Plot 2: Polar
    fig.add_trace(
        go.Heatmap(
            z=acf_polar,
            x=radii,
            y=angles,
            colorscale='RdBu', # Consistent coloring
            zmid=0,
            zmin=-1, zmax=1,
            colorbar=dict(title='Correlation Coeff'),
            name='Polar',
            hovertemplate='Angle: %{y:.1f}°<br>Shift: %{x:.1f} px<br>Corr: %{z:.3f}<extra></extra>'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Normalized Pattern Analysis",
        height=600, width=1100,
        template="plotly_white"
    )
    
    # Axis labels
    fig.update_xaxes(title_text="X Pixel Shift", row=1, col=1)
    fig.update_yaxes(title_text="Y Pixel Shift", row=1, col=1)
    fig.update_xaxes(title_text="Translation Distance (pixels)", row=1, col=2)
    fig.update_yaxes(title_text="Angle (degrees)", row=1, col=2, range=[360, 0])

    fig.show("browser")

# Run it
analyze_and_plot_plotly_normalized(raw_zs_minus_form)


#%% Try to find pitch from autocorrelation
import numpy as np
from scipy.signal import fftconvolve
from scipy.ndimage import maximum_filter
import plotly.graph_objects as go

def find_peaks_simple(image, min_distance=10, threshold_rel=0.5):
    """
    Finds local maxima without skimage.
    1. Dilates the image (finds max in neighborhood).
    2. Checks where original image equals dilated image.
    """
    # 1. Define neighborhood window size
    size = 2 * min_distance + 1
    
    # 2. Find local max in that window
    image_max = maximum_filter(image, size=size, mode='constant')
    
    # 3. Boolean mask where Image == Local Max
    mask = (image == image_max)
    
    # 4. Filter by threshold (ignore noise peaks)
    threshold = np.max(image) * threshold_rel
    mask = mask & (image > threshold)
    
    # 5. Get coordinates
    coords = np.argwhere(mask)
    return coords

def analyze_pitch_from_acf(z_data, pixel_size_um=1.0):
    # 1. Calculate Normalized ACF
    data_centered = z_data - np.nanmean(z_data)
    data_centered = np.nan_to_num(data_centered)
    acf_2d = fftconvolve(data_centered, data_centered[::-1, ::-1], mode='same')
    acf_2d /= np.max(acf_2d) # Normalize 0 to 1
    
    # 2. Find Peaks
    # min_distance: approximate radius in pixels to ignore noise. 
    # Adjust this if your pitch is very small (< 20 pixels).
    peaks = find_peaks_simple(acf_2d, min_distance=10, threshold_rel=0.3)
    
    # 3. Analyze Peaks to find Pitch
    center = np.array(acf_2d.shape) // 2
    
    # Calculate distances from center to all peaks
    distances = []
    valid_peaks = []
    
    for p in peaks:
        dist = np.linalg.norm(p - center)
        if dist > 0: # Ignore the center peak itself (dist=0)
            distances.append(dist)
            valid_peaks.append(p)
    
    distances = np.array(distances)
    valid_peaks = np.array(valid_peaks)
    
    # The Pitch is the minimal non-zero distance (Nearest Neighbor)
    if len(distances) > 0:
        min_idx = np.argmin(distances)
        pitch_pixels = distances[min_idx]
        pitch_um = pitch_pixels * pixel_size_um
        nearest_peak = valid_peaks[min_idx]
    else:
        pitch_pixels = 0
        pitch_um = 0
        nearest_peak = center

    return acf_2d, peaks, pitch_pixels, pitch_um, nearest_peak

# --- Usage with Plotly ---

# Assume 'corrected_data' is your profilometry array
pixel_size = xy_scales[0] # microns
acf, peaks, pitch_px, pitch_um, p_near = analyze_pitch_from_acf(raw_zs_minus_form, pixel_size_um=pixel_size)

print(f"Calculated Pitch: {pitch_px:.2f} pixels ({pitch_um:.2f} um)")

# Create Plotly Figure
fig = go.Figure()

# 1. The Heatmap
fig.add_trace(go.Heatmap(
    z=acf,
    colorscale='RdBu',
    zmid=0,
    name='ACF'
))

# 2. The Detected Peaks (Red Dots)
# Note: scatter x is column index, y is row index
fig.add_trace(go.Scatter(
    x=peaks[:, 1], 
    y=peaks[:, 0],
    mode='markers',
    marker=dict(color='yellow', size=8, symbol='circle-open', line=dict(width=2)),
    name='Local Maxima'
))

# 3. The Pitch Vector (Line from Center to Nearest Neighbor)
center_y, center_x = acf.shape[0]//2, acf.shape[1]//2
fig.add_trace(go.Scatter(
    x=[center_x, p_near[1]],
    y=[center_y, p_near[0]],
    mode='lines+markers',
    line=dict(color='green', width=3),
    name='Pitch Vector'
))

fig.update_layout(
    title=f"Pitch Measurement: {pitch_um*1e6:.2f} microns",
    height=600, width=600,
    yaxis=dict(scaleanchor="x", scaleratio=1) # Keep pixels square
)

fig.show("browser")



#%%

from codechembook import quickPlots as qp
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lstsq

def remove_planar_tilt(z_data):
    """
    Fits a plane (Z = aX + bY + c) to the data and subtracts it.
    Ignores NaNs during the fitting process.
    """
    # 1. Create coordinate grids (X, Y)
    rows, cols = z_data.shape
    Y, X = np.indices((rows, cols)) # Note: indices returns (row_indices, col_indices)
    
    # 2. Flatten arrays and filter out NaNs
    # We only want to fit to valid data points
    mask = np.isfinite(z_data)
    x_flat = X[mask]
    y_flat = Y[mask]
    z_flat = z_data[mask]
    
    if len(z_flat) < 3:
        raise ValueError("Not enough valid points to fit a plane.")

    # 3. Build the Design Matrix (A) for Z = aX + bY + c
    # The equation is A * [a, b, c] = Z
    # A columns are: [X coordinates, Y coordinates, Column of 1s]
    A = np.c_[x_flat, y_flat, np.ones(x_flat.shape)]
    
    # 4. Least Squares Solve
    # coeffs will contain [slope_x, slope_y, intercept]
    coeffs, _, _, _ = lstsq(A, z_flat)
    a, b, c = coeffs
    
    # 5. Generate the plane for the whole image (including where NaNs were)
    plane_fit = a * X + b * Y + c
    
    # 6. Subtract the plane
    z_corrected = z_data - plane_fit
    
    return z_corrected, plane_fit

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lstsq
from skimage.filters import threshold_otsu

def remove_quadratic_tilt(z_data, mask=None):
    """
    Fits a quadratic surface to the data and subtracts it.
    
    Parameters:
    - z_data: 2D numpy array of height values.
    - mask: Boolean array. TRUE means "use this pixel for fitting".
            FALSE means "ignore this pixel" (e.g., it's a pillar).
            If None, fits to all valid finite pixels.
    """
    rows, cols = z_data.shape
    Y, X = np.indices((rows, cols))
    
    # 1. Define the mask for FITTING
    # Start with all finite values
    fit_mask = np.isfinite(z_data)
    
    # If a custom mask is provided (e.g., only background), combine it
    if mask is not None:
        fit_mask = fit_mask & mask

    # 2. Extract fitting points
    x_flat = X[fit_mask]
    y_flat = Y[fit_mask]
    z_flat = z_data[fit_mask]
    
    if len(z_flat) < 6:
        raise ValueError("Not enough points to fit a quadratic surface.")

    # 3. Design Matrix for Quadratic: [1, x, y, x^2, y^2, xy]
    # We use ones_like simply to match the shape for the intercept column
    A = np.c_[np.ones_like(x_flat), x_flat, y_flat, x_flat**2, y_flat**2, x_flat*y_flat]
    
    # 4. Solve Least Squares
    coeffs, _, _, _ = lstsq(A, z_flat)
    c0, c1, c2, c3, c4, c5 = coeffs
    
    # 5. Generate the surface for the WHOLE image (unmasked)
    # We use the full X and Y grids here
    z_surf = (c0 + 
              c1*X + c2*Y + 
              c3*X**2 + c4*Y**2 + 
              c5*X*Y)
    
    # 6. Subtract
    z_corrected = z_data - z_surf
    
    return z_corrected, z_surf

# --- EXAMPLE WORKFLOW: The "2-Pass" Approach ---

# 1. Generate Dummy Data (Bowed Surface + Steps)
y, x = np.indices((100, 100))
# The "Bowl" distortion
distortion = 0.005 * ((x-50)**2 + (y-50)**2) 
true_pattern = np.zeros((100, 100))
true_pattern[30:70, 30:70] = 20 # The Pillar
# Combine
raw_data = true_pattern + distortion + np.random.normal(0, 0.5, (100, 100))

# --- STEP 1: Rough Linear Leveling ---
# (We do this just to make Otsu work reliably)
from scipy.signal import detrend
# Simple linear detrend is usually enough for the first pass
# Or use the remove_planar_tilt function from previous turn

# --- STEP 2: Identify Features (Otsu) ---
thresh = threshold_otsu(raw_zs)
# We assume Valleys are the "Background" we want to fit to.
# So we create a mask where True = Valley.
background_mask = raw_zs < thresh

# --- STEP 3: Robust Quadratic Fit ---
# Pass the mask so we ONLY fit the curve to the valleys, ignoring the pillar
final_data, fitted_curve = remove_quadratic_tilt(raw_zs, mask=background_mask)




qp.quickHist(final_data.flatten())
#%%


fig = make_subplots(specs=[[{'type': 'surface'}]])
fig.add_trace(go.Surface(
    z=np.array(zs),
    x=np.linspace(0, len(zs[0]), len(zs[0])),
    y=np.linspace(0, len(zs), len(zs)),
    colorscale = [[0, "lightgrey"],[1, "lightgrey"]], # use a uniform color
    surfacecolor = np.zeros_like(zs), # makes an array of zeros for the surface, which accesses the 0 value of the colorscale.
    showscale = False,
    lighting = dict(
        ambient = 0.2, # ranges from 0-1, ambient lighting
        roughness = 1, # ranges from 0-1, amount of light scattered
        diffuse = 1, # ranges from 0-1, if the light is scattered at many angles
        fresnel = 0, # ranges from 0-5, used to wash light over area.
        specular = 0, # range from 0-2, higher values introduce more bright spots. 
        )
    ), # end of surface
) # end of add_trace




fig.show("browser")


#%%