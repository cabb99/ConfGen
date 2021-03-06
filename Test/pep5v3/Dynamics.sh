date
echo "La dinamica de pep5v3_ionized se podra ver en el puerto 3000"
echo "VMD: vmd `pwd`/pep5v3_ionized.psf `pwd`/pep5v3_ionized.pdb"
#Mover de Conf a Data
if [ -e Conf/min-np.conf ]; then mv Conf/min-np.conf Data/min-np.conf ; fi 
if [ -e Conf/minMD-np.conf ]; then mv Conf/minMD-np.conf Data/minMD-np.conf ; fi 
if [ -e Conf/min-all.conf ]; then mv Conf/min-all.conf Data/min-all.conf ; fi 
if [ -e Conf/equil-all.conf ]; then mv Conf/equil-all.conf Data/equil-all.conf ; fi 
if [ -e Conf/MD-ntp.conf ]; then mv Conf/MD-ntp.conf Data/MD-ntp.conf ; fi 
if [ -e Conf/MD-ntv.conf ]; then mv Conf/MD-ntv.conf Data/MD-ntv.conf ; fi 
if [ -e Conf/MD-cool.conf ]; then mv Conf/MD-cool.conf Data/MD-cool.conf ; fi 
#Correr las dinamicas
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/min-np.conf > Logs/min-np.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/minMD-np.conf > Logs/minMD-np.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/min-all.conf > Logs/min-all.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/equil-all.conf > Logs/equil-all.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/MD-ntp.conf > Logs/MD-ntp.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/MD-ntv.conf > Logs/MD-ntv.log
/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2 Data/MD-cool.conf > Logs/MD-cool.log
#Mover de Data a Conf
if [ -e Data/min-np.conf ]; then mv Data/min-np.conf Conf/min-np.conf ; fi 
if [ -e Data/minMD-np.conf ]; then mv Data/minMD-np.conf Conf/minMD-np.conf ; fi 
if [ -e Data/min-all.conf ]; then mv Data/min-all.conf Conf/min-all.conf ; fi 
if [ -e Data/equil-all.conf ]; then mv Data/equil-all.conf Conf/equil-all.conf ; fi 
if [ -e Data/MD-ntp.conf ]; then mv Data/MD-ntp.conf Conf/MD-ntp.conf ; fi 
if [ -e Data/MD-ntv.conf ]; then mv Data/MD-ntv.conf Conf/MD-ntv.conf ; fi 
if [ -e Data/MD-cool.conf ]; then mv Data/MD-cool.conf Conf/MD-cool.conf ; fi 
#Unir los logs
catlog.py -o Fin/all.log Logs/min-np.log Logs/minMD-np.log Logs/min-all.log Logs/equil-all.log Logs/MD-ntp.log Logs/MD-ntv.log Logs/MD-cool.log 
#Unir los dcds
catdcd -o Fin/all.dcd Data/min-np.dcd Data/minMD-np.dcd Data/min-all.dcd Data/equil-all.dcd Data/MD-ntp.dcd Data/MD-ntv.dcd Data/MD-cool.dcd 
#Mover el psf
mv pep5v3_ionized.psf Fin/
echo "La dinamica de pep5v3_ionized ha concluido"
date
