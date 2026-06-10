#!/usr/bin/env python3
"""
volume_render.py - VTK Volume Rendering with Transfer Functions
CS661 Assignment 1, Part 2 [20 Points]

This script implements volume rendering of 3D scalar data using VTK's
ray-casting algorithm through vtkSmartVolumeMapper. It sets up specific
color and opacity transfer functions for a Hurricane Pressure dataset,
and supports optional Phong shading for advanced lighting effects.

Usage:
    python volume_render.py --input <input.vti> [--phong]

Examples:
    python volume_render.py --input data/Isabel_3D.vti
    python volume_render.py --input data/Isabel_3D.vti --phong

Phong shading parameters (when --phong is used):
    Ambient  = 0.5
    Diffuse  = 0.5
    Specular = 0.5

Author: Group 38
Course: CS661 - Big Data Visual Analytics
"""

import argparse
import sys
import vtk


# ==============================================================================
# SECTION 1: ARGUMENT PARSING
# ==============================================================================

def parse_arguments():
    """
    Parse command-line arguments for the volume rendering script.

    The script accepts:
        --input  : Path to the 3D .vti file (required)
        --phong  : Boolean flag to enable Phong shading (optional, off by default)

    Returns:
        argparse.Namespace: Parsed arguments with:
            - input (str):  Path to the input .vti file
            - phong (bool): True if --phong flag was provided, False otherwise
    """
    parser = argparse.ArgumentParser(
        description=(
            "Volume render a 3D VTK Image Data (.vti) file using VTK's\n"
            "ray-casting algorithm with configurable transfer functions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python volume_render.py --input Isabel_3D.vti
  python volume_render.py --input Isabel_3D.vti --phong

When --phong is specified, Phong shading is enabled with:
  Ambient coefficient:  0.5
  Diffuse coefficient:  0.5
  Specular coefficient: 0.5

Window controls (when the render window is open):
  Left mouse drag  : Rotate
  Right mouse drag : Zoom
  Middle mouse drag: Pan
  'r' key          : Reset camera
  'q' key          : Quit / close window
        """
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        metavar="INPUT.vti",
        help="Path to the input 3D VTK Image Data file (.vti)"
    )

    # LEARNING NOTE:
    #   action="store_true" means this is a BOOLEAN FLAG.
    #   If --phong is provided on the command line -> args.phong = True
    #   If --phong is NOT provided              -> args.phong = False (default)
    #   This pattern is the standard way to implement on/off switches in argparse.
    parser.add_argument(
        "--phong",
        action="store_true",
        default=False,
        help=(
            "Enable Phong shading for advanced lighting effects (off by default). "
            "Uses Ambient=0.5, Diffuse=0.5, Specular=0.5."
        )
    )

    return parser.parse_args()


# ==============================================================================
# SECTION 2: DATA READING
# ==============================================================================

def read_vti_file(filepath):
    """
    Read a 3D VTK Image Data file (.vti) from disk.

    LEARNING NOTE:
        This is the same vtkXMLImageDataReader used in Part 1.
        For a 3D volume, GetDimensions() returns (nx, ny, nz) where nz > 1.
        The resulting vtkImageData stores one scalar value (Pressure) per voxel.

        Volume rendering works on this 3D grid -- rays are cast through the
        volume, sampling the scalar field and accumulating color + opacity.

    Args:
        filepath (str): Path to the .vti file.

    Returns:
        vtk.vtkImageData: The loaded 3D volume data.

    Exits:
        If the file does not exist or is not readable.
    """
    print(f"\n[Step 1] Reading 3D volume file: {filepath}")
    print("         (Large files may take a few seconds to load...)")

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)

    # Verify the file is readable before attempting to load
    if not reader.CanReadFile(filepath):
        print(f"[ERROR] Cannot read file: {filepath}")
        print("        Ensure the file exists and is a valid .vti file.")
        sys.exit(1)

    # Execute the VTK pipeline -- triggers actual file I/O
    reader.Update()

    volume_data = reader.GetOutput()

    # ---- Print dataset information ----
    dims         = volume_data.GetDimensions()
    scalar_range = volume_data.GetScalarRange()
    spacing      = volume_data.GetSpacing()

    print(f"  Volume dimensions: {dims[0]} x {dims[1]} x {dims[2]} voxels")
    print(f"  Voxel spacing:     {spacing[0]:.4f} x {spacing[1]:.4f} x {spacing[2]:.4f}")
    print(f"  Scalar range:      [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")
    print(f"  Total voxels:      {volume_data.GetNumberOfPoints():,}")

    return volume_data


# ==============================================================================
# SECTION 3: COLOR TRANSFER FUNCTION
# ==============================================================================

def create_color_transfer_function():
    """
    Create and configure the Color Transfer Function (CTF) for volume rendering.

    LEARNING NOTE:
        A Color Transfer Function (CTF) maps each scalar value in the data
        to an RGB color. It acts like a color lookup table but with smooth
        PIECEWISE LINEAR interpolation between user-defined control points.

        In VTK:
          vtkColorTransferFunction stores (scalar_value -> RGB) mappings.
          AddRGBPoint(value, r, g, b) adds one control point.
          Between two control points, VTK linearly interpolates the R, G, B
          channels independently.

        The control points below are EXACTLY as specified in the assignment PDF.
        They represent a color mapping for Hurricane Pressure data:
          - Very low pressure (cold) -> cyan (0,1,1)
          - Low pressure            -> blue (0,0,1)
          - Medium-low pressure     -> dark blue (0,0,0.5)
          - Medium pressure         -> red (1,0,0)
          - Medium-high pressure    -> orange (1,0.4,0)
          - High pressure (hot)     -> yellow (1,1,0)

    Returns:
        vtk.vtkColorTransferFunction: Configured CTF with 6 control points.
    """
    print("  [CTF] Setting up Color Transfer Function with 6 control points...")

    color_tf = vtk.vtkColorTransferFunction()

    # ---- Control points from the assignment PDF ----
    # Format: AddRGBPoint(data_value, red, green, blue)
    # All RGB values are in the range [0.0, 1.0].
    color_tf.AddRGBPoint(-4931.54,  0.0,  1.0,  1.0)   # Cyan      (very low pressure)
    color_tf.AddRGBPoint(-2508.95,  0.0,  0.0,  1.0)   # Blue      (low pressure)
    color_tf.AddRGBPoint(-1873.90,  0.0,  0.0,  0.5)   # Dark Blue (med-low pressure)
    color_tf.AddRGBPoint(-1027.16,  1.0,  0.0,  0.0)   # Red       (medium pressure)
    color_tf.AddRGBPoint( -298.031, 1.0,  0.4,  0.0)   # Orange    (med-high pressure)
    color_tf.AddRGBPoint( 2594.97,  1.0,  1.0,  0.0)   # Yellow    (high pressure)

    print("         Data Value   Color")
    print("         ----------   -----")
    print("         -4931.54     Cyan       (0.0, 1.0, 1.0)")
    print("         -2508.95     Blue       (0.0, 0.0, 1.0)")
    print("         -1873.90     Dark Blue  (0.0, 0.0, 0.5)")
    print("         -1027.16     Red        (1.0, 0.0, 0.0)")
    print("          -298.031    Orange     (1.0, 0.4, 0.0)")
    print("          2594.97     Yellow     (1.0, 1.0, 0.0)")

    return color_tf


# ==============================================================================
# SECTION 4: OPACITY TRANSFER FUNCTION
# ==============================================================================

def create_opacity_transfer_function():
    """
    Create and configure the Opacity (Alpha) Transfer Function.

    LEARNING NOTE:
        An Opacity Transfer Function maps each scalar value to an opacity
        (alpha) value in the range [0.0, 1.0]:
          0.0 = fully transparent (invisible)
          1.0 = fully opaque (solid)

        VTK uses vtkPiecewiseFunction for this purpose.
        AddPoint(value, opacity) adds a control point.
        Between control points, opacity is linearly interpolated.

        In volume rendering, the opacity function controls which parts of the
        volume are "visible" -- low opacity means the viewer can see through
        that region of the volume, while high opacity makes it appear solid.

        Here:
          -4931.54 -> 1.0   : The lowest-pressure regions are fully opaque
           101.815 -> 0.002 : Mid-range pressure is nearly invisible
          2594.97  -> 0.0   : The highest-pressure regions are invisible

        This design makes the eye of the hurricane (low pressure center)
        visible while the outer high-pressure regions are transparent.

    Returns:
        vtk.vtkPiecewiseFunction: Configured opacity transfer function.
    """
    print("  [OTF] Setting up Opacity Transfer Function with 3 control points...")

    # LEARNING NOTE:
    #   vtkPiecewiseFunction is VTK's general-purpose 1D piecewise linear function.
    #   It is used here as an opacity lookup, but it can represent any mapping
    #   from a scalar value to a single output value.
    opacity_tf = vtk.vtkPiecewiseFunction()

    # ---- Control points from the assignment PDF ----
    # Format: AddPoint(data_value, opacity_value)
    opacity_tf.AddPoint(-4931.54,  1.0)    # Low pressure:  fully opaque
    opacity_tf.AddPoint(  101.815, 0.002)  # Mid pressure:  nearly transparent
    opacity_tf.AddPoint( 2594.97,  0.0)    # High pressure: completely transparent

    print("         Data Value   Opacity")
    print("         ----------   -------")
    print("         -4931.54     1.000  (fully opaque)")
    print("          101.815     0.002  (nearly transparent)")
    print("          2594.97     0.000  (invisible)")

    return opacity_tf


# ==============================================================================
# SECTION 5: VOLUME PROPERTY
# ==============================================================================

def create_volume_property(color_tf, opacity_tf, enable_phong):
    """
    Create the vtkVolumeProperty which bundles all appearance settings.

    LEARNING NOTE:
        vtkVolumeProperty is the central appearance configuration object
        for volume rendering. It holds:
          1. Color Transfer Function   -> maps values to colors
          2. Opacity Transfer Function -> maps values to transparency
          3. Interpolation type        -> how to sample between voxels
          4. Shading settings          -> whether to compute lighting

        PHONG SHADING:
            Phong shading (also called "gradient-based lighting") uses the
            local gradient of the scalar field as a surface normal proxy.
            This creates the illusion of a solid surface with proper lighting
            (highlights and shadows), making the rendering more 3D-looking.

            The Phong illumination model:
              Color = Ambient * C + Diffuse * (N*L) * C + Specular * (R*V)^n
            where:
              C = base color from the CTF
              N = estimated surface normal (from gradient)
              L = light direction
              V = view direction
              R = reflection of L about N
              n = shininess exponent

            Phong shading requires computing the gradient at every sample point,
            which makes rendering slower but more visually impressive.

    Args:
        color_tf    (vtk.vtkColorTransferFunction): Color mapping.
        opacity_tf  (vtk.vtkPiecewiseFunction):     Opacity mapping.
        enable_phong (bool): Whether to enable Phong shading.

    Returns:
        vtk.vtkVolumeProperty: Fully configured volume property.
    """
    shading_label = "ON" if enable_phong else "OFF"
    print(f"  [VP]  Setting up Volume Property (Phong shading: {shading_label})...")

    volume_property = vtk.vtkVolumeProperty()

    # Attach the color and opacity transfer functions
    volume_property.SetColor(color_tf)
    volume_property.SetScalarOpacity(opacity_tf)

    # LEARNING NOTE:
    #   SetInterpolationTypeToLinear() enables trilinear interpolation between voxels.
    #   This produces smooth gradients rather than blocky, pixelated rendering.
    #   The alternative is VTK_NEAREST_INTERPOLATION (nearest-neighbor), which is
    #   faster but produces a "Minecraft-like" blocky appearance.
    volume_property.SetInterpolationTypeToLinear()

    # ---- Configure Phong shading ----
    if enable_phong:
        # Enable gradient-based lighting (Phong shading)
        volume_property.ShadeOn()

        # Set the Phong coefficients exactly as specified in the assignment
        # LEARNING NOTE:
        #   Ambient = 0.5:  50% of color comes from ambient (non-directional) light.
        #                   This prevents areas facing away from the light being pitch black.
        #   Diffuse = 0.5:  50% of color responds to diffuse (directional, Lambert) lighting.
        #                   This creates the gradual shading from lit to shadowed regions.
        #   Specular = 0.5: 50% of color is specular (shiny highlight).
        #                   This creates the bright reflection spot on curved surfaces.
        volume_property.SetAmbient(0.5)    # Assignment requirement: 0.5
        volume_property.SetDiffuse(0.5)    # Assignment requirement: 0.5
        volume_property.SetSpecular(0.5)   # Assignment requirement: 0.5

        print("         Phong shading is ENABLED:")
        print("           Ambient  = 0.5")
        print("           Diffuse  = 0.5")
        print("           Specular = 0.5")
    else:
        # Shading off: all visible voxels use their raw color from the CTF
        # without any lighting calculation.
        volume_property.ShadeOff()
        print("         Phong shading is OFF (run with --phong to enable).")

    return volume_property


# ==============================================================================
# SECTION 6: VOLUME MAPPER
# ==============================================================================

def create_volume_mapper(volume_data):
    """
    Create a vtkSmartVolumeMapper to connect volume data to the renderer.

    LEARNING NOTE:
        vtkSmartVolumeMapper is VTK's intelligent volume rendering mapper.
        It automatically selects the best rendering technique based on
        available hardware:
          - If a capable GPU is detected -> GPU ray-casting (fast)
          - If not -> CPU-based ray-casting (slower but always works)

        This is preferable to manually choosing:
          - vtkGPUVolumeRayCastMapper (GPU only, no fallback)
          - vtkFixedPointVolumeRayCastMapper (CPU only, always slow)

        The mapper's job is to trace rays through the 3D volume,
        sampling the scalar field at regular intervals and compositing
        the color and opacity from the transfer functions along each ray.

        Ray-casting algorithm (conceptual):
          For each pixel in the render window:
            1. Cast a ray from the camera through this pixel into the volume.
            2. Sample the scalar value at regular intervals along the ray.
            3. Look up color and opacity from the transfer functions.
            4. Accumulate color and opacity using the FRONT-TO-BACK compositing:
               Color_out = Color_in + (1 - Alpha_in) * sample_color * sample_alpha
            5. Stop when accumulated opacity reaches ~1 (fully opaque) or ray exits.

    Args:
        volume_data (vtk.vtkImageData): The 3D scalar volume to render.

    Returns:
        vtk.vtkSmartVolumeMapper: Configured volume mapper.
    """
    print("  [Mapper] Setting up Smart Volume Mapper...")

    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(volume_data)

    return mapper


# ==============================================================================
# SECTION 7: OUTLINE FILTER
# ==============================================================================

def create_outline_actor(volume_data):
    """
    Create a wireframe bounding box (outline) around the volume.

    LEARNING NOTE:
        vtkOutlineFilter generates the 12 edges of the axis-aligned bounding box
        of its input dataset. The result is a vtkPolyData with 12 line segments.

        Why add an outline?
          - It shows the spatial extent of the volume in 3D space.
          - It helps the viewer understand the coordinate system and scale.
          - Without it, a semi-transparent volume can look like it's floating
            in undefined space.

        Pipeline: vtkOutlineFilter -> vtkPolyDataMapper -> vtkActor
          - vtkOutlineFilter: Computes the bounding box geometry.
          - vtkPolyDataMapper: Converts PolyData -> renderable GPU data.
          - vtkActor: Places the geometry in the 3D scene with appearance settings.

    Args:
        volume_data (vtk.vtkImageData): The volume whose bounds we want to outline.

    Returns:
        vtk.vtkActor: The outline actor ready to be added to the renderer.
    """
    print("  [Outline] Creating bounding box outline with vtkOutlineFilter...")

    # Create the filter that computes the bounding box geometry
    outline_filter = vtk.vtkOutlineFilter()
    outline_filter.SetInputData(volume_data)
    outline_filter.Update()   # Execute to produce the bounding box lines

    # Map the outline geometry to GPU-ready format
    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline_filter.GetOutputPort())

    # Create an actor to represent the outline in the scene
    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)

    # Style the outline as a white wireframe so it's visible on dark backgrounds
    outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)   # White outline
    outline_actor.GetProperty().SetLineWidth(1.5)          # Slightly thicker lines

    return outline_actor


# ==============================================================================
# SECTION 8: RENDERING PIPELINE ASSEMBLY AND DISPLAY
# ==============================================================================

def setup_and_render(volume_data, volume_property, mapper, enable_phong):
    """
    Assemble the full VTK rendering pipeline and display the render window.

    LEARNING NOTE:
        VTK's rendering architecture (the "Visualization Pipeline"):

        1. vtkVolume:
           - The 3D equivalent of vtkActor (which is used for polygonal geometry).
           - Holds the mapper (vtkSmartVolumeMapper) and property (vtkVolumeProperty).
           - This is what gets added to the renderer to make the volume visible.

        2. vtkRenderer:
           - Manages the 3D scene: actors, volumes, cameras, and lights.
           - Can contain multiple actors and volumes.
           - Has a viewport (a sub-region of the render window).
           - ResetCamera() adjusts the camera to frame all objects in the scene.

        3. vtkRenderWindow:
           - The OS-level window that the renderer draws into.
           - SetSize(1000, 1000) sets a 1000x1000 pixel window (assignment requirement).
           - Can hold multiple renderers (for split-screen views).

        4. vtkRenderWindowInteractor:
           - Captures user input events (mouse, keyboard).
           - Translates them into camera transformations (rotate, zoom, pan).
           - interactor.Start() enters the event loop, which blocks until the
             window is closed or 'q' is pressed.

    Args:
        volume_data    (vtk.vtkImageData):     The 3D volume (for outline).
        volume_property (vtk.vtkVolumeProperty): Appearance configuration.
        mapper         (vtk.vtkSmartVolumeMapper): Volume rendering mapper.
        enable_phong   (bool): Whether Phong shading is enabled (for title).
    """
    print("\n[Step 6] Assembling rendering pipeline and displaying result...")

    # ---- Create the Volume Actor ----
    # LEARNING NOTE:
    #   vtkVolume pairs a mapper and a property together into a scene object.
    #   The mapper handles HOW the data is rendered (ray-casting algorithm).
    #   The property handles WHAT it looks like (colors, opacity, shading).
    volume_actor = vtk.vtkVolume()
    volume_actor.SetMapper(mapper)
    volume_actor.SetProperty(volume_property)

    # ---- Create the Outline Actor ----
    outline_actor = create_outline_actor(volume_data)

    # ---- Create the Renderer ----
    # LEARNING NOTE:
    #   vtkRenderer is the scene manager. It holds all visible objects
    #   (actors and volumes) and manages the camera and lighting.
    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume_actor)     # Add the volume to the 3D scene
    renderer.AddActor(outline_actor)     # Add the bounding box outline

    # Set a dark background to make the colorful volume stand out
    renderer.SetBackground(0.05, 0.05, 0.10)   # Very dark blue-black

    # ---- Create the Render Window ----
    # LEARNING NOTE:
    #   vtkRenderWindow is the actual window displayed to the user.
    #   The assignment requires exactly 1000 x 1000 pixels.
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)    # Assignment requirement: 1000x1000

    # Set a descriptive window title to indicate Phong shading status
    shading_label = "WITH Phong Shading" if enable_phong else "WITHOUT Phong Shading"
    render_window.SetWindowName(
        f"CS661 Assignment 1 -- Volume Rendering ({shading_label})"
    )

    # ---- Create the Interactor ----
    # LEARNING NOTE:
    #   vtkRenderWindowInteractor enables user interaction with the 3D scene.
    #   The default interactor style supports:
    #     - Orbital rotation (left mouse drag)
    #     - Zoom (right mouse drag or scroll wheel)
    #     - Pan (middle mouse drag)
    #     - Camera reset (press 'r')
    #     - Quit (press 'q')
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # ---- Position the Camera ----
    # ResetCamera() automatically positions the camera so all objects in the
    # scene are visible, using the scene's bounding box.
    renderer.ResetCamera()

    # ---- Display rendering information ----
    print(f"\n  Rendering: {shading_label}")
    print(f"  Render window: 1000 x 1000 pixels")
    print(f"\n  Window controls:")
    print(f"    Left mouse drag   -> Rotate the volume")
    print(f"    Right mouse drag  -> Zoom in/out")
    print(f"    Middle mouse drag -> Pan")
    print(f"    'r' key           -> Reset camera to default view")
    print(f"    'q' key           -> Quit (close the window)")
    print(f"\n  Opening render window... (close window or press 'q' to exit)")

    # ---- Start the Rendering and Interaction Loop ----
    render_window.Render()        # Perform the initial render
    interactor.Initialize()       # Set up the interactor
    interactor.Start()            # Enter the event loop (blocks until window is closed)

    print("\n  Render window closed.")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """
    Main entry point: orchestrates argument parsing, pipeline setup, and rendering.
    """
    print("=" * 65)
    print("  CS661 Assignment 1 -- Part 2: Volume Rendering")
    print("  VTK Ray-Casting via vtkSmartVolumeMapper")
    print("=" * 65)

    # ---- Parse command-line arguments ----
    args = parse_arguments()

    print(f"\nRun parameters:")
    print(f"  Input file    : {args.input}")
    print(f"  Phong shading : {'Enabled (--phong flag detected)' if args.phong else 'Disabled (no --phong flag)'}")

    # ---- Step 1: Read the 3D volume data ----
    volume_data = read_vti_file(args.input)

    print("\n[Step 2-5] Configuring transfer functions and rendering pipeline...")

    # ---- Step 2: Create the Color Transfer Function ----
    color_tf = create_color_transfer_function()

    # ---- Step 3: Create the Opacity Transfer Function ----
    opacity_tf = create_opacity_transfer_function()

    # ---- Step 4: Create the Volume Property ----
    # (bundles CTF + OTF + shading settings)
    volume_property = create_volume_property(color_tf, opacity_tf, args.phong)

    # ---- Step 5: Create the Volume Mapper ----
    mapper = create_volume_mapper(volume_data)

    # ---- Step 6: Set up the rendering scene and display it ----
    setup_and_render(volume_data, volume_property, mapper, args.phong)

    print("\n" + "=" * 65)
    print("  Volume rendering complete.")
    print("=" * 65)


# ---- Run main() when this script is executed directly ----
if __name__ == "__main__":
    main()
