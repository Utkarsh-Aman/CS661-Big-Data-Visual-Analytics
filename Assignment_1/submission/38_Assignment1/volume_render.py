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
    print(f"Reading input file: {filepath}")

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)

    if not reader.CanReadFile(filepath):
        print(f"Error: Cannot read file: {filepath}")
        sys.exit(1)

    reader.Update()
    volume_data = reader.GetOutput()

    return volume_data


# ==============================================================================
# SECTION 3: COLOR TRANSFER FUNCTION
# ==============================================================================

def create_color_transfer_function():
    """Create and configure the Color Transfer Function (CTF)."""
    color_tf = vtk.vtkColorTransferFunction()

    # Exact control points from assignment PDF
    color_tf.AddRGBPoint(-4931.54,  0.0,  1.0,  1.0)   # Cyan
    color_tf.AddRGBPoint(-2508.95,  0.0,  0.0,  1.0)   # Blue
    color_tf.AddRGBPoint(-1873.90,  0.0,  0.0,  0.5)   # Dark Blue
    color_tf.AddRGBPoint(-1027.16,  1.0,  0.0,  0.0)   # Red
    color_tf.AddRGBPoint( -298.031, 1.0,  0.4,  0.0)   # Orange
    color_tf.AddRGBPoint( 2594.97,  1.0,  1.0,  0.0)   # Yellow

    return color_tf


# ==============================================================================
# SECTION 4: OPACITY TRANSFER FUNCTION
# ==============================================================================

def create_opacity_transfer_function():
    """Create and configure the Opacity (Alpha) Transfer Function."""
    opacity_tf = vtk.vtkPiecewiseFunction()

    # Exact control points from assignment PDF
    opacity_tf.AddPoint(-4931.54,  1.0)
    opacity_tf.AddPoint(  101.815, 0.002)
    opacity_tf.AddPoint( 2594.97,  0.0)

    return opacity_tf


# ==============================================================================
# SECTION 5: VOLUME PROPERTY
# ==============================================================================

def create_volume_property(color_tf, opacity_tf, enable_phong):
    """Create the vtkVolumeProperty which bundles all appearance settings."""
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
    else:
        volume_property.ShadeOff()

    return volume_property


# ==============================================================================
# SECTION 6: VOLUME MAPPER
# ==============================================================================

def create_volume_mapper(volume_data):
    """Create a vtkSmartVolumeMapper to connect volume data to the renderer."""
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(volume_data)

    return mapper


# ==============================================================================
# SECTION 7: OUTLINE FILTER
# ==============================================================================

def create_outline_actor(volume_data):
    """Create a wireframe bounding box (outline) around the volume."""
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

    shading_label = "with Phong Shading" if enable_phong else "without Phong Shading"
    render_window.SetWindowName(f"CS661 Assignment 1 -- Volume Rendering ({shading_label})")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.ResetCamera()

    print(f"Opening render window ({shading_label}). Press 'q' or close window to exit.")

    render_window.Render()
    interactor.Initialize()
    interactor.Start()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    args = parse_arguments()

    print(f"Running volume rendering on {args.input} (Phong shading: {'Enabled' if args.phong else 'Disabled'})")

    volume_data = read_vti_file(args.input)

    color_tf = create_color_transfer_function()
    opacity_tf = create_opacity_transfer_function()
    volume_property = create_volume_property(color_tf, opacity_tf, args.phong)
    mapper = create_volume_mapper(volume_data)

    setup_and_render(volume_data, volume_property, mapper, args.phong)


if __name__ == "__main__":
    main()
