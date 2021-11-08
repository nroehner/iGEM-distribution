import os
import sys
import git

import scriptutils

import sequences_to_features

from sbol_utilities.helper_functions import GBCONV_FILE_TYPES

REPORTER_OPTIONS = ['-m', '1'
                    '-M', '10',
                    '-U', 'https://synbiohub.org',
                    '-F', 'https://synbiohub.org/public/igem/cds_reporter/1',
                    '-ni',
                    '-cm',
                    '-a']

OPEN_YEAST_OPTIONS = ['-m', '1'
                      '-M', '10',
                      '-U', 'https://synbiohub.org',
                      '-F', 'https://synbiohub.org/public/igem_feature_libraries/igem_plasmid_vectors/1',
                      '-ni',
                      '-a']

CURATION_SELECTOR = {'Fluorescent Reporter Proteins': REPORTER_OPTIONS,
                     'Open Yeast Collection': OPEN_YEAST_OPTIONS}


def curate_package_sbol2_gbconv(package: str, curation_options) -> dict[str, str]:
	"""Find all SBOL2 GenBank-conversion files in a package directory and curate them using SYNBICT

    :param package: path of package to search
    :return: dictionary mapping paths of SBOL2 inputs to curated outputs
    """

    # import SBOL2 converted from GenBank
    target_files = []
    for file in itertools.chain(*(glob.glob(os.path.join(package, f'*{ext}')) for ext in GBCONV_FILE_TYPES)):
        target_files.append(file)

    # make curated SBOL2 versions of the SBOL2 GenBank-conversion file names
    output_files = [os.path.splitext(file)[0].splitext(file)[0]+'.synbict.xml' for file in target_files]

    mappings = {target_files[i] : output_files[i] for i in range(0, len(target_files))}

    curation_args = curation_options + ['-t'] + target_files
    curation_args = curation_args + ['-o'] + output_files

    sequences_to_features.main(curation_args)

    return mappings


# find the repository for automatic git actions, if possible
try:
    repo = git.Repo('.', search_parent_directories=True)
except git.InvalidGitRepositoryError:
    repo = None

error = False
packages = scriptutils.package_dirs()
for p in packages:
    package_name = os.path.basename(p)
    
    if package_name in CURATION_SELECTOR:
        curation_options = CURATION_SELECTOR[package_name]
    else:
        curation_options = []

    if len(curation_options) > 0:
        print(f'Curating SBOL2 GenBank-conversion files for package {package_name}')
        try:
            # convert files
            mappings = curate_package_sbol2_gbconv(p, curation_options)
            # if there's a git repo, try to remove the old files
            if repo and len(mappings):
                repo.index.add(mappings.keys())     # add, in case they weren't there before
                repo.index.remove(mappings.keys(), working_tree=True, f=True)  # then remove

        except (OSError, ValueError) as e:
            print(f'Could not curate SBOL2 GenBank-conversion files for package {package_name}: {e}')
            error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)