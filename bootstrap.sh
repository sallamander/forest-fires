#!/usr/bin/env bash

set -e
set -x

# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
bash Miniconda-latest-Linux-x86_64.sh -b
echo '' >> ~/.bashrc
echo 'export PATH="/home/ubuntu/miniconda/bin:$PATH"' >> ~/.bashrc
. ~/.bashrc

# Install git, clone repo, create conda environment
sudo apt-get update
sudo apt-get install git unzip -y
git clone https://github.com/sallamander/forest-fires.git
cd ~/forest-fires
conda env create
source activate forest-fires

# Unzip data
cd ~/forest-fires/data/
python unzip.py

# Install PostgreSQL and PostGIS extension and create DB
sudo apt-get install postgresql postgresql-contrib postgis postgresql-9.3-postgis-2.1 gdal-bin -y
sudo -u postgres psql -c "CREATE DATABASE forest_fires;"
sudo -u postgres psql -d forest_fires -c "CREATE EXTENSION POSTGIS;"
sudo -u postgres psql -c "CREATE USER ubuntu WITH PASSWORD 'ubuntu';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE forest_fires TO ubuntu;"

# Run Postgres script
cd ~/forest-fires/code
python data_setup/create_postgres_dts.py makefiles/year_list.pkl
