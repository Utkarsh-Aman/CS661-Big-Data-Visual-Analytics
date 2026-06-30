import sys
import vtk

def main():
    # 1. Read the command-line argument for the isovalue
    if len(sys.argv) < 2:
        print("Usage: python part1_isocontour.py <isovalue>")
        return
    
    try:
        isovalue = float(sys.argv[1])
    except ValueError:
        print("Error: Isovalue must be a valid float.")
        return

    print(f"Extracting isocontour for value: {isovalue}")

    # 2. Load the 2D data file using VTK 
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("Isabel_2D.vti") # Update with actual file path if needed
    reader.Update()
    
    data = reader.GetOutput()
    dims = data.GetDimensions() # Get X, Y, Z grid sizes
    scalars = data.GetPointData().GetScalars() # Fetch the Pressure values

    # 3. Create VTK elements to store the final output
    points = vtk.vtkPoints()
    cell_array = vtk.vtkCellArray()

    # Helper function to get point index in a uniform grid
    def get_point_index(i, j):
        return j * dims[0] + i

    # 4. Traverse the 2D grid cells
    for j in range(dims[1] - 1):
        for i in range(dims[0] - 1):
            
            # 5. Get the 4 corner indices in Counterclockwise Order
            # Starting from the bottom-left vertex
            idx0 = get_point_index(i, j)         # Bottom-Left
            idx1 = get_point_index(i + 1, j)     # Bottom-Right
            idx2 = get_point_index(i + 1, j + 1) # Top-Right
            idx3 = get_point_index(i, j + 1)     # Top-Left

            # Get structural spatial coordinates
            p0 = data.GetPoint(idx0)
            p1 = data.GetPoint(idx1)
            p2 = data.GetPoint(idx2)
            p3 = data.GetPoint(idx3)

            # Get scalar values (Pressure)
            v0 = scalars.GetTuple1(idx0)
            v1 = scalars.GetTuple1(idx1)
            v2 = scalars.GetTuple1(idx2)
            v3 = scalars.GetTuple1(idx3)

            # Define the 4 edges in counterclockwise order
            # (Vertex A, Vertex B, Coord A, Coord B, Value A, Value B)
            edges = [
                (idx0, idx1, p0, p1, v0, v1), # Bottom edge
                (idx1, idx2, p1, p2, v1, v2), # Right edge
                (idx2, idx3, p2, p3, v2, v3), # Top edge
                (idx3, idx0, p3, p0, v3, v0)  # Left edge
            ]

            cell_intersections = []

            # 6. Linear Interpolation to find edge intersections
            for edge in edges:
                va, vb = edge[4], edge[5]
                
                # Check if the isovalue cuts through this edge. 
                # Use a strict half-open interval rule [va, vb) to handle vertex hits 
                # and prevent double-counting across shared boundaries.
                if (va <= isovalue < vb) or (vb <= isovalue < va) or (va == isovalue == vb):
                    if va != vb: # Avoid division by zero
                        # Linear interpolation ratio t
                        t = (isovalue - va) / (vb - va)
                        # Compute exact intersection coordinate (x, y, z)
                        pa, pb = edge[2], edge[3]
                        x = pa[0] + t * (pb[0] - pa[0])
                        y = pa[1] + t * (pb[1] - pa[1])
                        z = pa[2] + t * (pb[2] - pa[2])
                        cell_intersections.append((x, y, z))
                    elif va == isovalue:
                        # If both are exactly equal to the isovalue, grab the starting point
                        cell_intersections.append(edge[2])

            # 7. Connect intersection points sequentially based on CCW traversal
            # Safe handling for standard intersections (2 points) and saddle intersections (4 points)
            if len(cell_intersections) >= 2:
                # Group points by pairs as encountered sequentially in counterclockwise travel
                for idx in range(0, len(cell_intersections) - 1, 2):
                    pt_id1 = points.InsertNextPoint(cell_intersections[idx])
                    pt_id2 = points.InsertNextPoint(cell_intersections[idx+1])
                    
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, pt_id1)
                    line.GetPointIds().SetId(1, pt_id2)
                    cell_array.InsertNextCell(line)

    # 8. Save the extracted boundaries to a VTK PolyData file (*.vtp)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(cell_array)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName("extracted_contour.vtp")
    writer.SetInputData(polydata)
    writer.Write()
    print("Contour extraction complete. Saved as 'extracted_contour.vtp'")

if __name__ == "__main__":
    main()