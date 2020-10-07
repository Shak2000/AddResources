# Program to check if new data is available at IRS location
# https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf

# 1. Grabs when files were updated last.
# 2. Checks if the date is changed from last updated date.
# 3. Downloads the files and calculate checksum.
# 4. Match the checksum of last used files, if different new files are available hence kick off the pipeline.


