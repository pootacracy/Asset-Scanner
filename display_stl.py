import sys
import os
import time
from pathlib import Path

start_time = time.time()
def log_step(step):
    print(f"[{time.time() - start_time:.3f}s] {step}", flush=True)

log_step("Starting display_stl.py...")
log_step(f"Arguments: {sys.argv}")
os.environ["QT_API"] = "pyqt6"

log_step("Importing pyvista...")
try:
    import pyvista as pv
    log_step("PyVista imported successfully.")
    PYVISTA_AVAILABLE = True
except ImportError:
    log_step("PyVista import failed.")
    PYVISTA_AVAILABLE = False
except Exception as e:
    log_step(f"An error occurred during PyVista import: {e}")
    PYVISTA_AVAILABLE = False

if __name__ == "__main__":
    if not PYVISTA_AVAILABLE:
        print("Missing PyVista dependency. Please `pip install pyvista`.")
        sys.exit(1)
        
    if len(sys.argv) < 3:
        print("Usage: python display_stl.py <path_to_stl> <output_dir>")
        sys.exit(1)
        
    stl_file = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    
    log_step(f"Reading STL file: {stl_file}")
    try:
        mesh = pv.read(stl_file)
        log_step(f"Mesh loaded: {mesh.n_points} points, {mesh.n_cells} cells")
    except Exception as e:
        log_step(f"Failed to load STL: {e}")
        sys.exit(1)

    log_step("Initializing Plotter...")
    # We store rotation states natively
    plotter = pv.Plotter(title=f"STL Preview - {stl_file.name}")
    plotter.window_size = (800, 600)
    plotter.set_background("#16161E", top="#292E42") # A sleek dark mode gradient
    log_step("Plotter initialized.")
    
    # Lightweight parameters for fast rotation
    fast_kwargs = {
        'color': 'lightblue',         # Standard named color to avoid VTK hex parsing failures
        'smooth_shading': False       # STLs often lack normals; smooth=True renders them black
    }
    
    # We must compute normals if we want any lighting to look good, but to be safe and performant:
    actor = plotter.add_mesh(mesh, **fast_kwargs)
    
    # Disable Eye Dome Lighting in preview mode because it artificially darkens 2D overlays (like the reticle)
    # plotter.enable_eye_dome_lighting() 
    
    # High-quality AO parameters for the final screenshot
    hq_kwargs = {
        'color': 'white', 
        'smooth_shading': True,       # We rely on split_sharp_edges down the line for the final render
        'split_sharp_edges': True,
        'ambient': 0.15,
        'diffuse': 0.85,
        'specular': 0.05,
    }

    # Rotation state
    rot_state = {'x': 0.0, 'y': 0.0, 'z': 0.0}

    def update_rotation():
        global actor
        plotter.remove_actor(actor)
        
        rotated = mesh.copy()
        rotated.rotate_x(rot_state['x'], inplace=True)
        rotated.rotate_y(rot_state['y'], inplace=True)
        rotated.rotate_z(rot_state['z'], inplace=True)
        
        actor = plotter.add_mesh(rotated, **fast_kwargs)

    def set_x(value): rot_state['x'] = value; update_rotation()
    def set_y(value): rot_state['y'] = value; update_rotation()
    def set_z(value): rot_state['z'] = value; update_rotation()

    # Add slider widgets at the bottom of the screen
    slider_kwargs = dict(
        style='modern',
        tube_width=0.005,
        slider_width=0.03,
        color='cyan',
        title_color='white'
    )
    plotter.add_slider_widget(set_x, [0, 360], value=0, title="X Rotation", pointa=(0.05, 0.1), pointb=(0.3, 0.1), **slider_kwargs)
    plotter.add_slider_widget(set_y, [0, 360], value=0, title="Y Rotation", pointa=(0.375, 0.1), pointb=(0.625, 0.1), **slider_kwargs)
    plotter.add_slider_widget(set_z, [0, 360], value=0, title="Z Rotation", pointa=(0.7, 0.1), pointb=(0.95, 0.1), **slider_kwargs)

    # Add a custom button to save the JPEG
    def save_jpeg_key():
        # Switch to clean light studio backdrop for export
        plotter.set_background("#F9FAFB", top="#F1F5F9")
        
        # Temporarily apply high quality look for screenshot
        try:
            plotter.disable_eye_dome_lighting()
        except Exception:
            pass
            
        global actor
        plotter.remove_actor(actor)
        
        # Hide all interactive elements and overlays
        plotter.clear_slider_widgets()
        plotter.clear_button_widgets()
        if 'text1' in globals(): plotter.remove_actor(text1)
        if 'text2' in globals(): plotter.remove_actor(text2)
        plotter.remove_actor(reticle_actor)
        
        rotated = mesh.copy()
        rotated.rotate_x(rot_state['x'], inplace=True)
        rotated.rotate_y(rot_state['y'], inplace=True)
        rotated.rotate_z(rot_state['z'], inplace=True)
        
        actor = plotter.add_mesh(rotated, **hq_kwargs)
        
        try:
            plotter.enable_ssao(radius=2.0)
            plotter.enable_anti_aliasing('fxaa')
        except AttributeError:
            pass
            
        # Force a render to apply the changes
        plotter.render()
        
        img = plotter.screenshot(None, return_img=True)
        output_file = out_dir / f"{stl_file.stem}.jpg"
        
        from PIL import Image
        crop_img = Image.fromarray(img)
        w, h = crop_img.size
        
        # The reticle is exactly 400x400 relative to the 800x600 window
        reticle_size = 400
        left = (w - reticle_size) // 2
        top = (h - reticle_size) // 2
        
        # Crop exactly to the reticle boundaries
        crop_img = crop_img.crop((left, top, left + reticle_size, top + reticle_size))
        
        # Upscale it back to 600x600 natively with high-quality Lanczos to maintain file resolution
        crop_img = crop_img.resize((600, 600), Image.Resampling.LANCZOS)
        crop_img.save(str(output_file))
        
        print(f"Saved render to {output_file}")
        plotter.close()
        os._exit(0)
        
    btn_widget_ref = []

    def save_jpeg_button(state):
        if state:  # only trigger when pressed down
            save_jpeg_key()
            if btn_widget_ref:
                # Force the widget to visually release immediately
                btn_widget_ref[0].GetRepresentation().SetState(0)
    
    text1 = plotter.add_text("Press 's' to Capture Thumbnail", position="upper_left", font_size=11, color="white")
    plotter.add_key_event("s", save_jpeg_key)
    
    # Render a modern button on the screen (Top Right Corner)
    btn = plotter.add_checkbox_button_widget(
        save_jpeg_button,
        value=False,
        color_on="lightgray", 
        color_off="darkgray",
        position=(670, 540),
        size=25,
    )
    btn_widget_ref.append(btn)
    text2 = plotter.add_text("Capture", position=(705, 545), font_size=11, color="cyan")

    # Add a square visual reticle
    import vtk
    points = vtk.vtkPoints()
    # For a 400x400 reticle centered in an 800x600 window:
    points.InsertNextPoint(200, 100, 0)
    points.InsertNextPoint(600, 100, 0)
    points.InsertNextPoint(600, 500, 0)
    points.InsertNextPoint(200, 500, 0)
    points.InsertNextPoint(200, 100, 0)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(5)
    for i in range(5): lines.InsertCellPoint(i)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)
    mapper = vtk.vtkPolyDataMapper2D()
    mapper.SetInputData(polydata)
    reticle_actor = vtk.vtkActor2D()
    reticle_actor.SetMapper(mapper)
    reticle_actor.GetProperty().SetColor(1.0, 1.0, 1.0) # White viewfinder
    reticle_actor.GetProperty().SetOpacity(0.12) # Soft transparency 
    reticle_actor.GetProperty().SetLineWidth(2.0)
    plotter.add_actor(reticle_actor)

    # Zoom out appropriately so the model fits comfortably inside the new smaller 400x400 reticle
    plotter.camera.zoom(0.5)

    log_step("Opening window...")
    plotter.show()
    os._exit(0)
