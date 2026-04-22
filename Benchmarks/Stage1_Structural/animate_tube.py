import pyvista as pv
import os
import re
import imageio
import numpy as np

# Headless rendering configuration
pv.OFF_SCREEN = True

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def generate_animations(vtk_dir, output_3d, output_2d):
    # Setup and sort files
    files = [f for f in os.listdir(vtk_dir) if f.endswith('.vtk')]
    if not files:
        print(f"No VTK files found in {vtk_dir}")
        return
    files.sort(key=natural_sort_key)
    files = files[::2] # Downsample for efficiency (100 frames)
    
    print(f"Generating consolidated 2D and 3D animations ({len(files)} frames)...")
    
    # Plotter 3D
    plotter_3d = pv.Plotter(off_screen=True, window_size=[1024, 768])
    plotter_3d.set_background("#181818")
    
    # Plotter 2D
    plotter_2d = pv.Plotter(off_screen=True, window_size=[1200, 600])
    plotter_2d.set_background("#181818")
    
    # Common Scalar Bar settings (Premium Technical Style)
    sargs = dict(
        title="Displacement Magnitude [m]",
        title_font_size=16,
        label_font_size=12,
        color="white",
        position_x=0.25,
        position_y=0.05,
        vertical=False,
        width=0.5,
        height=0.08
    )

    # Determine global max displacement for fixed scale comparison
    # (Optional: user previously preferred dynamic, but we can stick to dynamic)
    # We will use DYNAMIC scaling as requested in the latest iterations.

    frames_3d = []
    frames_2d = []
    
    STAGE_1 = "STAGE 1: Axial Pre-stretching"
    STAGE_2 = "STAGE 2: Vertical Pinching"

    # Single processing loop for efficiency
    for i, filename in enumerate(files):
        if i % 10 == 0:
            print(f"Rendering frame {i}/{len(files)}...")
            
        mesh = pv.read(os.path.join(vtk_dir, filename))
        mesh["Mag"] = np.linalg.norm(mesh.point_data["DISPLACEMENT"], axis=1)
        warped = mesh.warp_by_vector("DISPLACEMENT", factor=1.0)
        
        idx = int(re.findall(r'\d+', filename)[1])
        current_stage = STAGE_1 if idx <= 100 else STAGE_2
        
        # --- Update 3D Frame ---
        plotter_3d.clear()
        plotter_3d.add_text(current_stage, position='upper_edge', font_size=14, color='white', name="stage_label")
        plotter_3d.add_text(f"Time: {idx*0.01:.2f}s", position='upper_right', font_size=12, color='#aaaaaa', shadow=True)
        plotter_3d.add_mesh(
            warped, scalars="Mag", cmap="plasma", smooth_shading=True,
            show_edges=False, specular=0.4, specular_power=10, scalar_bar_args=sargs, name="tube"
        )
        plotter_3d.camera_position = [(0.25, 0.2, 0.25), (0, 0, 0), (0, 1, 0)]
        plotter_3d.reset_camera()
        plotter_3d.camera.zoom(1.3) # Reverting to the 1.3 zoom as requested earlier in "Mod 2"
        frames_3d.append(plotter_3d.screenshot(None))
        
        # --- Update 2D Frame (Premium Technical Section) ---
        slice_2d = warped.slice(normal='x', origin=(0, 0, 0))
        plotter_2d.clear()
        plotter_2d.add_text(f"{current_stage} (Cross-section)", position='upper_edge', font_size=14, color='white', name="stage_label")
        plotter_2d.add_mesh(
            slice_2d, scalars="Mag", cmap="plasma", 
            show_edges=False, # Clean surface without mesh lines
            scalar_bar_args=sargs, name="tube_2d"
        )
        plotter_2d.view_zy()
        plotter_2d.reset_camera()
        plotter_2d.camera.zoom(1.2)
        frames_2d.append(plotter_2d.screenshot(None))

    print("Saving 3D GIF...")
    imageio.mimsave(output_3d, frames_3d, fps=15, loop=0)
    
    print("Saving 2D GIF...")
    imageio.mimsave(output_2d, frames_2d, fps=15, loop=0)
    
    print("All animations consolidated and saved.")

if __name__ == "__main__":
    generate_animations("vtk_output", "tube_displacement.gif", "tube_2d_displacement.gif")
