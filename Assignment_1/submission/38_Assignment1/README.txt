================================================================================
  CS661 - Big Data Visual Analytics
  Assignment 1: Isocontour and Volume Visualization
  Group Number: 38
  Team Members: Utkarsh Aman (241114)
                Praveen (240709)
                Vishakha sharma (241173)
  All the codes are written by all three of us with almost equal contribution but
  this submission is done by Utkarsh.
  CITATIONS: resources provided in class lectures (especially 5 & 6).
  USE OF AI Tools: for readme.txt from plain english to beautification for proper readability.
  No AI was used for the code writing BUT for understanding the concepts of resources.
  NO CODE FROM THE INTERNET WAS USED DIRECTLY IN THE CODE HOWEVER SOME
  CODE STRUCTURE MAY BE SIMILAR TO SOME ONLINE RESOURCES AND LECTURES BUT AT BASIC LEVEL ONLY. 
================================================================================

--------------------------------------------------------------------------------
  REQUIREMENTS
--------------------------------------------------------------------------------

  - Python 3.11 or later  (tested with Python 3.11)
  - pip (comes with Python)
  - VTK library (vtk >= 9.x)

  Dataset files (Included in zip):
    - Isabel_2D.vti  → for Part 1 (contour.py)
    - Isabel_3D.vti  → for Part 2 (volume_render.py)

--------------------------------------------------------------------------------
  QUICK START SUMMARY (COPY-PASTE COMMANDS) (Detailed walk-through is in the sections below)
--------------------------------------------------------------------------------

  # 1. Navigate to the submission folder
  cd path/to/38_Assignment1

  # 2. Create and activate virtual environment
  python -m venv .venv
  .venv\Scripts\activate          # Windows(my system)
  # source .venv/bin/activate     # Linux/macOS

  # 3. Install VTK
  pip install vtk

  # 4. Run Part 1 (isocontour,give correct path to dataset)(default isovalue is -200 and input file is Isabel_2D.vti)
  python contour.py  

  OR for custom input file, isovalue and output file  

  python contour.py --input path/to/Isabel_2D.vti --isovalue -200 --output contour_-200.vtp

  # 5. Run Part 2 (volume rendering, no shading,give correct path to dataset)(default input file is Isabel_3D.vti)
  python volume_render.py

  OR for custom input file

  python volume_render.py --input path/to/Isabel_3D.vti

  # 6. Run Part 2 (volume rendering, with Phong shading,give correct path to dataset)
  python volume_render.py --phong

  OR for custom input file
  
  python volume_render.py --input path/to/Isabel_3D.vti --phong



This README describes in detail on how to set up and run the two Python scripts
submitted for Assignment 1.

--------------------------------------------------------------------------------
  CONTENTS 
--------------------------------------------------------------------------------

  38_Assignment1/
  ├── contour.py        - Part 1: 2D Isocontour Extraction 
  ├── volume_render.py  - Part 2: Volume Rendering          
  └── README.txt        - This file
  ├── Isabel_2D.vti   -> Dataset for part 1 (path provided by user in execution by default it is in the same directory as the scripts)
  ├── Isabel_3D.vti   -> Dataset for part 2 (path provided by user in execution by default it is in the same directory as the scripts)
  ├── .venv           -> Virtual environment folder (created by the grader i am not zipping it)
  ├── FINAL_IMAGE     -> IMAGE downloaded from paraview presenting data and 4 contour lines.

#below are created after running the scripts (multiple of them can be created by changing the isovalue and output file name)
  ├── contour_-200.vtp -> Output of part 1 for isovalue = -200
  ├── contour_-900.vtp -> Output of part 1 for isovalue = -900
  ├── contour_100.vtp -> Output of part 1 for isovalue = 100
  ├── volume_rendering_no_phong.png -> Output of part 2 (no phong shading)
  └── volume_rendering_phong.png    -> Output of part 2 (with phong shading)

Note: The .venv/ folder (virtual environment) must be created 
      using the instructions above. It is not included in the zip file.


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

  Verify activation (should see (.venv) in your prompt).

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

  Should see a version number like: 9.x.x

--------------------------------------------------------------------------------
  STEP 3: RUN PART 1 — 2D ISOCONTOUR EXTRACTION (contour.py)
--------------------------------------------------------------------------------

  DESCRIPTION:
    contour.py extracts isocontour line segments from a 2D scalar field
    stored in a VTK Image Data (.vti) file.

  COMMAND FORMAT:
    python contour.py --input <path/to/Isabel_2D.vti> --isovalue <VALUE> --output <output.vtp>

  PARAMETERS:
    --input    : Path to the input Isabel_2D.vti file(default Isabel_2D.vti)
    --isovalue : A floating point number for the scalar isovalue (default -200)
                 Valid range for Isabel_2D.vti: approximately -1438 to 630
    --output   : Path for the output .vtp file(default contour_-200.vtp) 
                 The file will be written in VTK XML PolyData format.

  EXAMPLES:
  #by default the input file is Isabel_2D.vti , isovalue is -200 and output file is contour_-200.vtp

    Example 1 (isovalue = -200):
      python contour.py --input Isabel_2D.vti --isovalue -200 --output contour_-200.vtp

    Example 2 (isovalue = 100):
      python contour.py --input Isabel_2D.vti --isovalue 100 --output contour_100.vtp

    Example 3 (if data is in a different directory but i have submitted the data along with the script so you dont have to change it):
      python contour.py --input ../Data/Isabel_2D.vti --isovalue -200 --output contour.vtp

  EXPECTED OUTPUT(As per testing):
    - A .vtp file is created at the specified output path.
    - The terminal prints progress messages and the number of segments generated.
    - Example terminal output:

(.venv) PS C:\Users\utkar\Desktop\projects\CS661\Assignment_CS661\Assignment_1\submission\38_Assignment1> python contour.py --input Isabel_2D.vti --isovalue -200 --output contour_-200.vtp
Reading input file: Isabel_2D.vti
Scalar data range: [-1434.859, 630.569]
Extracting isocontour for isovalue = -200...
Extraction complete: generated 500 points and 250 line segments
Successfully wrote output file: contour_-200.vtp

A FILE HAS GENERATED NAMED contour_-200.vtp IN THE SAME DIRECTORY AS THE PYTHON FILE(i.e. /38_Assignment1/)

  HOW TO VISUALIZE IN PARAVIEW:
    1. Open ParaView.
    2. File → Open → select output .vtp file generated.
    3. Click "Apply" in the Properties panel.
    4. The isocontour lines will appear in the 3D view.
    

--------------------------------------------------------------------------------
  STEP 4: RUN PART 2 — VOLUME RENDERING (volume_render.py)
--------------------------------------------------------------------------------

  DESCRIPTION:
    volume_render.py performs ray-casting volume rendering of a 3D scalar
    field using VTK's vtkSmartVolumeMapper. It sets up specific color and
    opacity transfer functions and optionally enables Phong shading.

  COMMAND FORMAT (WITHOUT Phong shading — default):
    python volume_render.py

  or if data is else where
    python volume_render.py --input <path/to/Isabel_3D.vti>

  COMMAND FORMAT (WITH Phong shading):
    python volume_render.py --phong

  or if data is else where
  python volume_render.py --input <path/to/Isabel_3D.vti> --phong

  PARAMETERS:
    --input  : Path to the input Isabel_3D.vti file(default Isabel_3D.vti)
    --phong  : Optional flag. If provided, enables Phong shading with:
               Ambient=0.5, Diffuse=0.5, Specular=0.5

  EXAMPLES:
  default valuve of input file is Isabel_3D.vti

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
    The script will exit once close the window (or press 'q').

--------------------------------------------------------------------------------
  TRANSFER FUNCTION VALUES (PART 2) same as given in assignment
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
  TROUBLESHOOTING THAT I FACED DURING DEVELOPMENT
--------------------------------------------------------------------------------

  Q: "ModuleNotFoundError: No module named 'vtk'"
  A: The virtual environment may not be activated, or VTK is not installed.
     Activate .venv and run: pip install vtk

  Q: "Cannot read file: Isabel_2D.vti"
  A: Provide the correct path to the .vti file. Use an absolute path or
     make sure the file is in the same directory as the script.
     For safety and easier execution i am zipping the dataset to the
     same directory as the script.

  Q: The volume render window opens but is black/empty
  A: VTK may need a few seconds to render. Try pressing 'r' to reset the
     camera. Also check that the .vti file loaded correctly (check terminal).
     This happened with one of my teammate because of his old laptop.


