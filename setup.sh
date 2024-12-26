#!/bin/bash

echo "Running create_tables.py..."
python3 securities_project/securities_project/src/create_tables.py
if [ $? -ne 0 ]; then
    echo "Error while running create_tables.py. Exiting."
    exit 1
fi
#################################################################################
echo "Running extract_data_all_time.py..."
python3 securities_project/securities_project/src/extract_data_all_time.py


if [ $? -ne 0 ]; then
    echo "Error while running extract_data_all_time.py. Exiting."
    exit 1
fi
#################################################################################
echo "Running bulk_upload.py..."
python3 securities_project/securities_project/src/bulk_upload.py


if [ $? -ne 0 ]; then
    echo "Error while running bulk_upload.py. Exiting."
    exit 1
fi

echo "All scripts ran successfully!"

