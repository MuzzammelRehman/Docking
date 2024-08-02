
import streamlit as st
from rdkit import Chem
from rdkit.Chem import AllChem
import py3Dmol
import subprocess
import os

# Function to run AutoDock Vina
def run_docking(protein_path, ligand_path, center, size):
    config_content = f"""
    receptor = {protein_path}
    ligand = {ligand_path}
    center_x = {center[0]}
    center_y = {center[1]}
    center_z = {center[2]}
    size_x = {size[0]}
    size_y = {size[1]}
    size_z = {size[2]}
    out = out.pdbqt
    """
    with open("config.txt", "w") as config_file:
        config_file.write(config_content)

    subprocess.run(["vina", "--config", "config.txt", "--log", "log.txt"])

# Function to visualize the docking results
def visualize_results():
    view = py3Dmol.view(width=800, height=600)
    with open("out.pdbqt") as f:
        pdbqt_data = f.read()
    view.addModel(pdbqt_data, "pdbqt")
    view.setStyle({"stick": {}})
    view.zoomTo()
    return view

# Streamlit application
st.title("Molecular Docking Tool")

# File uploaders for protein and ligand
protein_file = st.file_uploader("Upload Protein PDB File", type=["pdb"])
ligand_file = st.file_uploader("Upload Ligand PDB File", type=["pdb"])

# Input fields for docking box center and size
center_x = st.text_input("Docking Box Center X", "0")
center_y = st.text_input("Docking Box Center Y", "0")
center_z = st.text_input("Docking Box Center Z", "0")
size_x = st.text_input("Docking Box Size X", "20")
size_y = st.text_input("Docking Box Size Y", "20")
size_z = st.text_input("Docking Box Size Z", "20")

# Run docking button
if st.button("Run Docking"):
    if protein_file and ligand_file:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        
        protein_path = os.path.join("uploads", protein_file.name)
        ligand_path = os.path.join("uploads", ligand_file.name)
        
        with open(protein_path, "wb") as f:
            f.write(protein_file.getbuffer())
        
        with open(ligand_path, "wb") as f:
            f.write(ligand_file.getbuffer())
        
        center = [center_x, center_y, center_z]
        size = [size_x, size_y, size_z]
        
        run_docking(protein_path, ligand_path, center, size)
        st.success("Docking completed!")
    else:
        st.error("Please upload both protein and ligand files.")

# Visualize results button
if st.button("Visualize Results"):
    if os.path.exists("out.pdbqt"):
        view = visualize_results()
        view.show()
        st.pydeck_chart(view)
    else:
        st.error("Please run the docking process first.")
