================================================================================
  CS661 - Big Data Visual Analytics
  Assignment 1: Isocontour and Volume Visualization
  Group Number: 38
================================================================================

This README describes exactly how to set up and run the two Python scripts
submitted for Assignment 1.

--------------------------------------------------------------------------------
  CONTENTS OF THIS SUBMISSION
--------------------------------------------------------------------------------

  38_Assignment1/
  ├── contour.py        - Part 1: 2D Isocontour Extraction [80 pts]
  ├── volume_render.py  - Part 2: Volume Rendering          [20 pts]
  └── README.txt        - This file

Note: The .venv/ folder (virtual environment) must be created by the grader
      using the instructions below. It is not included in the zip file.

--------------------------------------------------------------------------------
  REQUIREMENTS
--------------------------------------------------------------------------------

  - Python 3.11 or later  (tested with Python 3.11)
  - pip (comes with Python)
  - VTK library (vtk >= 9.x)

  Dataset files (NOT included in zip, must be placed separately):
    - Isabel_2D.vti  → for Part 1 (contour.py)
    - Isabel_3D.vti  → for Part 2 (volume_render.py)

--------------------------------------------------------------------------------
  STEP 1: SET UP THE VIRTUAL ENVIRONMENT
--------------------------------------------------------------------------------

  Open a terminal (Command Prompt or PowerShell) and navigate to the submission
  folder (the folder containing contour.py and volume_render.py).

  On Windows:
  -----------
  Create the virtual environment:
    python -m venv .venv

  Activate the virtual environment:
    .venv\Scripts\activate

  Verify activation (you should see (.venv) in your prompt).

  On Linux / macOS:
  -----------------
  Create the virtual environment:
    python3 -m venv .venv

  Activate the virtual environment:
    source .venv/bin/activate

--------------------------------------------------------------------------------
  STEP 2: INSTALL DEPENDENCIES
--------------------------------------------------------------------------------

  With the virtual environment ACTIVATED, install VTK:

    pip install vtk

  This will install the VTK library and all its dependencies.
  VTK is a large package (~200 MB); installation may take a few minutes.

  Verify VTK is installed correctly:
    python -c "import vtk; print(vtk.vtkVersion.GetVTKVersion())"

  You should see a version number like: 9.x.x

--------------------------------------------------------------------------------
  STEP 3: RUN PART 1 — 2D ISOCONTOUR EXTRACTION (contour.py)
--------------------------------------------------------------------------------

  DESCRIPTION:
    contour.py extracts isocontour line segments from a 2D scalar field
    stored in a VTK Image Data (.vti) file. It implements a simplified
    Marching Squares algorithm WITHOUT using VTK's built-in contour filters.

  COMMAND FORMAT:
    python contour.py --input <path/to/Isabel_2D.vti> --isovalue <VALUE> --output <output.vtp>

  PARAMETERS:
    --input    : Path to the input Isabel_2D.vti file (required)
    --isovalue : A floating point number for the scalar isovalue (required)
                 Valid range for Isabel_2D.vti: approximately -1438 to 630
    --output   : Path for the output .vtp file (required)
                 The file will be written in VTK XML PolyData format.

  EXAMPLES:

    Example 1 (isovalue = -200):
      python contour.py --input Isabel_2D.vti --isovalue -200 --output contour_-200.vtp

    Example 2 (isovalue = -900):
      python contour.py --input Isabel_2D.vti --isovalue -900 --output contour_-900.vtp

    Example 3 (isovalue = 100):
      python contour.py --input Isabel_2D.vti --isovalue 100 --output contour_100.vtp

    Example 4 (if data is in a different directory):
      python contour.py --input ../Data/Isabel_2D.vti --isovalue -200 --output contour.vtp

  EXPECTED OUTPUT:
    - A .vtp file is created at the specified output path.
    - The terminal prints progress messages and the number of segments generated.
    - Example terminal output:
        [Step 1] Reading input file: Isabel_2D.vti
          Grid dimensions (points): 500 x 500 x 1
          Scalar data range: [-1438.xxx, 630.xxx]
        [Step 2] Extracting isocontour for isovalue = -200.0 ...
          Contour segments generated: XXXX
        [Step 3] Writing output to: contour_-200.vtp
          [SUCCESS] File written: contour_-200.vtp

  HOW TO VISUALIZE IN PARAVIEW:
    1. Open ParaView.
    2. File → Open → select your output .vtp file.
    3. Click "Apply" in the Properties panel.
    4. The isocontour lines will appear in the 3D view.
    5. If the background is white, change the contour color:
       Properties → Coloring → Solid Color → choose a visible color (e.g., red).

--------------------------------------------------------------------------------
  STEP 4: RUN PART 2 — VOLUME RENDERING (volume_render.py)
--------------------------------------------------------------------------------

  DESCRIPTION:
    volume_render.py performs ray-casting volume rendering of a 3D scalar
    field using VTK's vtkSmartVolumeMapper. It sets up specific color and
    opacity transfer functions and optionally enables Phong shading.

  COMMAND FORMAT (WITHOUT Phong shading — default):
    python volume_render.py --input <path/to/Isabel_3D.vti>

  COMMAND FORMAT (WITH Phong shading):
    python volume_render.py --input <path/to/Isabel_3D.vti> --phong

  PARAMETERS:
    --input  : Path to the input Isabel_3D.vti file (required)
    --phong  : Optional flag. If provided, enables Phong shading with:
               Ambient=0.5, Diffuse=0.5, Specular=0.5

  EXAMPLES:

    Example 1 (without Phong shading):
      python volume_render.py --input Isabel_3D.vti

    Example 2 (with Phong shading):
      python volume_render.py --input Isabel_3D.vti --phong

    Example 3 (data in a different directory):
      python volume_render.py --input ../Data/Isabel_3D.vti --phong

  EXPECTED BEHAVIOR:
    - A 1000x1000 pixel render window opens showing the volume rendering.
    - The volume is colored according to the transfer functions specified
      in the assignment (cyan → blue → dark blue → red → orange → yellow).
    - A white bounding box outline surrounds the volume.
    - Window title shows whether Phong shading is ON or OFF.
    - Note: Initial rendering of 3D data may take a few seconds.

  INTERACTIVE WINDOW CONTROLS:
    Left mouse button + drag  → Rotate the volume
    Right mouse button + drag → Zoom in/out
    Scroll wheel              → Zoom in/out
    Middle mouse + drag       → Pan (translate)
    'r' key                   → Reset camera to default view
    'q' key                   → Quit (close the window)

  NOTE:
    The volume rendering window is INTERACTIVE — it does not close automatically.
    The script will exit once you close the window (or press 'q').

--------------------------------------------------------------------------------
  TRANSFER FUNCTION VALUES (PART 2)
--------------------------------------------------------------------------------

  Color Transfer Function:
    Data Value   | Red  | Green | Blue
    -------------|------|-------|------
    -4931.54     | 0.0  | 1.0   | 1.0   (Cyan)
    -2508.95     | 0.0  | 0.0   | 1.0   (Blue)
    -1873.90     | 0.0  | 0.0   | 0.5   (Dark Blue)
    -1027.16     | 1.0  | 0.0   | 0.0   (Red)
     -298.031    | 1.0  | 0.4   | 0.0   (Orange)
     2594.97     | 1.0  | 1.0   | 0.0   (Yellow)

  Opacity Transfer Function:
    Data Value   | Opacity
    -------------|--------
    -4931.54     | 1.000
     101.815     | 0.002
     2594.97     | 0.000

  Phong Shading (when --phong is used):
    Ambient  = 0.5
    Diffuse  = 0.5
    Specular = 0.5

--------------------------------------------------------------------------------
  QUICK START SUMMARY (COPY-PASTE COMMANDS)
--------------------------------------------------------------------------------

  # 1. Navigate to the submission folder
  cd path/to/38_Assignment1

  # 2. Create and activate virtual environment
  python -m venv .venv
  .venv\Scripts\activate          # Windows
  # source .venv/bin/activate     # Linux/macOS

  # 3. Install VTK
  pip install vtk

  # 4. Run Part 1 (isocontour)
  python contour.py --input path/to/Isabel_2D.vti --isovalue -200 --output contour.vtp

  # 5. Run Part 2 (volume rendering, no shading)
  python volume_render.py --input path/to/Isabel_3D.vti

  # 6. Run Part 2 (volume rendering, with Phong shading)
  python volume_render.py --input path/to/Isabel_3D.vti --phong

--------------------------------------------------------------------------------
  DATASET INFORMATION
--------------------------------------------------------------------------------

  The data used in this assignment is a Hurricane Simulation dataset.
  Source: http://vis.computer.org/vis2004contest/index.html

  Isabel_2D.vti:
    - A 2D slice from a 3D Hurricane simulation
    - Variable: Pressure
    - Format: VTK XML Image Data (.vti)
    - Isovalue range: approximately -1438 to 630

  Isabel_3D.vti:
    - A 3D volume from a Hurricane simulation
    - Variable: Pressure
    - Format: VTK XML Image Data (.vti)

--------------------------------------------------------------------------------
  TROUBLESHOOTING
--------------------------------------------------------------------------------

  Q: "ModuleNotFoundError: No module named 'vtk'"
  A: The virtual environment may not be activated, or VTK is not installed.
     Activate .venv and run: pip install vtk

  Q: "Cannot read file: Isabel_2D.vti"
  A: Provide the correct path to the .vti file. Use an absolute path or
     make sure the file is in the same directory as the script.

  Q: The contour .vtp file is empty (0 segments)
  A: The isovalue may be outside the data range. Run contour.py to see the
     scalar range printed, then choose an isovalue within that range.

  Q: The volume render window opens but is black/empty
  A: VTK may need a few seconds to render. Try pressing 'r' to reset the
     camera. Also check that the .vti file loaded correctly (check terminal).

  Q: The render window is slow to open
  A: Isabel_3D.vti is a large 3D dataset (~25 MB). Loading and initial
     rendering may take 10-30 seconds depending on hardware.

================================================================================
  END OF README
================================================================================
