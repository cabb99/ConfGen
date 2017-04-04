#!/usr/bin/python
#Ideas para mejorar
#Imprimir en Fin/ el metodo usado
#Definir el tipo demolecula antes de generar los archivos y cambiar los parametros (n, p, l, pl, nl, np, npl, x?)

#Tomar los argumentos
import sys, getopt
import os, errno
def main(argv):
	global pdb, psf, fix, temp, press, time, IMDport, IMDfreq
	pdb=''
	psf=''
	fix=''
	temp = 310
	press = 1.0
	time = 1
	IMDport = 0
	IMDfreq = 10
	try:
		opts,args = getopt.getopt(argv, "p:s:f::T::t:I::i::H::", ["help", "grammar="])	
	except getopt.GetoptError:
		print "Error, getopt!?"
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-p", "-pdb"):     
			pdb = arg
			if pdb == '':
				print "No se especifico un pdb"
				sys.exit(2)                
		elif opt in ("-s", "-psf"): 
			psf = arg
			if psf == '':
				print "No se especifico un psf"
				sys.exit(2)                   
		elif opt in ("-f", "-fixed"):			
			fix = arg
			if fix == '':
				print "No se especifico un fix, se hara la dinamica minimizando todo de frente"      
		elif opt in ("-temp","-T", "-Temp"):
			try:
				temp = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la temperatura"
				sys.exit(2)
		elif opt in ("-press","-P", "-Press"):
			try:
				press = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la presion"
				sys.exit(2)
		elif opt in ("-time", "-t", "-tiempo"):
			try:
				time = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para el tiempo"
				sys.exit(2)
		elif opt in ("-I", "-i", "-imd"):
			try:
				IMDport = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para el puerto IMD"
				sys.exit(2)
		elif opt in ("-H", "-freq"):
			try:
				IMDfreq = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la frecuencia de IMD"
				sys.exit(2)
		else:
			print "El parametro " + opt + " no esta especificado"
			sys.exit(2) 
			
if __name__ == '__main__':
	main(sys.argv[1:])
#Confirmacion de los datos
print "El pdb es " + pdb
print "El psf es " + psf
print "El fixed es " + str(fix)
print "La temperatura es " + str(temp) + " K"
print "La presion es de " + str(press) + " atm"
print "La dinamica sera de " + str(time) + " ns"
print "Se conectara con el IMD en el puerto " + str(IMDport)

#Ajustes menores
press=press*1.01325 #La presion en el conf se da en bares

#Crear los directorios
if not os.path.exists('Data'):
	try:
		os.makedirs('Data')
	except OSError, e:
		if e.errno != errno.EEXIST:
			raise
if not os.path.exists('Logs'):
	try:
		os.makedirs('Logs')
	except OSError, e:
		if e.errno != errno.EEXIST:
			raise
if not os.path.exists('Conf'):
	try:
		os.makedirs('Conf')
	except OSError, e:
		if e.errno != errno.EEXIST:
			raise
if not os.path.exists('Fin'):
	try:
		os.makedirs('Fin')
	except OSError, e:
		if e.errno != errno.EEXIST:
			raise  

#Abrir los otros archivos para asegurarse que existan (y conservar el pdb)
superpdb=[]
parts=10.0
part=0.0	

try:
	PDB=open(pdb)
	print "Leyendo pdb..."
	PDBo=open('Data/'+pdb,'w+')
	pdblen=0
	for line in PDB:
		pdblen+=1
	PDB.close()
	PDB=open(pdb)
	pdbi=0
	for line in PDB:
		pdbi+=1		
		PDBo.write(line)
		if line.split()[0]=='ATOM':
			superpdb=superpdb+[[float(line[31:38]),float(line[39:46]),float(line[47:54])]]
		if pdbi % int(pdblen/parts) == 0 :
			per= (part/parts) * 100			
			print str(int(per)) + '%'
			part +=1
	PDB.close()
	PDBo.close()
	print "El pdb se leyo correctamente"
except ValueError:			
	print "No se pudo leer el pdb"
	sys.exit(2)

try:
	PSF=open(psf)
	PSFo=open('Data/'+psf,'w+')
	for line in PSF:
		PSFo.write(line)
	PSF.close()
	PSFo.close()
except ValueError:			
	print "No se pudo abrir el psf"
	sys.exit(2)

try:
	FIX=open(fix)
	FIXo=open('Data/'+fix,'w+')
	for line in FIX:
		FIXo.write(line)
	FIX.close()
	FIXo.close()
except ValueError:			
	print "No se pudo abrir el fix"
	sys.exit(2)

#Abrir el pdb y calcular minmax y center

xmin = None
ymin = None
zmin = None
xmax = None
ymax = None
zmax = None
xc1=0
yc1=0
zc1=0
print 'Obteniendo dimensiones de la caja...'
for x, y, z in superpdb:
	xmin = x if xmin == None else xmin
	ymin = y if ymin == None else ymin
	zmin = z if zmin == None else zmin
	xmax = x if xmax == None else xmax
	ymax = y if ymax == None else ymax
	zmax = z if zmax == None else zmax
	
	xmin = x if xmin > x else xmin
	ymin = y if ymin > y else ymin
	zmin = z if zmin > z else zmin
	xmax = x if xmax < x else xmax
	ymax = y if ymax < y else ymax
	zmax = z if zmax < z else zmax
#	xc1= xc1 + x*1/float(len(superpdb))
#	yc1= yc1 + y*1/float(len(superpdb))
#	zc1= zc1 + z*1/float(len(superpdb))


x = xmax - xmin
y = ymax - ymin
z = zmax - zmin

#VMD toma como centro c1, estoy tomando c, habra alguna diferencia?
xc= (xmax + xmin)/2
yc= (ymax + ymin)/2
zc= (zmax + zmin)/2

#Olvidar un poco para hacer espacio
superpdb=[]


#Calcular el numero de pasos
step_per_ns = 500.0 #Se suponen 500 pasos/ns
steps = int(round(time * step_per_ns*1000,-2))

#Escribir los archivos de configuracion
print "Escribiendo los archivos de configuracion..."

## Ubicacion de los archivos
CONFS=(('/home/lammps/Documentos/NAMD/bin/allmin-noprot.conf','Data/min-np.conf'),('/home/lammps/Documentos/NAMD/bin/allMD-noprot.conf','Data/minMD-np.conf'), ('/home/lammps/Documentos/NAMD/bin/allmin.conf','Data/min-all.conf'),('/home/lammps/Documentos/NAMD/bin/allequil.conf','Data/equil-all.conf'),('/home/lammps/Documentos/NAMD/bin/allMD-ntp.conf','Data/MD-ntp.conf'),('/home/lammps/Documentos/NAMD/bin/allMD-ntv.conf','Data/MD-ntv.conf'))

SCR=open('Dynamics.sh','w+')
if IMDport <> 0:
	SCR.write('echo "La dinamica de ' +  pdb[:-4] +' se podra ver en el puerto ' + str(IMDport) + '"' +'\n')
	SCR.write('echo "VMD: vmd `pwd`/' + psf + ' `pwd`/' + pdb+ '"\n')
else:
	SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha comenzado"\n')
comm1=''
comm2='catlog.py -o Fin/all.log '
for Confin,Confout in CONFS:
	CONFin=open(Confin)
	CONFout=open(Confout,'w+')
	for line in CONFin:
		line=line.replace('$$pdb',str(pdb))
		line=line.replace('$$psf',str(psf))
		line=line.replace('$$temp',str(temp))
		line=line.replace('$$press',str(press))
		line=line.replace('$$fix',str(fix))
		line=line.replace('$$xc',str(xc))
		line=line.replace('$$yc',str(yc))
		line=line.replace('$$zc',str(zc))
		line=line.replace('$$x',str(x))
		line=line.replace('$$y',str(y))
		line=line.replace('$$z',str(z))
		line=line.replace('$$steps',str(steps))
		line=line.replace('$$IMDport',str(IMDport))
		line=line.replace('$$IMDfreq',str(IMDfreq))
		if IMDport <> 0:		
			line=line.replace('$$IMD','1')
		else:
			line=line.replace('$$IMD','0')
		CONFout.write(line)
	SCR.write("/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll " + Confout + " > Logs/" + Confout[5:-5] + ".log\n")
	comm1=comm1 + "mv " + Confout + " Conf/" + Confout[5:] + "\n"
	comm2=comm2 + "Logs/" + Confout[5:-5] + ".log "
comm2 = comm2 + "\n"
SCR.write(comm1)
SCR.write(comm2)
SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha concluido exitosamente"\n')
SCR.close()
CONFin.close()
CONFout.close()
print "Finalizacion con exito"


