import streamlit as st
import subprocess
import os
import shutil
from py3Dmol import view
import time

from PIL import Image

# Load images
logo = Image.open("logo.png").resize((100, 100), Image.BILINEAR)  # Resize the logo
#sbb = Image.open("sbb.png").resize((100, 100), Image.BILINEAR)
your_picture = Image.open("hmh.png").resize((100, 100), Image.BILINEAR)
mentor_picture = Image.open("hmr.png").resize((100, 100), Image.BILINEAR)

company_name = "BioInfoQuant"
tagline = "Decoding the Blueprint of Life for a Healthier Future"

# Allow rendering of HTML content
st.set_option('deprecation.showfileUploaderEncoding', False)

# Create a layout with three columns
col1, col2 = st.columns([1, 6])

# Column 1: Logo
with col1:
    st.image(logo, width=100)

# Column 2: Company Name and Tagline
with col2:
    st.markdown(
        f"<h2 style='text-align: center; font-family: Times New Roman, Times, serif;'>{company_name}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h6 style='text-align: center;'>{tagline}</h6>",
        unsafe_allow_html=True
    )

# Column 3: SBB
#with col3:
#    st.image(sbb, width=100)

st.markdown("---")

# Title of the app
st.markdown(
    "<h1 style='text-align: center; padding: 20px; font-size: 40px; font-family: Times New Roman, Times, serif;'>BioDockX</h1>",
    unsafe_allow_html=True
)

# Introduction and instructions
st.markdown(
    "<h8 style='text-align: justify; padding: 20px;'>BioDockX is a powerful tool designed to facilitate molecular docking and virtual screening using AutoDock Vina. "
    "Upload your protein and ligand files, configure docking parameters, and visualize results with ease.</h8> "
    "<u><p style='text-align: center;'>To get started, please follow the steps outlined below.</p></u>",
    unsafe_allow_html=True
)
st.markdown("---")


# Ensure the uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Function to run docking with grid box parameters and log results
def run_docking(protein_file, ligand_file, output_file, log_file, config_file=None, center_x=None, center_y=None, center_z=None, size_x=None, size_y=None, size_z=None):
    command = ["vina", "--receptor", protein_file, "--ligand", ligand_file, "--out", output_file]
    if config_file:
        command += ["--config", config_file]
    else:
        if center_x and center_y and center_z:
            command += ["--center_x", str(center_x), "--center_y", str(center_y), "--center_z", str(center_z)]
        if size_x and size_y and size_z:
            command += ["--size_x", str(size_x), "--size_y", str(size_y), "--size_z", str(size_z)]
    
    # Simulating progress for the animation
    with st.spinner('Docking in progress...'):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.4)  # Slowed down progress indicator
            progress.progress(i + 1)
        result = subprocess.run(command, capture_output=True, text=True)
        with open(log_file, 'w') as log_f:
            log_f.write(result.stdout)
            log_f.write(result.stderr)
    
    if result.returncode != 0:
        st.error(f"Error in docking: {result.stderr}")
    return output_file

# Function to run virtual screening
def virtual_screening(protein_file, ligand_files, log_file, config_file=None, center_x=None, center_y=None, center_z=None, size_x=None, size_y=None, size_z=None):
    results = []
    for ligand_file in ligand_files:
        output_file = os.path.join("uploads", f"docked_{os.path.basename(ligand_file)}")
        result = run_docking(protein_file, ligand_file, output_file, log_file, config_file, center_x, center_y, center_z, size_x, size_y, size_z)
        results.append(result)
    return results

# Function to visualize molecule
def visualize_molecule(molecule_file):
    mol_view = view(width=800, height=600)
    with open(molecule_file) as f:
        mol_view.addModel(f.read(), 'pdbqt')
    mol_view.setStyle({'stick': {}})
    mol_view.zoomTo()
    return mol_view.show()

# Function to parse log file for binding energies and last 11 lines
def parse_log_file(log_file):
    binding_energies = []
    log_tail = []
    with open(log_file) as log_f:
        lines = log_f.readlines()
        for line in lines:
            if "REMARK VINA RESULT" in line:
                parts = line.split()
                if len(parts) >= 4:
                    binding_energies.append(float(parts[3]))
        log_tail = lines[-14:]  # Get the last 11 lines
    return binding_energies, log_tail

# Clear all uploads and reset app
def clear_uploads():
    shutil.rmtree("uploads")
    os.makedirs("uploads")
    st.experimental_rerun()

# Streamlit UI
#st.title("Docking App with Vina")

col1, col2, col3 = st.columns([1, 4, 1])

with col3:
    if st.button("Reset App"):
        clear_uploads()


#st.header("Protein PDBQT")
st.markdown("<h2 style='text-align: center;'>Protein PDBQT</h2>", unsafe_allow_html=True)

protein_file = st.file_uploader("Upload protein file", type=["pdbqt"])
if protein_file:
    protein_file_path = os.path.join("uploads", protein_file.name)
    with open(protein_file_path, "wb") as f:
        f.write(protein_file.getbuffer())
    st.write("Protein file uploaded.")

#st.header("Ligand PDBQT")
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Ligand PDBQT</h2>", unsafe_allow_html=True)

ligand_file = st.file_uploader("Upload ligand file", type=["pdbqt"])
if ligand_file:
    ligand_file_path = os.path.join("uploads", ligand_file.name)
    with open(ligand_file_path, "wb") as f:
        f.write(ligand_file.getbuffer())
    st.write("Ligand file uploaded.")

#st.header("Docking Configuration")
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Gridbox Configuration</h2>", unsafe_allow_html=True)

use_config_file = st.checkbox("Use configuration file for grid box settings")
config_file = None
if use_config_file:
    config_file = st.file_uploader("Upload config file", type=["txt"])
    if config_file:
        config_file_path = os.path.join("uploads", config_file.name)
        with open(config_file_path, "wb") as f:
            f.write(config_file.getbuffer())
else:
    center_x = st.number_input("Center X", value=0.0)
    center_y = st.number_input("Center Y", value=0.0)
    center_z = st.number_input("Center Z", value=0.0)
    size_x = st.number_input("Size X", value=20.0)
    size_y = st.number_input("Size Y", value=20.0)
    size_z = st.number_input("Size Z", value=20.0)

#st.header("Docking")
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Dock using Vina</h2>", unsafe_allow_html=True)

if st.button("Run Docking"):
    if not protein_file or not ligand_file:
        st.error("Please upload both protein and ligand files.")
    else:
        docked_file = os.path.join("uploads", "docked.pdbqt")
        log_file = os.path.join("uploads", "docking.log")
        if use_config_file:
            run_docking(protein_file_path, ligand_file_path, docked_file, log_file, config_file_path)
        else:
            run_docking(protein_file_path, ligand_file_path, docked_file, log_file, center_x=center_x, center_y=center_y, center_z=center_z, size_x=size_x, size_y=size_y, size_z=size_z)
        st.write(f"Docking completed. Results saved in {docked_file}.")
        st.write(visualize_molecule(docked_file))

        binding_energies, log_tail = parse_log_file(log_file)
        st.write("Binding Energies:")
        for energy in binding_energies:
            st.write(f"{energy} kcal/mol")
        
        st.write("Log File Contents (Last 11 lines):")
        log_contents = "\n".join(log_tail)
        st.text_area(label="", value=log_contents, height=200)
        
        with open(log_file, "r") as file:
            log_data = file.read()
        st.download_button("Download Log File", data=log_data, file_name="docking.log")

if 'virtual_screening' not in st.session_state:
    st.session_state['virtual_screening'] = False
#st.sidebar.markdown("---")
if st.button("Toggle Virtual Screening"):
    st.session_state['virtual_screening'] = not st.session_state['virtual_screening']

if st.session_state['virtual_screening']:
    st.header("Virtual Screening")
    ligand_files = st.file_uploader("Upload ligand files", type=["pdbqt"], accept_multiple_files=True)
    if st.button("Run Virtual Screening"):
        if not protein_file or not ligand_files:
            st.error("Please upload the protein file and at least one ligand file.")
        else:
            ligand_file_paths = []
            for ligand_file in ligand_files:
                ligand_file_path = os.path.join("uploads", ligand_file.name)
                with open(ligand_file_path, "wb") as f:
                    f.write(ligand_file.getbuffer())
                ligand_file_paths.append(ligand_file_path)
            log_file = os.path.join("uploads", "virtual_screening.log")
            if use_config_file:
                results = virtual_screening(protein_file_path, ligand_file_paths, log_file, config_file_path)
            else:
                results = virtual_screening(protein_file_path, ligand_file_paths, log_file, center_x=center_x, center_y=center_y, center_z=center_z, size_x=size_x, size_y=size_y, size_z=size_z)
            st.write("Virtual screening completed.")
            for result in results:
                st.write(visualize_molecule(result))
            
            binding_energies, log_tail = parse_log_file(log_file)
            st.write("Binding Energies:")
            for energy in binding_energies:
                st.write(f"{energy} kcal/mol")
            
            st.write("Log File Contents (Last 11 lines):")
            for line in log_tail:
                st.text(line)
            
            st.download_button("Download Log File", data=open(log_file).read(), file_name="virtual_screening.log")

st.markdown("---")
#st.header("Download Results")
# Create a layout with three columns to place the button on the right side
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("Compile All Results"):
        shutil.make_archive('uploads', 'zip', 'uploads')
        with open('uploads.zip', 'rb') as f:
            st.download_button('Download All Results', data=f, file_name='results.zip')




# Credits
st.markdown("---")
st.header("Developed by:")
col1, col2 = st.columns(2)
col1.write("   ")
col2.write("   ")

col1, col2 = st.columns(2)
col2.image(your_picture, width=100, use_column_width=False)
col1.image(mentor_picture, width=100, use_column_width=False)

col1, col2 = st.columns(2)
col2.markdown("<h6 style='text-align: left;'>Hafiz Muhammad Hammad</h6>", unsafe_allow_html=True)
col1.markdown("<h6 style='text-align: left;'>Dr. Hafiz Muzzammel Rehman</h6>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col2.markdown("<p style='text-align: left; font-size: 11px;'>CEO/CTO BioInfoQuant</p>", unsafe_allow_html=True)
col1.markdown("<p style='text-align: left; font-size: 11px;'>School of Biochemistry and Biotechnology</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col2.write("hammad@bioinfoquant.com")
col1.write("muzzammel.phd.ibb@pu.edu.pk")
