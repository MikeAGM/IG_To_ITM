import ezdxf
from pyproj import Transformer
import os
import tkinter as tk
from tkinter import filedialog

# Function to browse for the folder containing DXF files
def browse_input_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing DXF Files")
    return folder_path

# Function to browse for the output folder
def browse_output_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Output Folder for Converted DXF Files")
    return folder_path

# Function to convert DXF coordinates using pyproj
def convert_dxf(input_dxf_path, output_dxf_path):
    # Load the DXF file
    doc = ezdxf.readfile(input_dxf_path)
    msp = doc.modelspace()

    # Create a transformer from Irish Grid (EPSG: 29903) to ITM (EPSG: 2157)
    transformer = Transformer.from_crs("epsg:29903", "epsg:2157", always_xy=True)

    # Iterate over all entities in the modelspace
    for entity in msp:
        if entity.dxftype() == 'LINE':
            # Convert start and end points of the line
            start_x, start_y = transformer.transform(entity.dxf.start.x, entity.dxf.start.y)
            end_x, end_y = transformer.transform(entity.dxf.end.x, entity.dxf.end.y)
            entity.dxf.start = (start_x, start_y)
            entity.dxf.end = (end_x, end_y)

        elif entity.dxftype() == 'CIRCLE':
            # Convert center point of the circle
            center_x, center_y = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
            entity.dxf.center = (center_x, center_y)

        elif entity.dxftype() == 'ARC':
            # Convert center point of the arc
            center_x, center_y = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
            entity.dxf.center = (center_x, center_y)

        elif entity.dxftype() == 'LWPOLYLINE':
            # Convert all vertex points of the polyline
            for vertex in entity:
                x, y = transformer.transform(vertex[0], vertex[1])
                vertex[0] = x
                vertex[1] = y

        elif entity.dxftype() == 'POINT':
            # Convert the point coordinates
            x, y = transformer.transform(entity.dxf.location.x, entity.dxf.location.y)
            entity.dxf.location = (x, y)

        elif entity.dxftype() == 'INSERT':  # Handle block reference (INSERT)
            # Convert the block reference insertion point
            insert_x, insert_y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
            entity.dxf.insert = (insert_x, insert_y)

        elif entity.dxftype() == 'TEXT':  # Handle text entities
            # Convert the text insertion point
            text_x, text_y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
            entity.dxf.insert = (text_x, text_y)

        elif entity.dxftype() == 'MTEXT':  # Handle multiline text (MTEXT)
            # Convert the MTEXT insertion point
            mtext_x, mtext_y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
            entity.dxf.insert = (mtext_x, mtext_y)

    # Save the modified DXF file to the output path
    doc.saveas(output_dxf_path)
    print(f"Converted {input_dxf_path} and saved to {output_dxf_path}")

# Main function to process multiple DXF files
def process_dxf_folder():
    # Prompt the user to select the input folder containing DXF files
    input_folder = browse_input_folder()
    if not input_folder:
        print("No folder selected. Operation cancelled.")
        return

    # Prompt the user to select the output folder
    output_folder = browse_output_folder()
    if not output_folder:
        print("No output folder selected. Operation cancelled.")
        return

    # Iterate over all DXF files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.dxf'):
            input_dxf_path = os.path.join(input_folder, file_name)

            # Create the output file name with "_[ITM]" appended
            base_name, ext = os.path.splitext(file_name)
            output_dxf_path = os.path.join(output_folder, f"{base_name}_[ITM]{ext}")

            # Convert the DXF file
            convert_dxf(input_dxf_path, output_dxf_path)

    print(f"All DXF files from {input_folder} have been converted and saved to {output_folder}.")

if __name__ == "__main__":
    process_dxf_folder()
