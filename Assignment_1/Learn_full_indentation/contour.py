#!/usr/bin/env python3
"""
contour.py - 2D Isocontour Extraction from VTK Image Data
CS661 Assignment 1, Part 1 [80 Points]

This script implements a SIMPLIFIED version of the Marching Squares algorithm
to extract isocontours from a 2D scalar field stored in VTK Image Data format.

KEY RESTRICTION:
    We do NOT use vtkContourFilter or any existing VTK isocontour filter.
    All contour extraction logic is implemented from scratch.

Algorithm Summary:
    For each 2D grid cell (quad), we traverse its 4 edges in counterclockwise
    order starting from the bottom edge. If the isocontour crosses exactly 2
    edges, we add a line segment connecting those 2 crossing points to the output.
    Ambiguous cases (4 crossings) are skipped per assignment instructions.

Usage:
    python contour.py --input <input.vti> --isovalue <value> --output <output.vtp>

Example:
    python contour.py --input data/Isabel_2D.vti --isovalue -200 --output contour.vtp

Dataset isovalue range for Isabel_2D.vti: approximately (-1438, 630)

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
    Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Object with attributes:
            - input  (str):   Path to the input .vti file
            - isovalue (float): The scalar isovalue for contour extraction
            - output (str):   Path for the output .vtp file
    """
    parser = argparse.ArgumentParser(
        description=(
            "Extract 2D isocontour from a VTK Image Data file using a\n"
            "simplified Marching Squares algorithm (no VTK contour filter)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python contour.py --input Isabel_2D.vti --isovalue -200 --output contour.vtp
  python contour.py --input Isabel_2D.vti --isovalue 100  --output contour_100.vtp
  python contour.py --input Isabel_2D.vti --isovalue -900 --output contour_neg900.vtp

Note:
  Valid isovalue range for Isabel_2D.vti is approximately (-1438, 630).
  Values outside this range will produce an empty contour.
        """
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        metavar="INPUT.vti",
        help="Path to the input VTK Image Data file (.vti)"
    )
    parser.add_argument(
        "--isovalue",
        type=float,
        required=True,
        metavar="VALUE",
        help="The scalar isovalue at which to extract the contour (e.g. -200)"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        metavar="OUTPUT.vtp",
        help="Path for the output VTK PolyData file (.vtp), readable in ParaView"
    )

    args = parser.parse_args()

    # ---- Validate output extension ----
    if not args.output.lower().endswith(".vtp"):
        print("[WARNING] Output file does not end with '.vtp'.")
        print("          ParaView expects the .vtp extension to load the file correctly.")

    return args


# ==============================================================================
# SECTION 2: VTK IMAGE DATA READER
# ==============================================================================

def read_vti_file(filepath):
    """
    Read a VTK Image Data file (.vti) and return the resulting vtkImageData.

    LEARNING NOTE:
        vtkXMLImageDataReader is the standard VTK class for reading .vti files.
        These files store data on a regular (uniform) structured grid where:
          - Every grid point is equally spaced in X and Y
          - Each grid point holds one or more scalar/vector values

        After calling reader.Update(), the pipeline executes and the data is
        loaded into memory. reader.GetOutput() returns the vtkImageData object.

        Key vtkImageData attributes we use later:
          - GetDimensions()  -> (nx, ny, nz): number of POINTS in each axis
          - GetPoint(id)     -> (x, y, z): 3D world coordinate of a grid point
          - GetScalarRange() -> (min, max): range of all scalar values
          - GetPointData().GetScalars() -> the scalar array

    Args:
        filepath (str): Path to the .vti file.

    Returns:
        vtk.vtkImageData: The loaded image data.

    Exits:
        If the file cannot be read or contains no data.
    """
    print(f"\n[Step 1] Reading input file: {filepath}")

    # Create and configure the XML Image Data reader
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)

    # Validate the file can be read before executing
    if not reader.CanReadFile(filepath):
        print(f"[ERROR] Cannot read file: {filepath}")
        print("        Make sure the file exists and is a valid .vti file.")
        sys.exit(1)

    # Execute the VTK pipeline -- this triggers actual file I/O
    reader.Update()

    image_data = reader.GetOutput()

    # ---- Print dataset information ----
    dimensions = image_data.GetDimensions()
    spacing    = image_data.GetSpacing()
    origin     = image_data.GetOrigin()
    scalar_range = image_data.GetScalarRange()

    print(f"  Grid dimensions (points): {dimensions[0]} x {dimensions[1]} x {dimensions[2]}")
    print(f"  Grid spacing:             {spacing[0]:.4f} x {spacing[1]:.4f} x {spacing[2]:.4f}")
    print(f"  Origin:                   ({origin[0]:.4f}, {origin[1]:.4f}, {origin[2]:.4f})")
    print(f"  Number of cells:          {image_data.GetNumberOfCells()}")
    print(f"  Scalar data range:        [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")

    return image_data


# ==============================================================================
# SECTION 3: EDGE CROSSING DETECTION
# ==============================================================================

def edge_crosses_isovalue(scalar_start, scalar_end, isovalue):
    """
    Determine whether the isocontour crosses the edge from vertex A to vertex B.

    LEARNING NOTE:
        An isocontour crosses an edge when the isovalue lies strictly between
        the scalar values at the two endpoints -- i.e., one vertex is BELOW the
        isovalue and the other is AT OR ABOVE it.

        Mathematical test:
            (scalar_start < isovalue) XOR (scalar_end < isovalue)

        This XOR (exclusive-or) is True only when exactly one side is below.

        Why strict inequality on one side?
            If a vertex sits EXACTLY on the isovalue, we classify it as "above"
            (using `< isovalue` instead of `<= isovalue`). This prevents a vertex
            that lies exactly on the contour from being counted twice -- once for
            the edge coming into it and once for the edge leaving it.

    Args:
        scalar_start (float): Scalar value at the start vertex of the edge.
        scalar_end   (float): Scalar value at the end vertex of the edge.
        isovalue     (float): The target isovalue.

    Returns:
        bool: True if the isocontour crosses this directed edge.
    """
    return (scalar_start < isovalue) != (scalar_end < isovalue)


# ==============================================================================
# SECTION 4: LINEAR INTERPOLATION
# ==============================================================================

def interpolate_crossing_point(point_start, point_end, scalar_start, scalar_end, isovalue):
    """
    Compute the exact 3D position where the isocontour crosses the edge (A -> B).

    LEARNING NOTE:
        We use LINEAR INTERPOLATION (lerp) to find the crossing point.

        The idea:
            Imagine the scalar value varies linearly along the edge from A to B.
            We want to find the parameter t  in  [0, 1] such that:

                scalar_at_t = scalar_start + t * (scalar_end - scalar_start) = isovalue

            Solving for t:
                t = (isovalue - scalar_start) / (scalar_end - scalar_start)

            Then the 3D world position of the crossing is:
                P = point_start + t * (point_end - point_start)
            
            Which expands to:
                P.x = point_start.x + t * (point_end.x - point_start.x)
                P.y = point_start.y + t * (point_end.y - point_start.y)
                P.z = point_start.z + t * (point_end.z - point_start.z)

        This is called LERP and is fundamental to all marching algorithms.
        It guarantees that the crossing point lies exactly where the interpolated
        scalar field equals the isovalue.

    Args:
        point_start (tuple): (x, y, z) coordinates of edge start vertex.
        point_end   (tuple): (x, y, z) coordinates of edge end vertex.
        scalar_start (float): Scalar value at the start vertex.
        scalar_end   (float): Scalar value at the end vertex.
        isovalue     (float): The target isovalue.

    Returns:
        tuple: (x, y, z) of the interpolated crossing point.
    """
    # Compute interpolation parameter t (how far along the edge we are)
    t = (isovalue - scalar_start) / (scalar_end - scalar_start)

    # Linearly interpolate the 3D position
    x = point_start[0] + t * (point_end[0] - point_start[0])
    y = point_start[1] + t * (point_end[1] - point_start[1])
    z = point_start[2] + t * (point_end[2] - point_start[2])

    return (x, y, z)


# ==============================================================================
# SECTION 5: CORE ISOCONTOUR EXTRACTION ALGORITHM
# ==============================================================================

def extract_isocontour(image_data, isovalue):
    """
    Extract isocontour line segments from a 2D vtkImageData using a simplified
    Marching Squares approach.

    LEARNING NOTE -- Algorithm Overview:
        This is a SIMPLIFIED version of Marching Squares. Key differences
        from the full algorithm:
          1. We do NOT use a lookup table of 16 cases.
          2. We do NOT handle ambiguous cases (4-crossing cells).
          3. Instead, we traverse edges in CCW order and collect crossings naturally.

        For each 2D cell (a rectangular quad), the algorithm does:

        STEP A -- Identify vertices:
            The 4 corners of the cell (i, j) are at grid indices:
              v0 = (i,   j  )  -> bottom-left
              v1 = (i+1, j  )  -> bottom-right
              v2 = (i+1, j+1)  -> top-right
              v3 = (i,   j+1)  -> top-left

        STEP B -- Define edges in CCW order starting from the bottom:
            Edge 0 (Bottom): v0 -> v1  (left to right along bottom)
            Edge 1 (Right):  v1 -> v2  (bottom to top along right side)
            Edge 2 (Top):    v2 -> v3  (right to left along top)
            Edge 3 (Left):   v3 -> v0  (top to bottom along left side)

            This is counterclockwise (CCW) because: right, up, left, down.

        STEP C -- Find crossing points:
            For each edge, check if the isovalue crosses it.
            If yes, compute the crossing point via linear interpolation.
            Collect all crossings for this cell.

        STEP D -- Add segment:
            0 crossings -> cell is entirely inside or outside -> skip
            2 crossings -> normal case -> add one line segment
            4 crossings -> ambiguous case -> skip (assignment requirement)

        Why CCW starting from bottom?
            The traversal order creates a consistent local orientation.
            The first crossing is always the "entry" point of the contour
            into the cell, and the second is the "exit" point, in a consistent
            sense across all cells. This produces well-oriented output.

    Args:
        image_data (vtk.vtkImageData): The 2D input scalar field.
        isovalue   (float): The scalar value at which to extract the contour.

    Returns:
        vtk.vtkPolyData: The extracted isocontour as a collection of line segments.
    """
    print(f"\n[Step 2] Extracting isocontour for isovalue = {isovalue} ...")

    # ---- Grid dimensions ----
    # LEARNING NOTE:
    #   GetDimensions() returns (nx, ny, nz) = the number of POINTS (not cells)
    #   in each direction. The number of CELLS is one less than the point count
    #   in each direction (cells live between points).
    dims = image_data.GetDimensions()
    nx = dims[0]   # Number of grid points in the X direction
    ny = dims[1]   # Number of grid points in the Y direction

    # Number of cells (quads) in each direction
    num_cells_x = nx - 1
    num_cells_y = ny - 1

    print(f"  Grid: {nx} x {ny} points  ->  {num_cells_x} x {num_cells_y} cells")
    print(f"  Total cells to process: {num_cells_x * num_cells_y}")

    # ---- Retrieve the scalar data array ----
    # LEARNING NOTE:
    #   In VTK, data arrays are stored in "field data" containers.
    #   GetPointData() returns the container for data associated with POINTS
    #   (as opposed to GetCellData() for cell-centered data).
    #   GetScalars() returns the primary scalar array from that container.
    scalars = image_data.GetPointData().GetScalars()

    if scalars is None:
        print("[ERROR] No scalar data found in the input file!")
        print("        The dataset must have point-associated scalar values.")
        sys.exit(1)

    # ---- Initialize output containers ----
    # LEARNING NOTE:
    #   vtkPoints stores the 3D coordinates (x, y, z) of all output vertices.
    #   vtkCellArray stores the connectivity information -- which points form
    #   each geometric primitive (in our case, line segments).
    #
    #   We use a GLOBAL vtkCellArray: every contour segment from every cell
    #   is inserted into this single array, as recommended by the assignment.
    output_points    = vtk.vtkPoints()   # Will hold crossing point coordinates
    output_cell_array = vtk.vtkCellArray()  # Will hold line segment connectivity

    # Statistics counters
    total_segments_added    = 0
    cells_with_no_crossing  = 0
    cells_ambiguous_skipped = 0

    # =========================================================================
    # MAIN LOOP: Iterate over every cell in the 2D grid
    # =========================================================================
    for j in range(num_cells_y):       # j = row index in the Y direction
        for i in range(num_cells_x):   # i = column index in the X direction

            # =================================================================
            # STEP A: Compute the 4 corner vertex IDs of cell (i, j)
            #
            # VTK stores grid points in ROW-MAJOR (C) order, meaning:
            #   point_id = j * nx + i
            # for grid position (i, j).
            # =================================================================

            id_v0 = j * nx + i               # Bottom-left  vertex
            id_v1 = j * nx + (i + 1)         # Bottom-right vertex
            id_v2 = (j + 1) * nx + (i + 1)   # Top-right    vertex
            id_v3 = (j + 1) * nx + i         # Top-left     vertex

            # ---- Get the 3D world coordinates of each corner ----
            # LEARNING NOTE:
            #   vtkImageData.GetPoint(id) converts the flat index into the
            #   actual (x, y, z) coordinate using the stored Origin and Spacing.
            #   For 2D data, z will be constant (e.g., 0.0).
            p0 = image_data.GetPoint(id_v0)   # (x, y, z) of bottom-left
            p1 = image_data.GetPoint(id_v1)   # (x, y, z) of bottom-right
            p2 = image_data.GetPoint(id_v2)   # (x, y, z) of top-right
            p3 = image_data.GetPoint(id_v3)   # (x, y, z) of top-left

            # ---- Get the scalar values at each corner ----
            # LEARNING NOTE:
            #   GetTuple1(id) retrieves a single-component scalar value
            #   at the given point ID. This is the pressure value at that
            #   grid point in our hurricane dataset.
            s0 = scalars.GetTuple1(id_v0)   # Scalar at bottom-left
            s1 = scalars.GetTuple1(id_v1)   # Scalar at bottom-right
            s2 = scalars.GetTuple1(id_v2)   # Scalar at top-right
            s3 = scalars.GetTuple1(id_v3)   # Scalar at top-left

            # =================================================================
            # STEP B: Define the 4 directed edges in CCW order,
            #         starting from the BOTTOM edge.
            #
            # Each tuple: (start_point_3D, end_point_3D, scalar_start, scalar_end)
            #
            # CCW traversal order:
            #   Edge 0: Bottom (v0 -> v1)  -- left to right
            #   Edge 1: Right  (v1 -> v2)  -- bottom to top
            #   Edge 2: Top    (v2 -> v3)  -- right to left
            #   Edge 3: Left   (v3 -> v0)  -- top to bottom
            # =================================================================

            edges_ccw = [
                (p0, p1, s0, s1),   # Edge 0: Bottom edge
                (p1, p2, s1, s2),   # Edge 1: Right edge
                (p2, p3, s2, s3),   # Edge 2: Top edge
                (p3, p0, s3, s0),   # Edge 3: Left edge
            ]

            # =================================================================
            # STEP C: Check each edge for isocontour crossings
            #         and collect the crossing 3D points.
            # =================================================================

            crossing_points = []   # List of (x, y, z) crossing coordinates

            for (pt_start, pt_end, sc_start, sc_end) in edges_ccw:
                if edge_crosses_isovalue(sc_start, sc_end, isovalue):
                    # Compute the precise 3D crossing point via linear interpolation
                    crossing_xyz = interpolate_crossing_point(
                        pt_start, pt_end, sc_start, sc_end, isovalue
                    )
                    crossing_points.append(crossing_xyz)

            # =================================================================
            # STEP D: Add isocontour segments to the output based on
            #         the number of crossings found.
            # =================================================================

            num_crossings = len(crossing_points)

            if num_crossings == 0:
                # The entire cell is above or below the isovalue.
                # No contour passes through this cell.
                cells_with_no_crossing += 1
                continue

            elif num_crossings == 2:
                # ---- NORMAL CASE: one contour segment through this cell ----
                #
                # LEARNING NOTE:
                #   We have exactly 2 crossing points (the contour enters and exits).
                #   We connect them as a single line segment.
                #
                #   To add a line segment to vtkCellArray:
                #     1. InsertNextPoint() adds a new 3D point and returns its ID.
                #     2. InsertNextCell(2) starts a new cell with 2 point slots.
                #     3. InsertCellPoint(id) fills each slot with a point ID.

                pt_A = crossing_points[0]   # First crossing (entry point, CCW order)
                pt_B = crossing_points[1]   # Second crossing (exit point, CCW order)

                # Add point A to the global points array
                id_A = output_points.InsertNextPoint(pt_A[0], pt_A[1], pt_A[2])

                # Add point B to the global points array
                id_B = output_points.InsertNextPoint(pt_B[0], pt_B[1], pt_B[2])

                # Add the line segment (connecting A and B) to the cell array
                output_cell_array.InsertNextCell(2)      # A line segment has 2 endpoints
                output_cell_array.InsertCellPoint(id_A)  # First endpoint of the segment
                output_cell_array.InsertCellPoint(id_B)  # Second endpoint of the segment

                total_segments_added += 1

            elif num_crossings == 4:
                # ---- AMBIGUOUS CASE: skip per assignment instructions ----
                #
                # LEARNING NOTE:
                #   4 crossings occur when the 4 corners alternate: above-below-above-below
                #   (or below-above-below-above). In this case there are two possible ways
                #   to connect the 4 crossing points into 2 segments, creating an ambiguity.
                #
                #   The traditional Marching Squares algorithm uses the "Asymptotic Decider"
                #   to resolve this, but the assignment explicitly says:
                #   "You do not have to handle the cells that have ambiguities."
                #   So we simply skip these cells.
                cells_ambiguous_skipped += 1
                continue

            # Note: 1 or 3 crossings cannot occur with our edge-crossing check
            # because we treat exact-isovalue vertices as "above", ensuring
            # each vertex is counted at most once.

    # =========================================================================
    # STEP 5: Report extraction statistics
    # =========================================================================
    print(f"\n  Extraction complete:")
    print(f"    Contour segments generated:  {total_segments_added}")
    print(f"    Cells with no crossing:      {cells_with_no_crossing}")
    if cells_ambiguous_skipped > 0:
        print(f"    Ambiguous cells skipped:     {cells_ambiguous_skipped}")

    # =========================================================================
    # STEP 6: Assemble the output vtkPolyData
    #
    # LEARNING NOTE:
    #   vtkPolyData is VTK's primary geometric data structure. It stores:
    #     - Points (vtkPoints): the 3D vertex coordinates
    #     - Cells (vtkCellArray): the connectivity (here, line segments)
    #
    #   SetPoints() attaches the coordinate array to the PolyData.
    #   SetLines() attaches the line segment connectivity array.
    #   Other methods like SetPolys() and SetVerts() are not needed here.
    # =========================================================================
    output_polydata = vtk.vtkPolyData()
    output_polydata.SetPoints(output_points)
    output_polydata.SetLines(output_cell_array)

    print(f"\n  Output PolyData:")
    print(f"    Total points:        {output_polydata.GetNumberOfPoints()}")
    print(f"    Total line segments: {output_polydata.GetNumberOfCells()}")

    return output_polydata


# ==============================================================================
# SECTION 6: VTP FILE WRITER
# ==============================================================================

def write_vtp_file(polydata, filepath):
    """
    Write vtkPolyData to disk as a VTK XML PolyData file (.vtp).

    LEARNING NOTE:
        vtkXMLPolyDataWriter writes the modern XML-based VTK PolyData format.
        This is the standard format that ParaView uses to read polydata files.

        The .vtp format stores:
          - The XML header (metadata)
          - Point coordinate data
          - Cell connectivity data

        SetDataModeToAscii() produces a human-readable text file, which is
        easier to debug. SetDataModeToBinary() would be smaller and faster
        but harder to inspect manually.

        After writing, open the .vtp file in ParaView:
          1. File -> Open -> select .vtp file
          2. Click Apply in the pipeline browser
          3. The contour lines should appear (change color if background is white)

    Args:
        polydata (vtk.vtkPolyData): The isocontour geometry to write.
        filepath (str): Full path for the output .vtp file.
    """
    print(f"\n[Step 3] Writing output to: {filepath}")

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filepath)
    writer.SetInputData(polydata)

    # Write in ASCII (text) mode for human readability and ParaView compatibility
    writer.SetDataModeToAscii()

    # Execute the write operation
    success = writer.Write()

    if success:
        print(f"  [SUCCESS] File written: {filepath}")
        print(f"  Open this file in ParaView to visualize the isocontour.")
        print(f"  Tip: In ParaView, change the display color if the background is white.")
    else:
        print(f"  [ERROR] Failed to write file: {filepath}")
        sys.exit(1)


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """
    Main entry point: orchestrates argument parsing, data reading,
    contour extraction, and output writing.
    """
    print("=" * 65)
    print("  CS661 Assignment 1 -- Part 1: 2D Isocontour Extraction")
    print("  Simplified Marching Squares (manual implementation, no VTK filter)")
    print("=" * 65)

    # ---- Parse command-line arguments ----
    args = parse_arguments()

    print(f"\nRun parameters:")
    print(f"  Input file : {args.input}")
    print(f"  Isovalue   : {args.isovalue}")
    print(f"  Output file: {args.output}")

    # ---- Step 1: Read the VTK Image Data file ----
    image_data = read_vti_file(args.input)

    # ---- Validate isovalue is within the data range ----
    scalar_range = image_data.GetScalarRange()
    if not (scalar_range[0] <= args.isovalue <= scalar_range[1]):
        print(f"\n[WARNING] Isovalue {args.isovalue} is OUTSIDE the data scalar range!")
        print(f"          Data range: [{scalar_range[0]:.3f}, {scalar_range[1]:.3f}]")
        print(f"          The output contour will likely be empty.")

    # ---- Step 2: Extract the isocontour ----
    contour_polydata = extract_isocontour(image_data, args.isovalue)

    # ---- Warn if output is empty ----
    if contour_polydata.GetNumberOfCells() == 0:
        print("\n[WARNING] No contour segments were generated!")
        print("          This may happen if the isovalue is outside the data range,")
        print("          or if the isovalue does not intersect any cell boundaries.")
        print("          Try a different isovalue.")

    # ---- Step 3: Write the output .vtp file ----
    write_vtp_file(contour_polydata, args.output)

    print("\n" + "=" * 65)
    print("  Isocontour extraction complete!")
    print("=" * 65)


# ---- Run main() when this script is executed directly ----
if __name__ == "__main__":
    main()
