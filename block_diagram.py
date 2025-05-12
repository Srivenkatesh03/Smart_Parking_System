from graphviz import Digraph

# Create a directed graph
dot = Digraph("Parh11_Block_Diagram", format="jpg")
dot.attr(rankdir="TB", size="8,8", dpi="300")

# Define node attributes
node_attrs_main = {"shape": "box", "style": "filled", "color": "#ffccff", "fontsize": "12", "fontname": "Arial"}
node_attrs_data = {"shape": "ellipse", "style": "filled", "color": "#ffdddd", "fontsize": "12", "fontname": "Arial"}
node_attrs_component = {"shape": "box", "style": "rounded,filled", "color": "#bbbbff", "fontsize": "10",
                        "fontname": "Arial"}

# Add main components
dot.node("MainApp", "Main Application", **node_attrs_main)
dot.node("UserInterface", "User Interface", **node_attrs_main)
dot.node("DetectionSystem", "Detection System", **node_attrs_main)
dot.node("VehicleTracking", "Vehicle Tracking", **node_attrs_main)
dot.node("ParkingAllocation", "Parking Allocation", **node_attrs_main)
dot.node("Visualization", "Visualization", **node_attrs_main)

# Add data components
dot.node("ConfigFiles", "Configuration Files", **node_attrs_data)
dot.node("LogFiles", "Log Files", **node_attrs_data)
dot.node("DataStorage", "Data Storage", **node_attrs_data)
dot.node("VideoSources", "Video Sources", **node_attrs_data)

# Add sub-components
ui_components = ["Setup Tab", "Detection Tab", "Allocation Tab", "Log Tab", "Stats Tab", "Reference Tab"]
for ui in ui_components:
    dot.node(ui, ui, **node_attrs_component)

detection_components = ["Classical CV", "ML Detection", "Background Subtraction", "Contour Analysis", "YOLO Detector",
                        "Faster R-CNN"]
for det in detection_components:
    dot.node(det, det, **node_attrs_component)

tracking_components = ["Detection", "DeepSORT", "Vehicle Counter"]
for track in tracking_components:
    dot.node(track, track, **node_attrs_component)

allocation_components = ["XGBoost Model", "Load Balancing", "Space Optimization"]
for alloc in allocation_components:
    dot.node(alloc, alloc, **node_attrs_component)

# Add connections
dot.edges([
    # Main application links
    ("MainApp", "UserInterface"),
    ("MainApp", "DetectionSystem"),
    ("MainApp", "VehicleTracking"),
    ("MainApp", "ParkingAllocation"),
    ("MainApp", "Visualization"),
    ("MainApp", "DataStorage"),

    # External file connections
    ("ConfigFiles", "MainApp"),
    ("MainApp", "LogFiles"),
    ("VideoSources", "DetectionSystem"),
    ("VideoSources", "VehicleTracking"),

    # User interface sub-components
    ("UserInterface", "Setup Tab"),
    ("UserInterface", "Detection Tab"),
    ("UserInterface", "Allocation Tab"),
    ("UserInterface", "Log Tab"),
    ("UserInterface", "Stats Tab"),
    ("UserInterface", "Reference Tab"),

    # Detection sub-components
    ("DetectionSystem", "Classical CV"),
    ("DetectionSystem", "ML Detection"),
    ("Classical CV", "Background Subtraction"),
    ("Classical CV", "Contour Analysis"),
    ("ML Detection", "YOLO Detector"),
    ("ML Detection", "Faster R-CNN"),

    # Vehicle tracking sub-components
    ("VehicleTracking", "Detection"),
    ("VehicleTracking", "DeepSORT"),
    ("VehicleTracking", "Vehicle Counter"),

    # Parking allocation sub-components
    ("ParkingAllocation", "XGBoost Model"),
    ("ParkingAllocation", "Load Balancing"),
    ("ParkingAllocation", "Space Optimization"),

    # Connections to data storage
    ("DetectionSystem", "DataStorage"),
    ("VehicleTracking", "DataStorage"),
    ("ParkingAllocation", "DataStorage"),
    ("Visualization", "DataStorage")
])

# Render the graph
output_file = "parh11_clean_organized_diagram"
dot.render(output_file, cleanup=True)
print(f"Diagram saved as '{output_file}.jpg'.")