import logging
import glob
import os
import itertools

import sequences_to_features

from sbol_utilities.helper_functions import GENETIC_DESIGN_FILE_TYPES
from sbol_utilities.conversion import convert_from_genbank, convert3to2

SYNBICT_NAMESPACE = 'http://synbict.org'

CURATED_FILE_TYPE = '.synbict.xml'

GBCONV_FILE_TYPE = '.gbconv.xml'


def convert_package_genbank_to_sbol2(package: str, namespace: str) -> dict[str, str]:
    """Find all GenBank files in a package directory and convert them to SBOL2

    :param package: path of package to search
    :return: dictionary mapping paths of GenBank inputs to SBOL2 outputs
    """
    mappings = {}

    # import GenBank
    for file in itertools.chain(*(glob.glob(os.path.join(package, f'*{ext}')) for ext in GENETIC_DESIGN_FILE_TYPES['GenBank'])):
        print(f'Attempting to convert GenBank file {file} to SBOL2')
        file2 = os.path.splitext(file)[0]+'.gbconv.xml'  # make a GenBank to SBOL2 version of the file name
        doc2 = convert3to2(convert_from_genbank(file, namespace, True))
        # check if it's valid before writing
        report = doc2.validate()
        if report == 'Invalid.':
            logging.warning('GenBank conversion failed: SBOL2 file has errors')
            continue

        print(f'Writing SBOL2 GenBank-conversion file to {file2}')
        doc2.write(file2)
        # record the conversion for later use
        mappings[file] = file2

    return mappings


def curate_package_sbol2_gbconv(package: str, curation_options) -> dict[str, str]:
    """Find all SBOL2 GenBank-conversion files in a package directory and curate them using SYNBICT

    :param package: path of package to search
    :return: dictionary mapping paths of SBOL2 inputs to curated outputs
    """

    # import SBOL2 converted from GenBank
    target_files = []
    for file in itertools.chain(*(glob.glob(os.path.join(package, f'*{ext}')) for ext in {GBCONV_FILE_TYPE})):
        target_files.append(file)

    # make curated SBOL2 versions of the SBOL2 GenBank-conversion file names
    gbconv_name = os.path.splitext(file)[0]
    output_files = [os.path.splitext(gbconv_name)[0]+CURATED_FILE_TYPE for file in target_files]

    mappings = {target_files[i] : output_files[i] for i in range(0, len(target_files))}

    curation_args = curation_options + ['-t'] + target_files
    curation_args = curation_args + ['-o'] + output_files

    sequences_to_features.main(curation_args)

    return mappings