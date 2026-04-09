# VKS OSS Projects Landscape

This repository contains the configuration and scripts to generate a custom CNCF-style landscape for the open-source projects used in VMware vSphere Kubernetes Service (VKS) and the Supervisor.

## Prerequisites

1. **Python 3**: Required to run the generation script.
2. **landscape2 CLI**: The official CNCF landscape builder. 
   - Installation instructions: [landscape2 GitHub](https://github.com/cncf/landscape2)

## Directory Structure

- `vks-entries.txt`: The list of projects to include in the landscape.
- `landscape-template.yml`: The master CNCF landscape data file used as the source of truth.
- `generate_landscape.py`: Python script that reads `vks-entries.txt`, extracts the relevant data from the template, generates `landscape.yml`, and downloads the necessary logos.
- `settings.yml`: Configuration file for the `landscape2` CLI (controls UI, colors, categories, etc.).
- `landscape.yml`: (Auto-generated) The filtered landscape data for VKS.
- `hosted_logos/`: (Auto-generated) Directory containing the downloaded SVG logos.
- `build/`: (Auto-generated) The compiled static website.

## How to Update the Landscape

If you want to add or remove projects from the landscape, follow these steps:

### 1. Update the Project List
Open `vks-entries.txt` and add or remove project names. 
*Note: The names must exactly match how they appear in the CNCF landscape (e.g., `Project Calico`, not just `Calico`).*

### 2. Generate the Data and Logos
Run the Python script to update the `landscape.yml` file and fetch any missing logos:
```bash
python3 generate_landscape.py
```

### 3. Build the Website
Use the `landscape2` CLI to compile the static website into the `build/` directory:
```bash
landscape2 build \
  --data-file landscape.yml \
  --settings-file settings.yml \
  --logos-path hosted_logos \
  --output-dir build
```

### 4. Serve the Website Locally
Start a local web server to view your landscape:
```bash
landscape2 serve --landscape-dir build
```
Open your browser and navigate to **http://127.0.0.1:8000**.
