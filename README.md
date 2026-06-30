# CS661 - Big Data Visual Analytics Assignments

This repository contains the programming assignments for the CS661 - Big Data Visual Analytics course.

## What it does

The repository comprises two main assignments:

**Assignment 1: Isocontour and Volume Visualization**
- **Part 1 (2D Isocontour Extraction):** Extracts isocontour line segments from a 2D scalar field (`Isabel_2D.vti`) and outputs them as VTK XML PolyData (`.vtp`).
- **Part 2 (Volume Rendering):** Performs ray-casting volume rendering of a 3D scalar field (`Isabel_3D.vti`) using VTK's `vtkSmartVolumeMapper`, featuring custom color/opacity transfer functions and optional Phong shading.

**Assignment 2: Interactive Volume Visualization**
- Provides an interactive dashboard built using **Plotly**, **PyVista**, and **ipywidgets** within a Jupyter Notebook.
- Features dynamic 3D isosurface visualization, a 2D histogram reflecting data distribution, and interactive sliders to explore different isosurface shells of a turbulence/mixture simulation (`mixture.vti`).

## File Structure

```text
Assignment_CS661/
├── Assignment_1/
│   └── submission/
│       └── 38_Assignment1/
│           ├── contour.py        # Part 1: 2D Isocontour Extraction
│           ├── volume_render.py  # Part 2: Volume Rendering
│           ├── Isabel_2D.vti     # Dataset for Part 1
│           ├── Isabel_3D.vti     # Dataset for Part 2
│           └── README.txt        # Detailed instructions for Assignment 1
├── Assignment_2/
│   ├── Interactive_Volume_Visualization.ipynb # Interactive dashboard notebook
│   ├── mixture.vti                            # Dataset for Assignment 2
│   └── README.md                              # Detailed instructions for Assignment 2
└── README.md                                  # This file
```

## How to Run

### Setup Virtual Environment
First, create and activate a virtual environment in the root directory:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate
```

### Running Assignment 1
Install the required dependencies for Assignment 1:
```bash
pip install vtk
```

Navigate to the Assignment 1 directory:
```bash
cd Assignment_1/submission/38_Assignment1
```

Run Part 1 (Isocontour):
```bash
python contour.py --input Isabel_2D.vti --isovalue -200 --output contour_-200.vtp
```

Run Part 2 (Volume Rendering with Phong shading):
```bash
python volume_render.py --input Isabel_3D.vti --phong
```

### Running Assignment 2
Install the required dependencies for Assignment 2:
```bash
pip install numpy pyvista plotly ipywidgets vtk jupyter
```

Navigate to the Assignment 2 directory:
```bash
cd Assignment_2
```

Start the Jupyter Notebook server:
```bash
python -m notebook --ip=127.0.0.1 --port=8888
```
Open the provided URL in your browser and run all cells in `Interactive_Volume_Visualization.ipynb`.
