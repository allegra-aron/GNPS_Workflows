#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the Progensis output into a diserable format
"""
import pandas as pd
import sys


#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename, sep=",", skiprows=2)

    non_sample_names = ["Compound", "Neutral mass (Da)", "m/z", "Charge", "Retention time (min)", \
        "Chromatographic peak width (min)", "Identifications", "Isotope Distribution", "Maximum Abundance", \
        "Minimum CV%", "Accepted Compound ID", "Accepted Description", "Adducts", "Formula", \
        "Score", "Fragmentation Score", "Mass Error (ppm)", "Isotope Similarity", "Retention Time Error (mins)", "Compound Link", "Max Fold Change Peak area", \
        "Max Fold Change", "Highest Mean", "Lowest Mean"]

    input_records = input_format.to_dict(orient="records")
    sample_names = [header for header in input_format.keys() if not header in non_sample_names and not header[-2:] == ".1"]

    output_records = []
    compound_to_scan_mapping = {}
    running_scan = 0
    for record in input_records:
        running_scan += 1

        compound_name = record["Compound"]
        mz = record["m/z"]
        rt = record["Retention time (min)"]

        output_record = {}
        output_record["row ID"] = str(running_scan)
        output_record["row retention time"] = str(rt)
        output_record["row m/z"] = str(mz)

        for sample_name in sample_names:
            output_record[sample_name + " Peak area"] = record[sample_name]

        output_records.append(output_record)
        compound_to_scan_mapping[compound_name] = running_scan

    output_df = pd.DataFrame(output_records)
    output_df.to_csv(output_filename, sep=",", index=False)

    return compound_to_scan_mapping

#Converts MSP to MGF
def convert_mgf(input_msp, output_mgf, compound_to_scan_mapping):
    output_filename = open(output_mgf, "w")
    read_name = False
    for line in open(input_msp):
        if line.startswith("Name:"):
            compound_name = line.rstrip().replace("Name: ", "").split("(")[1][:-1]
            read_name = True
            output_filename.write("BEGIN IONS\n")
            output_filename.write("SCANS=%s\n" % (compound_to_scan_mapping[compound_name]))
            output_filename.write("MSLEVEL=2\n")
        elif line.startswith("PrecursorMZ:"):
            output_filename.write("PEPMASS=%s\n" % (line.rstrip().replace("PrecursorMZ: ", "")))
        elif line.startswith("Charge:"):
            output_filename.write("CHARGE=%s\n" % (line.rstrip().replace("Charge: ", "")))
        elif len(line.rstrip()) == 0 and read_name == True:
            read_name = False
            output_filename.write("END IONS\n\n")
        else:
            try:
                mass = float(line.split(" ")[0])
                intensity = float(line.split(" ")[1])
                output_filename.write("%f %f\n" % (mass, intensity))
            except:
                continue

    return

if __name__=="__main__":
    convert_to_feature_csv(sys.argv[1], sys.argv[2])
