# after cloning repo I had to run these commands, then upgrade the requirements.txt file

pip install setuptools
python -m pip install --upgrade setuptools
python -m pip install -r requirements.txt

mysqlclient/README.md at main  PyMySQL/mysqlclient  GitHub

# for Manjaro
sudo pacman -S gcc
sudo pacman -S pkg-config
pip install mysqlclient

# To run gunicorn server; 
gunicorn app:app
# CTRL + C to stop
