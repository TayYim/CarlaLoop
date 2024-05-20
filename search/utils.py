import xml.etree.ElementTree as ET
import os
import pickle
import csv
import psutil


def change_route_value(file_path, route_id, param_name, value):
    # Load the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Traverse all 'route' elements
    for route in root.findall(".//route"):
        # Check if the 'id' attribute of the element is equal to the given route_id
        if route.get("id") == str(route_id):
            # Traverse all 'scenarios' elements under the 'route' element with the given route_id
            for scenarios in route.findall("scenarios"):
                # Traverse all 'scenario' elements under the 'scenarios' element
                for scenario in scenarios.findall("scenario"):
                    # Traverse all elements with the given param_name under the 'scenario' element
                    for param in scenario.findall(param_name):
                        # Check if the element has a 'value' attribute
                        if param.get("value"):
                            # If it does, modify the value of the 'value' attribute to the given value
                            param.set("value", str(value))

    # Save the modified XML data back to the file
    tree.write(file_path)


def save_pickle(path, filename, data):
    """
    save dict data to pickle
    """
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file:
        pickle.dump(data, file)


def save_csv(path, filename, data):
    """
    save dict data to csv
    """
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        header = data.keys()
        writer = csv.writer(file)
        writer.writerow(header)
        length = len(data[list(header)[0]])
        for i in range(length):
            row = []
            for item in header:
                if len(data[item]) <= i:
                    row.append("")
                try:
                    row.append(data[item][i])
                except:
                    pass
            writer.writerow(row)


def is_process_running(process_name):
    # Enumerate all running processes
    for proc in psutil.process_iter(attrs=["name"]):
        try:
            # Find the process name that matches the specified name
            if process_name.lower() in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
