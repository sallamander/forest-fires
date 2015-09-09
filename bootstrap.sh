# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
bash Miniconda-latest-Linux-x86_64.sh
echo '' >> ~/.bashrc
echo 'export PATH="/home/ubuntu/miniconda/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install git, clone repo, create conda environment
sudo apt-get update
sudo apt-get install git -y
git clone https://github.com/sallamander/forest-fires.git
cd ~/forest-fires
conda env create

# Unzip data
cd ~/forest-fires/data/
python unzip.py

# Install PostgreSQL and PostGIS extension and create DB
sudo apt-get install postgresql postgresql-contrib postgis postgresql-9.3-postgis-2.1 gdal-bin -y
sudo su postgres -
cd
psql -c "CREATE DATABASE forest_fires;"
psql -d forest_fires -c "CREATE EXTENSION POSTGIS;"
psql -c "CREATE USER ubuntu WITH PASSWORD 'ubuntu';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE forest_fires TO ubuntu;"
exit

# Run Postgres script
cd ~/forest_fires/cpde
python data_setup/create_postgres_dts.py makefiles/year_list.pkl
