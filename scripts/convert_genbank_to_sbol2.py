import os
import sys
import git

import scriptutils

# find the repository for automatic git actions, if possible
try:
    repo = git.Repo('.', search_parent_directories=True)
except git.InvalidGitRepositoryError:
    repo = None

error = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Converting GenBank to SBOL2 files for package {os.path.basename(p)}')
    try:
        # convert files
        scriptutils.convert_package_genbank_to_sbol2(p, scriptutils.SYNBICT_NAMESPACE)

    except (OSError, ValueError) as e:
        print(f'Could not convert GenBank files for package {os.path.basename(p)}: {e}')
        error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)
