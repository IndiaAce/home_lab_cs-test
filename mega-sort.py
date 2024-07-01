import os
import re
import collections

def get_user_input(prompt):
    return input(prompt).strip()

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def save_yaml(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def count_properties(directory, file_name, property_name, ignore_dirs):
    property_counter = collections.Counter()
    file_locations = collections.defaultdict(list)
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                content = load_yaml(file_path)
                matches = re.findall(fr'{property_name}: ([^\n]+)', content)
                for match in matches:
                    property_counter.update([match])
                    file_locations[match].append(file_path)
    return property_counter, file_locations

def display_stats(property_counter, property_name):
    total = sum(property_counter.values())
    print(f"Total '{property_name}' values found: {total}")
    for value, count in property_counter.items():
        print(f"{value}: {count} ({(count/total)*100:.2f}%)")

def display_file_locations(file_locations, property_value):
    if property_value in file_locations:
        print(f"Files with '{property_value}':")
        for file in file_locations[property_value]:
            print(f"- {file}")
    else:
        print(f"No files found with '{property_value}'.")

def modify_property(directory, file_name, property_name, new_value, ignore_dirs):
    property_pattern = re.compile(fr'({property_name}: )([^\n]+)')
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file == file_name:
                file_path = os.path.join(root, file)
                content = load_yaml(file_path)
                modified_content = property_pattern.sub(fr'\1{new_value}', content)
                save_yaml(file_path, modified_content)

if __name__ == "__main__":
    root_directory = "C:\\Users\\lukew\\OneDrive\\Documents\\dev_link\\splunk_dev\\wrench_deletion"  # Hardcoded root directory
    folder_blocklist = ["global"]  # Folders to always ignore
    
    while True:
        file_base_name = get_user_input("What file name would you like to modify? (e.g., macros): ")
        file_name = file_base_name + ".yml"
        property_name = get_user_input("What property would you like to modify? (e.g., owner): ")
        
        # Get directories to ignore from user input
        ignore_dirs_input = get_user_input("Enter client directories to ignore (comma-separated, e.g., 'client1,client2'): ")
        ignore_dirs = ignore_dirs_input.split(",") if ignore_dirs_input else []
        
        # Combine blocklist and user-specified ignore directories
        ignore_dirs = set(ignore_dirs + folder_blocklist)
        
        # Display statistics
        property_counter, file_locations = count_properties(root_directory, file_name, property_name, ignore_dirs)
        display_stats(property_counter, property_name)
        
        # Ask if user wants to mass-modify or investigate
        action = get_user_input("Do you want to mass-modify, investigate, or exit? (yes/i/no): ").lower()
        
        if action == 'yes':
            new_value = get_user_input(f"What should the new '{property_name}' value be set to?: ")
            modify_property(root_directory, file_name, property_name, new_value, ignore_dirs)
            # Re-display statistics after modification
            property_counter, file_locations = count_properties(root_directory, file_name, property_name, ignore_dirs)
            display_stats(property_counter, property_name)
        elif action == 'i':
            investigate_value = get_user_input(f"Please specify the {property_name} you want to investigate: ")
            display_file_locations(file_locations, investigate_value)
        elif action == 'no':
            break
