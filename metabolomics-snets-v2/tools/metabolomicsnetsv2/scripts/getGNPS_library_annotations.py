#!/usr/bin/python

import sys
import os
import ming_fileio_library
import pandas as pd
import ming_gnps_library
import requests
from collections import defaultdict

def main():
    input_result_filename = sys.argv[1]
    output_result_filename = sys.argv[2]

    spectrum_id_cache = {}


    input_rows, input_table = ming_fileio_library.parse_table_with_headers(input_result_filename)

    output_table = defaultdict(list)

    output_headers = ["SpectrumID", "Compound_Name", "Ion_Source", "Instrument", "Compound_Source", "PI", "Data_Collector", "Adduct"]
    output_headers += ["Precursor_MZ", "ExactMass", "Charge", "CAS_Number", "Pubmed_ID", "Smiles", "INCHI", "INCHI_AUX", "Library_Class"]
    output_headers += ["IonMode", "UpdateWorkflowName", "LibraryQualityString", "#Scan#", "SpectrumFile", "MQScore", "Organism"]
    output_headers += ["TIC_Query", "RT_Query", "MZErrorPPM", "SharedPeaks", "MassDiff", "LibMZ", "SpecMZ", "SpecCharge"]
    output_headers += ["MoleculeExplorerDatasets", "MoleculeExplorerFiles"]

    for header in output_headers:
        output_table[header] = []

    number_hits_per_query = defaultdict(lambda: 0)

    for i in range(input_rows):
        number_hits_per_query[input_table["FileScanUniqueID"][i]] += 1

    molecule_explorer_df = pd.DataFrame(ming_gnps_library.get_molecule_explorer_dataset_data())

    for i in range(input_rows):
        spectrum_id = input_table["LibrarySpectrumID"][i]
        score = input_table["MQScore"][i]
        filename = input_table["SpectrumFile"][i]
        libfilename = input_table["LibraryName"][i]
        scan = input_table["#Scan#"][i]
        TIC_Query = input_table["UnstrictEvelopeScore"][i]
        RT_Query = input_table["p-value"][i]
        SpecCharge = input_table["Charge"][i]
        SpecMZ = input_table["SpecMZ"][i]
        MZErrorPPM = input_table["mzErrorPPM"][i]
        SharedPeaks = input_table["LibSearchSharedPeaks"][i]
        MassDiff = input_table["ParentMassDiff"][i]

        print(spectrum_id)
        gnps_library_spectrum = None
        try:
            gnps_library_spectrum = None
            if spectrum_id in spectrum_id_cache:
                gnps_library_spectrum = spectrum_id_cache[spectrum_id]
            else:
                gnps_library_spectrum = ming_gnps_library.get_library_spectrum(spectrum_id)
                spectrum_id_cache[spectrum_id] = gnps_library_spectrum

            #Making sure not an error
            gnps_library_spectrum["annotations"][0]["Compound_Name"]
        except KeyboardInterrupt:
            raise
        except:
            continue

        gnps_library_spectrum["annotations"] = sorted(gnps_library_spectrum["annotations"], key=lambda annotation: annotation["create_time"], reverse=True)

        output_table["SpectrumID"].append(spectrum_id)
        output_table["Compound_Name"].append(gnps_library_spectrum["annotations"][0]["Compound_Name"].replace("\t", ""))
        output_table["Ion_Source"].append(gnps_library_spectrum["annotations"][0]["Ion_Source"].replace("\t", ""))
        output_table["Instrument"].append(gnps_library_spectrum["annotations"][0]["Instrument"].replace("\t", ""))
        output_table["Compound_Source"].append(gnps_library_spectrum["annotations"][0]["Compound_Source"].replace("\t", ""))
        output_table["PI"].append(gnps_library_spectrum["annotations"][0]["PI"].replace("\t", ""))
        output_table["Data_Collector"].append(gnps_library_spectrum["annotations"][0]["Data_Collector"].replace("\t", ""))
        output_table["Adduct"].append(gnps_library_spectrum["annotations"][0]["Adduct"].replace("\t", ""))
        output_table["Precursor_MZ"].append(gnps_library_spectrum["annotations"][0]["Precursor_MZ"].replace("\t", ""))
        output_table["ExactMass"].append(gnps_library_spectrum["annotations"][0]["ExactMass"].replace("\t", ""))
        output_table["Charge"].append(gnps_library_spectrum["annotations"][0]["Charge"].replace("\t", ""))
        output_table["CAS_Number"].append(gnps_library_spectrum["annotations"][0]["CAS_Number"].replace("\t", ""))
        output_table["Pubmed_ID"].append(gnps_library_spectrum["annotations"][0]["Pubmed_ID"].replace("\t", ""))
        output_table["Smiles"].append(gnps_library_spectrum["annotations"][0]["Smiles"].replace("\t", ""))
        output_table["INCHI"].append(gnps_library_spectrum["annotations"][0]["INCHI"].replace("\t", ""))
        output_table["INCHI_AUX"].append(gnps_library_spectrum["annotations"][0]["INCHI_AUX"].replace("\t", ""))
        output_table["Library_Class"].append(gnps_library_spectrum["annotations"][0]["Library_Class"].replace("\t", ""))
        output_table["IonMode"].append(gnps_library_spectrum["annotations"][0]["Ion_Mode"].replace("\t", ""))

        if gnps_library_spectrum["annotations"][0]["Library_Class"] == "1":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-GOLD")
            output_table["LibraryQualityString"].append("Gold")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "2":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-SILVER")
            output_table["LibraryQualityString"].append("Silver")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "3":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Bronze")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "4":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "5":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "10":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Challenge")
        else:
            print("BULLLSHIT", gnps_library_spectrum["annotations"][0]["Library_Class"])

        output_table["#Scan#"].append(scan)
        output_table["SpectrumFile"].append(filename)
        output_table["LibraryName"].append(libfilename)
        output_table["MQScore"].append(score)
        output_table["Organism"].append(gnps_library_spectrum["spectruminfo"]["library_membership"])
        output_table["TIC_Query"].append(TIC_Query)
        output_table["RT_Query"].append(RT_Query)
        output_table["MZErrorPPM"].append(MZErrorPPM)
        output_table["SharedPeaks"].append(SharedPeaks)
        output_table["MassDiff"].append(MassDiff)
        output_table["LibMZ"].append(gnps_library_spectrum["annotations"][0]["Precursor_MZ"])
        output_table["SpecMZ"].append(SpecMZ)
        output_table["SpecCharge"].append(SpecCharge)
        output_table["FileScanUniqueID"].append(input_table["FileScanUniqueID"][i])
        output_table["NumberHits"].append(number_hits_per_query[input_table["FileScanUniqueID"][i]])


        tag_list = [ (tag["tag_desc"] + "[" + tag["tag_type"] + "]") for tag in gnps_library_spectrum["spectrum_tags"]]
        tag_string = "||".join(tag_list).replace("\t", "")

        output_table["tags"].append(tag_string)

        #Getting molecule explorer information
        compound_name = gnps_library_spectrum["annotations"][0]["Compound_Name"].replace("\t", "")
        compound_filtered_df = molecule_explorer_df[molecule_explorer_df["compound_name"] == compound_name]
        if len(compound_filtered_df) == 1:
            output_table["MoleculeExplorerDatasets"].append(compound_filtered_df.to_dict(orient="records")[0]["number_datasets"])
            output_table["MoleculeExplorerFiles"].append(compound_filtered_df.to_dict(orient="records")[0]["number_files"])
        else:
            output_table["MoleculeExplorerDatasets"].append(0)
            output_table["MoleculeExplorerFiles"].append(0)


    ming_fileio_library.write_dictionary_table_data(output_table, output_result_filename)




if __name__ == "__main__":
    main()
