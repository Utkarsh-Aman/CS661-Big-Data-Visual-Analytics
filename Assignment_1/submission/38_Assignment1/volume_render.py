import sys
import vtk

def main():
    # 1. Parse Phong Shading user preference from command-line
    if len(sys.argv) < 2:
        print("Usage: python part2_volume_render.py <use_shading: yes/no>")
        return
    
    shading_input = sys.argv[1].lower()
    use_shading = (shading_input == "yes")

    # 2. Load 3D Volume Data
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("Isabel_3D.vti")  # Ensure file matches assignment data
    reader.Update()

    # 3. Create Color Transfer Function (Strict specification matching table)
    color_tf = vtk.vtkColorTransferFunction()
    color_tf.AddRGBPoint(-4931.54, 0.0, 1.0, 1.0)
    color_tf.AddRGBPoint(-2508.95, 0.0, 0.0, 1.0)
    color_tf.AddRGBPoint(-1873.9,  0.0, 0.0, 0.5)
    color_tf.AddRGBPoint(-1027.16, 1.0, 0.0, 0.0)
    color_tf.AddRGBPoint(-298.031, 1.0, 0.4, 0.0)
    color_tf.AddRGBPoint(2594.97,  1.0, 1.0, 0.0)

    # 4. Create Opacity Transfer Function (Strict specification matching table)
    opacity_tf = vtk.vtkPiecewiseFunction()
    opacity_tf.AddPoint(-4931.54, 1.0)
    opacity_tf.AddPoint(101.815,  0.002)
    opacity_tf.AddPoint(2594.97,  0.0)

    # 5. Set Up Volume Properties and Shading
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_tf)
    volume_property.SetScalarOpacity(opacity_tf)
    volume_property.SetInterpolationTypeToLinear()

    if use_shading:
        volume_property.ShadeOn()
        volume_property.SetAmbient(0.5)   # Set required coefficients
        volume_property.SetDiffuse(0.5)   
        volume_property.SetSpecular(0.5)  
        print("Volume Rendering Profile: Phong Shading ENABLED.")
    else:
        volume_property.ShadeOff()
        print("Volume Rendering Profile: Phong Shading DISABLED.")

    # 6. Setup Smart Volume Mapper & Volume Actor
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)

    # 7. Add Bounding Box Outline Filter
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader.GetOutputPort())
    
    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())
    
    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0, 0, 0) # Black outline for crisp visibility

    # 8. Setup Rendering Stage Window (Size fixed at 1000x1000)
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)  # Mandatory resolution assignment

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Add actors to scene context
    renderer.AddViewProp(volume)
    renderer.AddActor(outline_actor)
    renderer.SetBackground(1, 1, 1)  # White background matching standard reports

    # Center camera frame configurations
    renderer.ResetCamera()
    camera = renderer.GetActiveCamera()
    camera.Zoom(1.2) # Zoom in slightly to fit nicely in 1000x1000 window

    print("Launching window. Left-click and drag inside the frame to inspect perspectives.")
    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    main()