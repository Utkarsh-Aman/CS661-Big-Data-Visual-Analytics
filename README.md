# CS661 Assignment 2: Interactive Volume Visualization

An interactive volume visualization dashboard built using **Plotly**, **PyVista**, and **ipywidgets** in a Jupyter Notebook.

## Features

1. **Interactive 3D Isosurface Plot**: Displays a 3D isosurface generated from the 3D scalar volume dataset using a single shell at the selected isovalue. The surface uses the `plasma` colormap, shifting visually as the isovalue changes.
2. **Dynamic 2D Histogram**: Visualizes the distribution of scalar values. When the isovalue is adjusted via the slider, the histogram dynamically updates to show only data points within `[isovalue - 0.25, isovalue + 0.25]` range, rescaled to this narrower window.
3. **Isovalue Slider Widget**: A slider mapped to the entire dataset range (from `-0.993554` to `0.432802`) with a step size of `0.01` to interactively explore different isosurface shells.
4. **Reset Button**: Reverts the dashboard to its initial state:
   - Slider value is reset to `0.0`.
   - Isosurface is updated to `0.0`.
   - Histogram reverts to show the entire volume dataset.

## Dataset

* **File**: `mixture.vti` (VTK Image Data)
* **Description**: 3D scalar field volume data from a turbulence/mixture simulation.
* **Dimensions**: 75 x 75 x 75 grid points (421,875 points total).
* **Bounds**: X, Y, Z coordinates range from `0.00` to `149.00`.
* **Scalar Range**: `[-0.993554, 0.432802]`.

## Prerequisites

create a virtual environment
```bash
python -m venv .venv
```

activate the venv
```bash
.venv\Scripts\activate
```

To run this dashboard locally, ensure you have Python installed along with the required libraries. You can install the dependencies using `pip`:

```bash
pip install numpy pyvista plotly ipywidgets vtk jupyter
```

## Running the Dashboard

Start the Jupyter Notebook server in this directory:

```bash
python -m notebook --ip=127.0.0.1 --port=8888
```

Open the printed URL in your browser and run all cells in `Interactive_Volume_Visualization.ipynb`.

## Submission Guidelines

Zip the notebook and the dataset using the naming convention:
```bash
38_241114_240790_241173_Assignment2.zip
```
