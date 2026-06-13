#!/usr/bin/env python3
"""
contour.py - 2D Isocontour Extraction from VTK Image Data
CS661 Assignment 1, Part 1 [80 Points]

This script extracts isocontours from a 2D scalar field stored in VTK Image Data
format by manually traversing edges in CCW order to detect crossings.


Usage:
    python contour.py --input <input.vti> --isovalue <value> --output <output.vtp>

    or simply 
    python contour.py
    (this will use default values for input file, isovalue and output file)

"""

import argparse
import sys
import vtk



# SECTION 1: ARGUMENT PARSING


def parse_arguments():
    # parse and validate command line arguments.
    parser = argparse.ArgumentParser(
        description="Extract 2D isocontour by manually traversing edges in CCW order to detect crossings."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="Isabel_2D.vti",
        metavar="INPUT.vti",
        help="Path to the input VTK Image Data file (.vti) [default: Isabel_2D.vti]"
    )
    parser.add_argument(
        "--isovalue",
        type=float,
        default=-200,
        metavar="VALUE",
        help="The scalar isovalue at which to extract the contour [default: -200]"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="contour_-200.vtp",
        metavar="OUTPUT.vtp",
        help="Path for the output VTK PolyData file (.vtp) [default: contour_-200.vtp]"
    )
    # parser.add_argument()

    args = parser.parse_args()

    return args




# SECTION 2: VTK IMAGE DATA READER


def read_vti_file(filepath):
    #read a VTK Image Data file (.vti) and return the vtkImageData.
    print(f"\n[Step 1] Reading input file: {filepath}")

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)

    if not reader.CanReadFile(filepath):
        print(f"[ERROR] Cannot read file: {filepath}")
        sys.exit(1)

    reader.Update()
    image_data = reader.GetOutput()

    dimensions = image_data.GetDimensions()
    spacing = image_data.GetSpacing()
    origin = image_data.GetOrigin()
    scalar_range = image_data.GetScalarRange()

    print(f"  Grid dimensions (points): {dimensions[0]} x {dimensions[1]} x {dimensions[2]}")
    print(f"  Grid spacing:             {spacing[0]:.4f} x {spacing[1]:.4f} x {spacing[2]:.4f}")
    print(f"  Origin:                   ({origin[0]:.4f}, {origin[1]:.4f}, {origin[2]:.4f})")
    print(f"  Number of cells:          {image_data.GetNumberOfCells()}")
    print(f"  Scalar data range:        [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")

    return image_data



# SECTION 3: EDGE CROSSING DETECTION


def edge_crosses_isovalue(scalar_start, scalar_end, isovalue):
    # Determine whether the isocontour crosses the edge from vertex A to vertex B.
    return (scalar_start < isovalue) != (scalar_end < isovalue)


# SECTION 4: LINEAR INTERPOLATION


def interpolate_crossing_point(point_start, point_end, scalar_start, scalar_end, isovalue):
    #compute the exact 3D position where the isocontour crosses the edge.
    t = (isovalue - scalar_start) / (scalar_end - scalar_start)

    x = point_start[0] + t * (point_end[0] - point_start[0])
    y = point_start[1] + t * (point_end[1] - point_start[1])
    z = point_start[2] + t * (point_end[2] - point_start[2])

    return (x, y, z)


# SECTION 5: CORE ISOCONTOUR EXTRACTION ALGORITHM


def extract_isocontour(image_data, isovalue):
    # Extract isocontour line segments from a 2D vtkImageData.
    print(f"\n[Step 2] Extracting isocontour for isovalue = {isovalue} ...")

    dims = image_data.GetDimensions()
    nx = dims[0]
    ny = dims[1]

    num_cells_x = nx - 1
    num_cells_y = ny - 1

    print(f"  Grid: {nx} x {ny} points  ->  {num_cells_x} x {num_cells_y} cells")
    print(f"  Total cells to process: {num_cells_x * num_cells_y}")

    scalars = image_data.GetPointData().GetScalars()
    if scalars is None:
        print("[ERROR] No scalar data found in the input file!")
        sys.exit(1)

    output_points = vtk.vtkPoints()
    output_cell_array = vtk.vtkCellArray()

    total_segments_added = 0
    cells_with_no_crossing = 0
    cells_ambiguous_skipped = 0

    for j in range(num_cells_y):
        for i in range(num_cells_x):

            # Compute corner IDs
            id_v0 = j * nx + i
            id_v1 = j * nx + (i + 1)
            id_v2 = (j+ 1) * nx + (i + 1)
            id_v3 = (j + 1) * nx + i

            # Coordinates
            p0 = image_data.GetPoint(id_v0)
            p1 = image_data.GetPoint(id_v1)
            p2 = image_data.GetPoint(id_v2)
            p3 = image_data.GetPoint(id_v3)

            # Scalars
            s0 = scalars.GetTuple1(id_v0)
            s1 = scalars.GetTuple1(id_v1)
            s2 = scalars.GetTuple1(id_v2)
            s3 = scalars.GetTuple1(id_v3)

            # Traverse 4 edges in CCW order starting from bottom edge
            edges_ccw = [
                (p0, p1, s0, s1),   # Bottom
                (p1, p2, s1, s2),   # Right
                (p2, p3, s2, s3),   # Top
                (p3, p0, s3, s0),   # Left
            ]

            crossing_points = []
            for (pt_start, pt_end, sc_start, sc_end) in edges_ccw:
                if edge_crosses_isovalue(sc_start, sc_end, isovalue):
                    crossing_xyz = interpolate_crossing_point(
                        pt_start, pt_end, sc_start, sc_end, isovalue
                    )
                    crossing_points.append(crossing_xyz)

            num_crossings = len(crossing_points)

            if num_crossings == 0:
                cells_with_no_crossing += 1
                continue

            elif num_crossings == 2:
                # Normal case: Add the single line segment connecting the two points
                pt_A = crossing_points[0]
                pt_B = crossing_points[1]

                id_A = output_points.InsertNextPoint(pt_A[0], pt_A[1], pt_A[2])
                id_B = output_points.InsertNextPoint(pt_B[0], pt_B[1], pt_B[2])

                output_cell_array.InsertNextCell(2)
                output_cell_array.InsertCellPoint(id_A)
                output_cell_array.InsertCellPoint(id_B)

                total_segments_added += 1

            elif num_crossings == 4:
                # Ambiguous case: Skipped per assignment instructions
                cells_ambiguous_skipped += 1
                continue

    print(f"\n  Extraction complete:")
    print(f"    Contour segments generated:  {total_segments_added}")
    print(f"    Cells with no crossing:      {cells_with_no_crossing}")
    if cells_ambiguous_skipped > 0:
        print(f"    Ambiguous cells skipped:     {cells_ambiguous_skipped}")

    output_polydata = vtk.vtkPolyData()
    output_polydata.SetPoints(output_points)
    output_polydata.SetLines(output_cell_array)

    print(f"\n  Output PolyData:")
    print(f"    Total points:        {output_polydata.GetNumberOfPoints()}")
    print(f"    Total line segments: {output_polydata.GetNumberOfCells()}")

    return output_polydata



# SECTION 6: VTP FILE WRITER


def write_vtp_file(polydata, filepath):
    # Write vtkPolyData to disk as a VTK XML PolyData file (.vtp).
    print(f"\n[Step 3] Writing output to: {filepath}")

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filepath)
    writer.SetInputData(polydata)
    writer.SetDataModeToAscii()

    success = writer.Write()

    if success:
        print(f"  [SUCCESS] File written: {filepath}")
    else:
        print(f"  [ERROR] Failed to write file: {filepath}")
        sys.exit(1)



# MAIN ENTRY POINT


def main():
    print("=" * 65) # will print = 65 times 
    print("  CS661 Assignment 1 -- Part 1: 2D Isocontour Extraction") 
    print("=" * 65) 

    args = parse_arguments()

    print(f"\nRun parameters:")
    print(f"  Input file : {args.input}")
    print(f"  Isovalue   : {args.isovalue}")
    print(f"  Output file: {args.output}")

    image_data = read_vti_file(args.input)

    scalar_range = image_data.GetScalarRange()
    if not (scalar_range[0] <= args.isovalue <= scalar_range[1]):
        print(f"\n[WARNING] Isovalue {args.isovalue} is OUTSIDE the data scalar range!")
        print(f"          Data range: [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")

    contour_polydata = extract_isocontour(image_data, args.isovalue)

    if contour_polydata.GetNumberOfCells() == 0:
        print("\n[WARNING] No contour segments were generated!")

    write_vtp_file(contour_polydata, args.output)

    print("\n" + "=" * 65)
    print("  Isocontour extraction complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
