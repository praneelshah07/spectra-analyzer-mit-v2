import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.style import use
use('fast')
import json
import random
from scipy.signal import find_peaks

# Set up the Streamlit app
st.title("Spectra Visualization App")
st.write("Upload your chemical data in CSV format to start analyzing.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)

    # Convert JSON string to lists and normalize the spectra
    data['Raw_Spectra_Intensity'] = data['Raw_Spectra_Intensity'].apply(json.loads)
    data['Raw_Spectra_Intensity'] = data['Raw_Spectra_Intensity'].apply(np.array)
    data['Normalized_Spectra_Intensity'] = data['Raw_Spectra_Intensity'].apply(lambda x: x / max(x))

    # Preview the dataframe to ensure data is loaded correctly
    st.write(data.head())

    # Select SMILES for molecules you want to highlight
    unique_smiles = data['SMILES'].unique()
    selected_smiles = st.multiselect('Select molecules by SMILES to highlight:', unique_smiles)

    # Add a checkbox to enable or disable peak finding
    peak_finding_enabled = st.checkbox('Enable Peak Finding and Labeling', value=False)

    # Initialize plot with adjusted DPI for better resolution
    fig, ax = plt.subplots(figsize=(16, 6.5), dpi=100)

    # Calculate wavelength
    wavenumber = np.arange(4000, 500, -1)
    wavelength = 10000 / wavenumber  # in microns

    # Color palette for highlighted spectra
    color_palette = ['r', 'g', 'b', 'c', 'm', 'y']  # Add more colors if needed
    random.shuffle(color_palette)  # Shuffle colors to randomize highlights

    # Plot the spectra
    target_spectra = {}  # Store selected spectra for highlighting
    for smiles, spectra in data[['SMILES', 'Normalized_Spectra_Intensity']].values:
        if smiles in selected_smiles:
            target_spectra[smiles] = spectra  # Store for highlighting later
        else:
            ax.fill_between(wavelength, 0, spectra, color="k", alpha=0.01)  # Plot all other spectra

    # Highlight the selected spectra with different colors and annotate peaks if enabled
    for i, smiles in enumerate(target_spectra):
        spectra = target_spectra[smiles]
        ax.fill_between(wavelength, 0, spectra, color=color_palette[i % len(color_palette)], 
                        alpha=0.5, label=f"{smiles}")
        
        # If peak finding is enabled, find and annotate peaks
        if peak_finding_enabled:
            peaks, _ = find_peaks(spectra, height=0.05)  # Adjust height parameter for sensitivity
            for peak in peaks:
                peak_wavelength = wavelength[peak]
                peak_intensity = spectra[peak]
                ax.text(peak_wavelength, peak_intensity + 0.05, f'{round(peak_wavelength, 1)}', 
                        fontsize=10, ha='center', color=color_palette[i % len(color_palette)])

    # Customize plot axes and ticks
    ax.set_xscale('log')
    ax.set_xlim([2.5, 20])

    major_ticks = [3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 20]
    ax.set_xticks(major_ticks, minor=False)

    ax.tick_params(axis="x", labelsize=16)
    ax.tick_params(axis="y", labelsize=16)

    ax.set_xticks([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20])
    ax.set_xticklabels(["3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "15", "20"])

    ax.tick_params(direction="in",
                   labelbottom=True, labeltop=False, labelleft=True, labelright=False,
                   bottom=True, top=True, left=True, right=True)

    ax.set_xlabel("Wavelength ($\mu$m)", fontsize=22)
    ax.set_ylabel("Absorbance (Normalized to 1)", fontsize=22)

    # Show legend
    if selected_smiles:
        ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)
