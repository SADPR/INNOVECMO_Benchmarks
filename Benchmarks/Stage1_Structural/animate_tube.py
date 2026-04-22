import pyvista as pv
import os
import re
import imageio
import numpy as np

# Use a static backend that doesn't require a GUI window
pv.OFF_SCREEN = True

def natural_sort_key(s):
    # Sorts strings containing numbers in numerical order (1, 2, 10 instead of 1, 10, 2)
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def generate_gif(vtk_dir, output_gif):
    # Get and sort VTK files
    files = [f for f in os.listdir(vtk_dir) if f.endswith('.vtk')]
    if not files:
        print(f"No VTK files found in {vtk_dir}")
        return
        
    files.sort(key=natural_sort_key)
    
    # We'll downsample to 100 frames (every 2nd file) to keep GIF size manageable 
    # and speed up rendering, but still maintain smoothness.
    files = files[::2] 
    
    print(f"Processing {len(files)} frames (downsampled for efficiency)...")

    # Initialize plotter with a dark gray background instead of pure black
    plotter = pv.Plotter(off_screen=True, window_size=[1024, 768])
    plotter.set_background("#181818") # Deep charcoal for premium look
    
    # Custom color bar settings (Horizontal, Bottom Center)
    sargs = dict(
        title="Displacement Magnitude [m]",
        title_font_size=16,
        label_font_size=12,
        color="white",
        position_x=0.25, # Centered (0.25 to 0.75)
        position_y=0.05, # Low
        vertical=False,
        width=0.5,
        height=0.08
    )

    # Determine global max displacement
    sample_steps = [0, len(files)//2, -1]
    max_val = 0
    for idx in sample_steps:
        temp_mesh = pv.read(os.path.join(vtk_dir, files[idx]))
        if "DISPLACEMENT" in temp_mesh.point_data:
            mag = np.linalg.norm(temp_mesh.point_data["DISPLACEMENT"], axis=1)
            max_val = max(max_val, mag.max())
    
    if max_val == 0: max_val = 0.01 

    frames = []
    
    # Text labels for stages
    STAGE_1 = "STAGE 1: Axial Pre-stretching"
    STAGE_2 = "STAGE 2: Vertical Pinching"

    # Initial camera setup with the first mesh to avoid "jumping"
    first_mesh = pv.read(os.path.join(vtk_dir, files[0]))
    first_mesh.point_data["Mag"] = np.linalg.norm(first_mesh.point_data["DISPLACEMENT"], axis=1)
    plotter.add_mesh(first_mesh, scalars="Mag", cmap="plasma", clim=[0, max_val], scalar_bar_args=sargs, name="tube")
    plotter.camera_position = [(0.25, 0.2, 0.25), (0, 0, 0), (0, 1, 0)]
    plotter.reset_camera()
    # No more manual zoom!

    # Animation Loop
    for i, filename in enumerate(files):
        if i % 10 == 0:
            print(f"Rendering frame {i}/{len(files)}...")
            
        mesh = pv.read(os.path.join(vtk_dir, filename))
        mesh["Mag"] = np.linalg.norm(mesh.point_data["DISPLACEMENT"], axis=1)
        warped = mesh.warp_by_vector("DISPLACEMENT", factor=1.0)
        
        # Determine stage based on filename index
        idx = int(re.findall(r'\d+', filename)[1])
        current_stage = STAGE_1 if idx <= 100 else STAGE_2
        
        plotter.clear()
        
        # Add labels and mesh
        plotter.add_text(current_stage, position='upper_edge', font_size=14, color='white', name="stage_label")
        plotter.add_text(f"Time: {idx*0.01:.2f}s", position='upper_right', font_size=12, color='#aaaaaa', shadow=True)

        plotter.add_mesh(
            warped, 
            scalars="Mag", 
            cmap="plasma", 
            # clim removed to allow dynamic color bar per frame
            scalar_bar_args=sargs,
            smooth_shading=True,
            show_edges=False,
            specular=0.4,
            specular_power=10,
            name="tube" 
        )
        
        frames.append(plotter.screenshot(None))

    print("Stitching GIF...")
    imageio.mimsave(output_gif, frames, fps=15, loop=0)
    print(f"Animation complete: {output_gif}")

if __name__ == "__main__":
    generate_gif("vtk_output", "tube_displacement.gif")
