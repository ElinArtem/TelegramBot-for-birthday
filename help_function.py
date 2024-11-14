import json

def save_to_json(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data saved to {filename} successfully.")
    except Exception as e:
        print(f"Error saving data to {filename}: {str(e)}")
    


def conect_json(file_name):
    with open(file_name) as f:
        return json.loads(f.read())