# SIDEWALK
AISE 4020 Final Project - Sidewalk Irregularity Detection E-Robot With Autonomous Location Knowledge
This project provides a simulation, data processing, and model-training pipeline for inspecting and detecting potential cracks or defects in asphalt surfaces (such as parking lots). The workflow includes simulating a car robot’s path, training a custom YOLO model for object detection, and processing inspection videos to generate comprehensive reports with detected defects mapped onto satellite imagery.

---

## Repository Overview

The repository is organized into three main folders:

1. **Driving**  
   - **Purpose**: Simulate the path of a car robot capturing video or images of parking lots (or other paved surfaces).  
   - **Key File**: `driveSim.ipynb`  
     - Simulates the car’s movement and the path it should follow for data collection.

2. **Model Training**  
   - **Purpose**: Train a YOLO model on a road-damage dataset to detect pavement defects.  
   - **Key Points**:  
     - Contains code to load and prepare the dataset.  
     - Trains a custom YOLO model.  
     - Saves the best weights to a file named `best_yolo_model.pt`.

3. **Processing**  
   - **Purpose**: Automate the analysis of pavement inspection videos, flag potential defects, plot them on a satellite map, and generate a PDF report.  
   - **Key File**: `create_report.ipynb`  
     - Loads a custom-trained YOLO model.  
     - Processes video frames (sampling every 15th frame by default).  
     - Detects defects above a confidence threshold (≥ 40%).  
     - Draws bounding boxes on detected frames (saved in the `Frames` folder).  
     - Maps each defect to a geographic coordinate by matching timestamps to GPS data.  
     - Uses **folium** (with ArcGIS satellite tiles) to create an interactive map marking defect and non-defect locations.  
     - Automatically captures a screenshot of the map (`map.png`) using Selenium.  
     - Generates a PDF report (`pavement_report.pdf`) that includes:  
       - Title page with inspection details (date, location, total runtime, defect count, and flagged-point percentage).  
       - An embedded map image showing defect markers.  
       - Annotated defect images, their coordinates, and suspected defect type(s) with confidence levels.

---

## Installation and Requirements

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Ecook46/SIDEWALK.git
   cd SIDEWALK
2. **Install Dependencies**:
   It is recommended to use a Python virtual environment.
   Dependencies include:
   - yolov11
   - opencv-python
   - follium
   - selenium
   - matplotlib
   - reportlab
   - pandas
   - numpy
3. **Running the Project:**
   Navigate into the specific folders(e.g., Driving, Model Training or Processing)        based on your needed functionality.
   
