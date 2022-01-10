import os
import sys
import git

import scriptutils

FLUORESCENT_REPORTER_OPTIONS = ['-m', '1', # Minimum target length
                                '-M', '10', # Minimum feature length
                                '-U', 'https://synbiohub.org', # SynBioHub URL
                                '-F', 'https://synbiohub.org/public/igem/cds_reporter/1', # Feature URL
                                '-ni', # Non-interactive
                                '-cm', # Complete matches allowed
                                '-a'] # Merge compatible annotations

OPEN_YEAST_OPTIONS = ['-m', '1',
                      '-M', '10',
                      '-U', 'https://synbiohub.org',
                      '-F', 'https://synbiohub.org/public/free_genes_feature_libraries/open_yeast/1',
                      '-ni',
                      '-a']

CURATION_SELECTOR = {'Fluorescent Reporter Proteins': FLUORESCENT_REPORTER_OPTIONS,
                     'Open Yeast Collection': OPEN_YEAST_OPTIONS}


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
            mappings = scriptutils.curate_package_sbol2_gbconv(p, curation_options)
            # if there's a git repo, try to remove the old files
            # if repo and len(mappings):
                # repo.index.add(mappings.keys())     # add, in case they weren't there before
                # repo.index.remove(mappings.keys(), working_tree=True, f=True)  # then remove

        except (OSError, ValueError) as e:
            print(f'Could not curate SBOL2 GenBank-conversion files for package {package_name}: {e}')
            error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)