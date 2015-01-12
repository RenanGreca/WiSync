apt-get install python-dev
apt-get install python-pip
wget https://pypi.python.org/packages/source/p/pysendfile/pysendfile-2.0.1.tar.gz
tar -zxvf pysendfile-2.0.1.tar.gz
cd pysendfile-2.0.1
make
cd ..
python pysendfile-2.0.1/setup.py build
python pysendfile-2.0.1/setup.py install