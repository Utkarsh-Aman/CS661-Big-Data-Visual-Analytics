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
    """Parse command-line arguments for the volume rendering script."""
    parser = argparse.ArgumentParser(
        description="Volume render a 3D VTK Image Data (.vti) file."
    )

    parser.add_argument(
        "--input",
        type=str,
        default="Isabel_3D.vti",
        metavar="INPUT.vti",
        help="Path to the input 3D VTK Image Data file (.vti) [default: Isabel_3D.vti]"
    )

    parser.add_argument(
        "--phong",
        action="store_true",
        default=False,
        help="Enable Phong shading (off by default). Uses Ambient=0.5, Diffuse=0.5, Specular=0.5."
    )

    return parser.parse_args()


# ==============================================================================
# SECTION 2: DATA READING
# ==============================================================================

def read_vti_file(filepath):
    """Read a 3D VTK Image Data file (.vti) from disk."""
    print(f"\n[Step 1] Reading 3D volume file: {filepath}")

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)

    if not reader.CanReadFile(filepath):
        print(f"[ERROR] Cannot read file: {filepath}")
        sys.exit(1)

    reader.Update()
    volume_data = reader.GetOutput()

    dims = volume_data.GetDimensions()
    scalar_range = volume_data.GetScalarRange()
    spacing = volume_data.GetSpacing()

    print(f"  Volume dimensions: {dims[0]} x {dims[1]} x {dims[2]} voxels")
    print(f"  Voxel spacing:     {spacing[0]:.4f} x {spacing[1]:.4f} x {spacing[2]:.4f}")
    print(f"  Scalar range:      [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")
    print(f"  Total voxels:      {volume_data.GetNumberOfPoints():,}")

    return volume_data


# ==============================================================================
# SECTION 3: COLOR TRANSFER FUNCTION
# ==============================================================================

def create_color_transfer_function():
    """Create and configure the Color Transfer Function (CTF)."""
    print("  [CTF] Setting up Color Transfer Function with 6 control points...")

    color_tf = vtk.vtkColorTransferFunction()

    # Exact control points from assignment PDF
    color_tf.AddRGBPoint(-4931.54,  0.0,  1.0,  1.0)   # Cyan
    color_tf.AddRGBPoint(-2508.95,  0.0,  0.0,  1.0)   # Blue
    color_tf.AddRGBPoint(-1873.90,  0.0,  0.0,  0.5)   # Dark Blue
    color_tf.AddRGBPoint(-1027.16,  1.0,  0.0,  0.0)   # Red
    color_tf.AddRGBPoint( -298.031, 1.0,  0.4,  0.0)   # Orange
    color_tf.AddRGBPoint( 2594.97,  1.0,  1.0,  0.0)   # Yellow

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
    """Create and configure the Opacity (Alpha) Transfer Function."""
    print("  [OTF] Setting up Opacity Transfer Function with 3 control points...")

    opacity_tf = vtk.vtkPiecewiseFunction()

    # Exact control points from assignment PDF
    opacity_tf.AddPoint(-4931.54,  1.0)
    opacity_tf.AddPoint(  101.815, 0.002)
    opacity_tf.AddPoint( 2594.97,  0.0)

    print("         Data Value   Opacity")
    print("         ----------   -------")
    print("         -4931.54     1.000")
    print("          101.815     0.002")
    print("          2594.97     0.000")

    return opacity_tf


# ==============================================================================
# SECTION 5: VOLUME PROPERTY
# ==============================================================================

def create_volume_property(color_tf, opacity_tf, enable_phong):
    """Create the vtkVolumeProperty which bundles all appearance settings."""
    shading_label = "ON" if enable_phong else "OFF"
    print(f"  [VP]  Setting up Volume Property (Phong shading: {shading_label})...")

    volume_property = vtk.vtkVolumeProperty()

    volume_property.SetColor(color_tf)
    volume_property.SetScalarOpacity(opacity_tf)
    volume_property.SetInterpolationTypeToLinear()

    if enable_phong:
        volume_property.ShadeOn()
        # Assignment requirement: all coefficients set to 0.5
        volume_property.SetAmbient(0.5)
        volume_property.SetDiffuse(0.5)
        volume_property.SetSpecular(0.5)

        print("         Phong shading is ENABLED:")
        print("           Ambient  = 0.5")
        print("           Diffuse  = 0.5")
        print("           Specular = 0.5")
    else:
        volume_property.ShadeOff()

    return volume_property


# ==============================================================================
# SECTION 6: VOLUME MAPPER
# ==============================================================================

def create_volume_mapper(volume_data):
    """Create a vtkSmartVolumeMapper to connect volume data to the renderer."""
    print("  [Mapper] Setting up Smart Volume Mapper...")

    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(volume_data)

    return mapper


# ==============================================================================
# SECTION 7: OUTLINE FILTER
# ==============================================================================

def create_outline_actor(volume_data):
    """Create a wireframe bounding box (outline) around the volume."""
    print("  [Outline] Creating bounding box outline with vtkOutlineFilter...")

    outline_filter = vtk.vtkOutlineFilter()
    outline_filter.SetInputData(volume_data)
    outline_filter.Update()

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline_filter.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)
    outline_actor.GetProperty().SetLineWidth(1.5)

    return outline_actor


# ==============================================================================
# SECTION 8: RENDERING PIPELINE ASSEMBLY AND DISPLAY
# ==============================================================================

def setup_and_render(volume_data, volume_property, mapper, enable_phong):
    """Assemble the full VTK rendering pipeline and display the render window."""
    print("\n[Step 6] Assembling rendering pipeline and displaying result...")

    volume_actor = vtk.vtkVolume()
    volume_actor.SetMapper(mapper)
    volume_actor.SetProperty(volume_property)

    outline_actor = create_outline_actor(volume_data)

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume_actor)
    renderer.AddActor(outline_actor)
    renderer.SetBackground(0.05, 0.05, 0.10)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)

    shading_label = "WITH Phong Shading" if enable_phong else "WITHOUT Phong Shading"
    render_window.SetWindowName(f"CS661 Assignment 1 -- Volume Rendering ({shading_label})")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.ResetCamera()

    print(f"\n  Rendering: {shading_label}")
    print(f"  Render window: 1000 x 1000 pixels")
    print(f"\n  Opening render window... (close window or press 'q' to exit)")

    render_window.Render()
    interactor.Initialize()
    interactor.Start()

    print("\n  Render window closed.")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    print("=" * 65)
    print("  CS661 Assignment 1 -- Part 2: Volume Rendering")
    print("=" * 65)

    args = parse_arguments()

    print(f"\nRun parameters:")
    print(f"  Input file    : {args.input}")
    print(f"  Phong shading : {'Enabled' if args.phong else 'Disabled'}")

    volume_data = read_vti_file(args.input)

    print("\n[Step 2-5] Configuring transfer functions and rendering pipeline...")

    color_tf = create_color_transfer_function()
    opacity_tf = create_opacity_transfer_function()
    volume_property = create_volume_property(color_tf, opacity_tf, args.phong)
    mapper = create_volume_mapper(volume_data)

    setup_and_render(volume_data, volume_property, mapper, args.phong)

    print("\n" + "=" * 65)
    print("  Volume rendering complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()
