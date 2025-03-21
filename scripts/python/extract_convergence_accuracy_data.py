#!/usr/bin/env python3

import scripts.python.static_degradation_viz_module as sdvm
import os
import pandas as pd
import argparse
import warnings
import timeit
import sys
from joblib import Parallel, delayed

"""Saving numpy arrays in HDF files will give a performance warning, so ignoring it"""
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

def load_data(args):
    """Load the JSON data from a given folder.

    Args:
        data_folder: Path to the folder containing all the JSON data files. The files can be several levels deep.
    """
    json_data_lst = []

    # Parallel implementation of generating StaticDegradationJsonData objects
    def parallel_generate_json_data_lst(root, files):

        if not files: return None # no files detected
        else:
            json_files = [filename for filename in files if filename.endswith(".json")]
            if any(json_files):
                if args.verbose:
                    print("Creating a StaticDegradationJsonData object for {0} JSON files in folder={1}...".format(len(json_files), root))
                    sys.stdout.flush()

                return sdvm.StaticDegradationJsonData(root)

    # Extract JSON data objects in parallel
    json_data_lst = Parallel(n_jobs=-1, verbose=0)(
        delayed(parallel_generate_json_data_lst)(root, files) for root, _, files in os.walk(args.FOLDER)
    )

    # Clean up the `None`s in the list
    return [obj for obj in json_data_lst if obj is not None]

def save_to_h5(json_data_lst, args):
    df = pd.DataFrame()

    start = None

    for i, d in enumerate(json_data_lst):
        if args.verbose:
            start = timeit.default_timer()
            print("Processing data for convergence and accuracy values {0}/{1}...".format(i+1, len(json_data_lst)), end=" ")
            sys.stdout.flush()

        df = sdvm.process_convergence_accuracy(d, df, args.THRESH)

        if args.verbose:
            print("Done!")
            end = timeit.default_timer()
            print("\t-- Elapsed time:", end-start, "s --\n")

    df.to_hdf(args.output, key="df" if not args.key else args.key)

    print("Stored data as {0} with key \"{1}\"".format(os.path.join(os.getcwd(), args.output), "df" if not args.key else args.key))

def main(args):

    json_data_lst = load_data(args)
    if json_data_lst: save_to_h5(json_data_lst, args)
    else: print("No JSON files found.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process convergence and accuracy data from simulated experiment data to save into HDF file. The stored data is a Pandas DataFrame.")
    parser.add_argument("FOLDER", type=str, help="path to the folder containing all the JSON data files; the files can be several levels deep")
    parser.add_argument("THRESH", type=float, help="threshold to assess convergence point")
    parser.add_argument("--output", default="conv_acc_data.h5", type=str, help="output filename (default: conv_acc_data.h5)")
    parser.add_argument("--key", default="df", help="dictionary key when storing the Pandas DataFrame (default: \"df\")")
    parser.add_argument("--verbose", action="store_true", help="flag to run with verbose output")

    args = parser.parse_args()

    main(args)
