import sys
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection, PathCollection
import pickle
import numpy as np
import graphviz
import re
import warnings

# ignore matplotlib warnings related to older versions
warnings.filterwarnings(
    "ignore",
    message=r".*This figure was saved with matplotlib version .*",
    category=UserWarning
)

# attribute global flags
title = False
axis = False
legend = False
text = False

def load_obj(file_path):
    with open(file_path, "rb") as f:
        obj = pickle.load(f)
    return obj

def check_plot_properties(ref_ax, student_ax, tolerance=0):      
    # Check if the student's axis exists
    if not student_ax:
        print("No axes found in the figure.", file=sys.stderr)
        return False
    
    # Check if title, x-label, y-label, and legend are set
    has_title = bool(student_ax.get_title())
    has_xlabel = bool(student_ax.get_xlabel())
    has_ylabel = bool(student_ax.get_ylabel())
    has_legend = bool(student_ax.get_legend())

    # Check that the figure contains a title
    if title and not has_title:
        print("Missing title.", file=sys.stderr)
        return False

    # Check axes labels
    if axis and not has_xlabel:
        # For bar plots, x-label might not always be explicitly set, check tick labels
        if not student_ax.get_xticklabels():
            print("Missing x-label and no x-ticks present.", file=sys.stderr)
            return False
    if axis and not has_ylabel:
        print("Missing y-label.", file=sys.stderr)
        return False

    # Check that the legend is present
    if legend and not has_legend:
        print("Missing legend.", file=sys.stderr)
        return False

    # check text if flag is set
    if text:
        if not student_ax.texts:
            print("Text object not present in graph", file=sys.stderr)
            return False
    
        ref_text_obj = sorted(ref_ax.texts, key=lambda x: x.get_text())
        student_text_obj = sorted(student_ax.texts, key=lambda x: x.get_text())  
    
        if len(ref_text_obj) != len(student_text_obj):
            print(f"Mismatch in number of texts found\nEXPECTED: {len(ref_text_obj)}\nACTUAL: {len(student_text_obj)}", file=sys.stderr)
            return False
    
        for ref_text_obj, student_tex_obj in zip(ref_text_obj, student_text_obj):
            if ref_text_obj.get_text() != student_tex_obj.get_text():
                print(f"Incorrect text found\nEXPECTED: {ref_text_obj.get_text()}\nACTUAL: {student_tex_obj.get_text()}")
                return False
    
            if not np.allclose(ref_text_obj.get_position(), student_tex_obj.get_position(), atol=tolerance):
                print(f"Position of {ref_text_obj.get_text()} is incorrect\nEXPECTED: {ref_text_obj.get_position()}\nACTUAL: {student_tex_obj.get_position()}", file=sys.stderr)
                return False

    return True
    
def extract_scatter_data(ax):
    all_x_data = []
    all_y_data = []

    for scatter in ax.collections:
        paths = scatter.get_offsets()
        x_data, y_data = zip(*paths)

        all_x_data.extend(x_data)
        all_y_data.extend(y_data)

    return all_x_data, all_y_data

def extract_line_data(ax):
    all_x_data = []
    all_y_data = []

    for line in ax.get_lines():
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        
        all_x_data.extend(x_data)
        all_y_data.extend(y_data)

    return all_x_data, all_y_data

def extract_bar_data(ax):
    bars = ax.patches
    x_data = [bar.get_x() + bar.get_width() / 2 for bar in bars]
    y_data = [bar.get_height() for bar in bars]
    return x_data, y_data

def compare_data(x_ref, y_ref, x_student, y_student, tolerance=0):
    if len(x_student) != len(x_ref) or len(y_student) != len(y_ref):
        print("Arrays have different lengths.", file=sys.stderr)
        return False
    
    x_match = np.allclose(x_ref, x_student, atol=tolerance)
    y_match = np.allclose(y_ref, y_student, atol=tolerance)
    
    if not x_match:
        print("Differences in x values:", file=sys.stderr)
        for i, (x_s, x_r) in enumerate(zip(x_ref, x_student)):
            diff = abs(x_s - x_r)
            if diff > tolerance:
                print(f"Index {i}: EXPECTED x = {x_s:0.5f}, ACTUAL x = {x_r:0.5f}, DIFFERENCE = {diff:0.5f}", file=sys.stderr)
    
    if not y_match:
        print("Differences in y values:", file=sys.stderr)
        for i, (y_s, y_r) in enumerate(zip(y_ref, y_student)):
            diff = abs(y_s - y_r)
            if diff > tolerance:
                print(f"Index {i}: EXPECTED y = {y_s:0.5f}, ACTUAL y = {y_r:0.5f}, DIFFERENCE = {diff:0.5f}", file=sys.stderr)
    
    return x_match and y_match

def extract_geo_data(ax):
    geo_data = {
        "regions": [],
        "points": [],
        "metadata": []
    }

    for collection in ax.collections:
        if isinstance(collection, PatchCollection): 
            # Extract geometry regions
            paths = collection.get_paths()
            geo_data["regions"] = [path.vertices for path in paths]
            continue
        if isinstance(collection, PathCollection):
            # Extract point coordinates (if any)
            offsets = collection.get_offsets()
            if offsets is not None:
                geo_data["points"] = [tuple(coord) for coord in offsets]

            # Extract metadata
            metadata = collection.get_array()
            geo_data["metadata"] = list(metadata) if metadata is not None else []
            continue 

    return geo_data


def compare_geo_data(ref_geo, student_geo, tolerance=0):
    keys = ["regions", "points", "metadata"]

    for key in keys:
        ref_value = ref_geo[key]
        student_value = student_geo[key]

        if key in ["regions", "points"]:
            # Compare geometric data
            if len(ref_value) != len(student_value):
                print(f"Mismatch in number of {key}.", file=sys.stderr)
                return False

            for i, (ref_item, student_item) in enumerate(zip(ref_value, student_value)):
                if not np.allclose(ref_item, student_item, atol=tolerance):
                    print(f"Mismatch in {key} at index {i}: EXPECTED = {ref_item}, ACTUAL = {student_item}", file=sys.stderr)
                    return False

        elif key == "metadata":
            # Compare metadata 
            if not np.allclose(ref_value, student_value, atol=tolerance):
                print(f"Mismatch in metadata: EXPECTED = {ref_value}, ACTUAL = {student_value}", file=sys.stderr)
                return False
                
    return True    

def check_crs(ref_fig, student_fig): ## NOT WORKING
    ref_crs = getattr(ref_fig, "crs", None)
    student_crs = getattr(student_fig, "crs", None)
    return ref_crs == student_crs

def extract_digraph_data(source):
    digraph_dict = {}
    pattern = r'(?:"([^"]+)"|(\w+)) -> (\w+)'
    
    for match in re.finditer(pattern, source):
        key = match.group(1) or match.group(2) 
        value = match.group(3) 
        if key not in digraph_dict:
            digraph_dict[key] = set()
        digraph_dict[key].add(value)
    
    # convert sets to lists
    return {key: list(values) for key, values in digraph_dict.items()}

def compare_digraph_data(ref_digraph, student_digraph):
    # make sure that both dictionaries have the same keys
    if set(ref_digraph.keys()) != set(student_digraph.keys()):
        print(f"Mismatch in keys\nEXPECTED: {ref_digraph.keys()}\nACTUAL: {student_digraph.keys()}", file=sys.stderr)
        return False

    rv = True

    # check the values that each key points to in the digraph
    for key in ref_digraph.keys():
        if set(ref_digraph[key]) != set(student_digraph[key]): # sets to ingore order
            print(f"Contents of {key} do not match the expected values\nEXPECTED: {ref_digraph[key]}\nACTUAL: {student_digraph[key]}", file=sys.stderr)
            rv = False
            continue
    
    return rv

def check_slope_and_order(ref_ax, student_ax):
    ref_dict = {}
    ref_handles, ref_labels = ref_ax.get_legend_handles_labels()

    for handle, label in zip(ref_handles, ref_labels):
        y_data = list(handle.get_ydata())
        ref_dict[label] = (y_data, (y_data[-1] - y_data[0]) / (len(y_data) - 1))

    student_dict = {}
    student_handles, student_labels = student_ax.get_legend_handles_labels()

    if not student_labels:
        print("Missing labels. Make sure to add labels to every line in the graph", file=sys.stderr)
        return False

    for handle, label in zip(student_handles, student_labels):
        y_data = list(handle.get_ydata())
        student_dict[label] = (y_data, (y_data[-1] - y_data[0]) / (len(y_data) - 1))

    # check that the keys match
    if set(ref_dict.keys()) != set(student_dict.keys()):
        print(f"Label names do not match the expected.\nEXPECTED: {list(ref_dict.keys())}\nACTUAL: {list(student_dict.keys())}", file=sys.stderr)
        return False

    rv = True

    # check slope of lines
    for label in list(ref_dict.keys()):
        if ref_dict[label][1] >= 0 and student_dict[label][1] < 0:
            print(f"Slope of '{label}' is incorrect.\nEXPECTED: POSITIVE\nACTUAL: NEGATIVE [{student_dict[label][1]:0.5f}]", file=sys.stderr)
            rv &= False
        elif ref_dict[label][1] < 0 and student_dict[label][1] >= 0:
            print(f"Slope of '{label}' is incorrect.\nEXPECTED: NEGATIVE\nACTUAL: POSITIVE [{student_dict[label][1]:0.5f}]", file=sys.stderr)
            rv &= False

    # check order of lines
    ref_order = sorted(list(ref_dict.keys()), key=lambda x: ref_dict[x][0][-1], reverse=True)
    student_order = sorted(list(student_dict.keys()), key=lambda x: student_dict[x][0][-1], reverse=True)

    if ref_order != student_order:
        print(f"Final order of lines is incorrect.\nEXPECTED (descending order): {ref_order}\nACTUAL (descending order): {student_order}", file=sys.stderr)
        rv &= False    
    
    return rv

def grade_plot(ref_fig, student_fig, fig_type, tolerance=0):
    # check digraphs
    if fig_type == "digraph":
        ref_digraph = extract_digraph_data(graphviz.Source(ref_fig).source)
        student_digraph = extract_digraph_data(graphviz.Source(student_fig).source)
        return compare_digraph_data(ref_digraph, student_digraph)
            
    # check geopandas graphs
    if fig_type == "geo":
        if not check_crs(ref_fig, student_fig):
            print("CRS mismatch between reference and student plots", file=sys.stderr)
            return False
            
        ref_geo = extract_geo_data(ref_fig.gca())
        student_geo = extract_geo_data(student_fig.gca())
        return compare_geo_data(ref_geo, student_geo, tolerance=tolerance) 

    # continue to normal matplotlib plots
    ref_fig_ax = ref_fig.gca()
    student_fig_ax = student_fig.gca()

    if not check_plot_properties(ref_fig_ax, student_fig_ax, tolerance=tolerance):
        return False
            
    rv = True

    types = fig_type.split("-")

    for t in types:
        match t: 
            case "scatter":
                data_func = extract_scatter_data
            case "line":
                data_func = extract_line_data
            case "bar":
                data_func = extract_bar_data
            case "slope":
                rv &= check_slope_and_order(ref_fig_ax, student_fig_ax)
                continue
    
        ref_x, ref_y = data_func(ref_fig_ax)
        student_x, student_y = data_func(student_fig_ax)
        
        rv  &= compare_data(ref_x, ref_y, student_x, student_y, tolerance=tolerance)

    return rv

def main():
    # Check correctness of passed arguments 
    if len(sys.argv) < 5 or len(sys.argv) > 9 :
        print("Usage: python3 image_tester.py <ref_img_path> <student_img_path> <figure_types> <tolerance> [-t] [-ax] [-l] [-tx]", file=sys.stderr)
        return -1

    # get reference image path
    ref_img_path = sys.argv[1]
    
    # get student image path
    student_img_path = sys.argv[2]
    
    # get figure types
    fig_types = sys.argv[3]

    # get tolerance val
    tolerance = float(sys.argv[4])

    # get graph attribute flags
    global title
    global axis 
    global legend
    global text
    
    if len(sys.argv) > 5:
        for flag in sys.argv[5:]:
            match flag:
                case "-t":
                    title = True
                case "-ax":
                    axis = True
                case "-l":
                    legend = True
                case "-tx":
                    text = True
                case _:
                    continue

    ref_fig = load_obj(ref_img_path)
    student_fig = load_obj(student_img_path)
    
    return grade_plot(ref_fig, student_fig, fig_types, tolerance=tolerance)

if __name__ == "__main__":
    rv = main()
    sys.exit(rv)