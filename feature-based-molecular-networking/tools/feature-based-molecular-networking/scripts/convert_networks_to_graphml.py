#!/usr/bin/python


import sys
import getopt
import os
import molecular_network_filtering_library
import glob
import networkx as nx
import argparse

def main():
    parser = argparse.ArgumentParser(description='Creating GraphML')
    parser.add_argument('input_pairs', help='input_pairs')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('input_librarysearch', help='input_librarysearch')
    parser.add_argument('output_graphml', help='output_graphml')
    parser.add_argument('--input_analoglibrarysearch', help='input_analoglibrarysearch')
    parser.add_argument('--input_pairsfolder', help='input_pairsfolder')
    args = parser.parse_args()

    #Doing other filtering
    G = molecular_network_filtering_library.loading_network(args.input_pairs, hasHeaders=True)
    molecular_network_filtering_library.add_clusterinfo_summary_to_graph(G, args.input_clusterinfosummary)
    molecular_network_filtering_library.add_library_search_results_to_graph(G, args.input_librarysearch)


    if args.input_pairsfolder is not None:
        all_pairs_files = glob.glob(os.path.join(args.input_pairsfolder, "*"))
        for additional_pairs_file in all_pairs_files:
            print("Adding Additional Edges", additional_pairs_file)
            molecular_network_filtering_library.add_additional_edges(G, additional_pairs_file)

    if args.input_analoglibrarysearch is not None:
        molecular_network_filtering_library.add_library_search_results_to_graph(G, args.input_librarysearch, annotation_prefix="Analog:")

    nx.write_graphml(G, args.output_graphml, infer_numeric_types=True)



if __name__ == "__main__":
    main()
