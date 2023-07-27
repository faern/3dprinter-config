#!/usr/bin/env python3
#
# Splits a SuperSlicer "Config Bundle" file into separate ini files, one per profile.
# This allows versioning various printer and all filament configs separately.
# Gives way nicer diffs and better overview.
#
# See the repo's main README for usage instructions.

import argparse
import re

# Should match any ini section
INI_SECTION_REGEX = r"^\[(?P<section_name>.*)\]$"

# Matches the ini section names from SuperSlicer that we care about and want to split into files.
# We care about the "print", "filament" and "printer" profiles.
SECTION_NAME_REGEX = r"(?P<profile_type>print|filament|printer):(?P<profile_name>.*)"


def create_arg_parser():
    arg_parser = argparse.ArgumentParser(
        description="Splits a SuperSlicer Config Bundle into different files for printer and filament configs"
    )
    arg_parser.add_argument("config_bundle")
    arg_parser.add_argument("--output-dir", "-o", default=".")
    return arg_parser


if __name__ == "__main__":
    args = create_arg_parser().parse_args()
    config_bundle = args.config_bundle
    output_dir = args.output_dir

    section_pattern = re.compile(INI_SECTION_REGEX)
    superslicer_section_name_pattern = re.compile(SECTION_NAME_REGEX)

    # The output INI file we currently write to. None when not writing to any file
    current_output_file = None

    with open(config_bundle, "r") as config_bundle:
        for line in config_bundle:
            section_match = section_pattern.match(line.strip())
            # We hit a new INI section. Parse it and update current_output_file accordingly
            if section_match is not None:
                # Close any already open file. Since we hit a new section, we are done with the current one
                if current_output_file is not None:
                    current_output_file.close()
                    current_output_file = None

                section_name = section_match.group("section_name")
                section_name_match = superslicer_section_name_pattern.match(section_name)
                # This is an INI section we care about and want in a separate file
                if section_name_match is not None:
                    profile_type = section_name_match.group("profile_type")
                    profile_name = section_name_match.group("profile_name")
                    print(f"Parsing {profile_type} section \"{profile_name}\"")

                    # Open the new output ini file
                    current_output_file = open(f"{output_dir}/{profile_type} - {profile_name}.ini", "w")
                else:
                    print(f"Ignoring INI section {line.strip()}")

            # Write the current line to the current output file
            if current_output_file is not None:
                current_output_file.write(line)

    # Clean up and close the last file if one is open
    if current_output_file is not None:
        current_output_file.close()
        current_output_file = None
