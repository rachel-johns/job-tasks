"""

SNOMED (Systematized Nomenclature of Medicine - Clinical Terms) and LOINC (Logical Observation Identifiers, Names, and Codes)
are examples of clinical terminology codes used in healthcare to standardize the representation of medical concepts and
observations, allowing for accurate data exchange between different systems and healthcare providers.

At work, I use SNOMED and LOINC almost everyday. I regularly reference only the codes housed in our Maven® Disease Surveillance System
Before I began, I exported the SNOMED and LOINC references codes from Maven but they are formatted in XML, rendering them difficult to read and use
for adhoc and large scale projects.

Instead of scrolling for hours or using the CTRL + F function to find conditions or lab tests,
I wrote this basic code to:
1. parse only the fields of interest from the .xml file
2. format the contents into columns
3. save and export/download the output as a .csv file

From there I use the output for data validation and ETL processes across systems.
This is the code for SNOMED codes extraction.
I used the same codes for LOINC codes extraction by just changing the file path and renaming the desired export file

"""

import os
import xml.etree.ElementTree as ET
import pandas as pd

def main():
    # Pre-set the XML file path
    xml_file = r"C:\Users\johns\Downloads\South Dakota Department of Health\Reference Codes\SNOMED Codes.xml"

    # Check if the file exists
    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' does not exist.")
        return

    # Parse the XML file
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error: Failed to parse the XML file. Details: {e}")
        return

    # Initialize lists to store the extracted data
    reference_groups = []
    reference_codes = []
    descriptions = []

    # Iterate through each ReferenceCodeDefinition element
    for element in root.findall('.//ReferenceCodeDefinition'):
        reference_group = element.get('ReferenceGroup', 'N/A')
        reference_code = element.get('ReferenceCode', 'N/A')
        description = element.get('Description', 'N/A')

        # Append the extracted data to the lists
        reference_groups.append(reference_group)
        reference_codes.append(reference_code)
        descriptions.append(description)

    # Create a DataFrame from the extracted data
    data = {
        'ReferenceGroup': reference_groups,
        'ReferenceCode': reference_codes,
        'Description': descriptions
    }

    df = pd.DataFrame(data)

    # Display the first few rows of the DataFrame
    print("Extracted data preview:")
    print(df.head())

    # Define the output CSV file name with full path
    output_csv = r"C:\Users\johns\Downloads\South Dakota Department of Health\Reference Codes\Extracted_SNOMED_Codes.csv"

    # Save the DataFrame to a CSV file
    try:
        df.to_csv(output_csv, index=False)
        print(f"Data successfully saved to {output_csv}")
    except Exception as e:
        print(f"Failed to save CSV file. Error: {e}")

if __name__ == "__main__":
    main()
