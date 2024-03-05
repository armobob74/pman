import csv

def read_csv(filepath, delimiter='\t'):
    with open(filepath, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        data = list(reader)
    data = [[cell.strip() for cell in row] for row in data]
    return data

def write_csv(data, filepath, delimiter='\t'):
    """
    Write the given data to a CSV file.

    Args:
        data (list of lists): The data to be written to the CSV file.
        filepath (str): The file path where the CSV file will be created.
        delimiter (str, optional): The delimiter to be used in the CSV file. Defaults to '\t'.
    """
    try:
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=delimiter)
            writer.writerows(data)
        return True
    except Exception as e:
        return f"ERROR -- Failed to write CSV: {e}"

