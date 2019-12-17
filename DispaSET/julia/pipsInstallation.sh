### Tested on Ubuntu 18.10


sudo apt-get install wget cmake libboost-all-dev libmpich-dev -y

cd ThirdPartyLibs/ASL
sh wgetASL.sh
cd -
cd ThirdPartyLibs/CBC
sh wgetCBC.sh
cd -
cd ThirdPartyLibs/ConicBundle
sh wgetConicBundle.sh
cd -
cd ThirdPartyLibs/METIS
sh wgetMETIS.sh
cd -
cd ThirdPartyLibs/MA27/
sh installMa27.sh
cd -
#### MA57 IS ONLY ACADEMIC!!!!!

#### ARE THOSE REALLY ENOUGH? -> At least it compiles
sudo apt-get install libblas-dev liblapack-dev -y # BLAS LAPACK
sudo apt-get install libmumps-scotch-dev #MUMPS
sudo apt install libblacs-mpi-dev

mkdir build_pips cd build_pips cmake .. make
