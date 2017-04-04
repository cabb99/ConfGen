#!/usr/bin/python
#Ideas para mejorar
#Imprimir en Fin/ el metodo usado
#Definir el tipo demolecula antes de generar los archivos y cambiar los parametros (n, p, l, pl, nl, np, npl, x?)
#Escoger los tipos de dinamicas a correr (estabilizacion, enfriamiento, cooling, steered)
#Copiar .psf al Fin
import os,sys

#Encontrarme a mi mismo
def get_path():
	import pat
	PAT=str(pat).split()[3][1:-9]
	if PAT[-1] <> "/":
		PAT = PAT + "/"
	return PAT

#Encontrar donde estoy
def get_pos():
	os.system('pwd>path.log')
	a=open('path.log')
	PATH=a.readline()[:-1]
	if PATH[-1] <> "/":
		PATH = PATH + "/"
	a.close()
	os.system('rm path.log')
	return PATH

#Caracteristicas del sistema (Modificar aca)
My_Pos=get_pos()[:-1]
My_Soul=get_path()[:-1]
My_Charmm="/home/lammps/Programas/CHARMM_top"
My_Namd="/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2"

#Tomar los argumentos con calma
import sys, getopt
import os, errno
import subprocess
def main(argv):
	global pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug
	pdb=''
	psfgen=False
	psf=''
	fixgen=False
	fix=''
	temp = 310
	press = 1.0
	time = 1
	IMDport = 0
	IMDfreq = 4
	debug = False
	try:
		opts,args = getopt.getopt(argv, "p:s::f::T::t:I::i::H::", ["help", "pdb", "psf", "fixed", "Temp", "temp", "press", "Press", "time", "tiempo", "IMD", "imd", "freq"])	
	except getopt.GetoptError:
		print "Error, getopt!?"
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-p", "--pdb"):     
			pdb = arg
			fixgen=True
			psfgen=True
			try:
				PDB=open(pdb)
				PDB.close
			except ValueError:			
				print "No se pudo leer el pdb"
				sys.exit(2)
			if pdb == '':
				print "Error: no se especifico un pdb"
				sys.exit(2)                
		elif opt in ("-s", "--psf"): 
			psf = arg
			psfgen=False
			if psf == '':
				print "No se especifico un psf"
				sys.exit(2)                   
		elif opt in ("-f", "--fixed"):			
			fix = arg
			fixgen=False
			if fix == '':
				print "No se especifico un fix, se creara uno"      
		elif opt in ("--temp","-T", "--Temp"):
			try:
				temp = int(arg) + 273
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la temperatura"
				sys.exit(2)
		elif opt in ("--press","-P", "--Press"):
			try:
				press = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para la presion"
				sys.exit(2)
		elif opt in ("--time", "-t", "--tiempo"):
			try:
				time = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para el tiempo"
				sys.exit(2)
		elif opt in ("-I", "-IMD", "--imd"):
			try:
				IMDport = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para el puerto IMD"
				sys.exit(2)
		elif opt in ("--freq"):
			try:
				IMDfreq = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la frecuencia de IMD"
				sys.exit(2)
		elif opt in ("--debug"):
			debug = True		
		elif opt in ("-h", "--help"):
				print "\n\
Modo de empleo:\n\
Confgen.py [-p *.pdb] [-s *.psf] [-f *_fixed.pdb] [-t tiempo(ns)]\n\
             [-P Presion(atm)] [-T Temp(C)] [- I Puerto_imd]\n\n\
Este programa permite crear archivos de configuracion para NAMD utilizando una\n\
metodologia estandar. En caso se requiera modificar esta metodologia modifique\n\
los archivos que se encuentran en el mismo directorio que este programa.\n\n\
-p,   --pdb       Archivo pdb con informacion de coordenadas [ionized.pdb]\n\
-s,   --psf       Archivo psf con informacion de coordenadas [ionized.psf]\n\
-f,   --fixed     Archivo fixed con informacion de partes del\n\
                  pdb que se mantendran fijas [autofix.pdb]\n\
-t,   --tiempo    Tiempo en ns que dura la simulacion [1ns]\n\
-T,   --temp      Temperatura en grados Celcius [37C]\n\
-P,   --press     Presion del sistema en atmosferas [1atm]\n\
-I,   --imd       Puerto IMD al que se conectara, Rec: 3000-3200 [nulo]\n\
      --freq      Frecuencia del IMD [4ps]\n\
      --debug     Otorga datos para debug (Guardelos en un log)\n\
-h,   --help      Escribe informacion de ayuda y sale\n\n\
Recuerde escribir los archivos de entrada y el tiempo"
				sys.exit(2)		
		else:
			print "Opcion invalida: " + opt + "\n pruebe ConfGen.py --help para mas informacion"
			sys.exit(2) 
			
#Crear el psf y fixed
def core(pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug):
	if psfgen == True:
		print "No se ha especificado un archivo psf"	
		print "Creando pdb y psf..."	
		#Copiar y modificar el archivo psfgen	
		GEN=open(My_Soul + '/psfgen.pgn')
		GENo=open('psfgen.pgn','w+')
		for line in GEN:
			line=line.replace('$$THIS_PATH',str(My_Pos))
			line=line.replace('$$NAME',str(pdb[:-4]))
			GENo.write(line)
		GEN.close	
		GENo.close
		GENo=open('psfgen.pgn')
		GENo.close
		os.system('vmd -dispdev text ' + pdb + ' -e psfgen.pgn > psfgen.log')
		#Ahora el pdb y el psf activos son:
		psf=str(pdb[:-4])+'_ionized.psf'	
		pdb=str(pdb[:-4])+'_ionized.pdb'

	if fixgen == True:
		print "No se ha especificado un archivo fixed"		
		print "Creando fixed..."
		#Copiar el archivo fixgen
		GEN=open(My_Soul + '/fixgen.pgn')
		GENo=open('fixgen.pgn','w+')
		for line in GEN:
			line=line.replace('$$THIS_PATH',str(My_Pos))
			line=line.replace('$$NAME',str(pdb[:-4]))
			GENo.write(line)
		GEN.close	
		GENo.close
		GENo=open('fixgen.pgn')
		GENo.close
		os.system("vmd -dispdev text " + psf + " " + pdb + " -e fixgen.pgn > fixgen.log")
		#Ahora el fix activo es:
		fix='autofix.pdb'

	#Confirmacion de los datos
	print "El pdb es " + pdb
	print "El psf es " + psf
	print "El fixed es " + str(fix)
	print "La temperatura es " + str(temp) + " K"
	print "La presion es de " + str(press) + " atm"
	print "La dinamica sera de " + str(time) + " ns"
	if IMDport <> 0:
		print "Se conectara con el IMD en el puerto " + str(IMDport)
		print "La frecuencia de la simulacion es de " + str(IMDfreq)
	else:
		print "La simulacion no se conectara con IMD"

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

	if not os.path.exists('Build') and psfgen == True:
		try:
			os.makedirs('Build')
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise

	if psfgen == True:	
		Files = os.listdir('.')
		Files.remove('Build')
		Files.remove('Data')
		Files.remove('Fin')
		Files.remove('Logs')
		Files.remove('Conf')
		Files.remove(psf)
		Files.remove(pdb)
		Files.remove(fix)
		for ori in OriFiles:
				try:
					Files.remove(ori)
				except ValueError:
					ori=ori
		for f in Files:
			os.system ("mv " + f + " Build")

	#Abrir los otros archivos para asegurarse que existan (y conservar el pdb)
	superpdb=[]
	parts=100.0
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
			if len(line)>4:
				if line[0:4]=='ATOM':
					superpdb=[[(line[31:38]),(line[39:46]),(line[47:54])]]
			if pdbi % int(pdblen/parts) == 0 :
				per= (part/parts) * 100			
				print str(int(per)) + '%'
				part +=1
		PDB.close()
		PDBo.close()
		print '100%'	
		print "El pdb se leyo correctamente"
	except ValueError:			
		print "No se pudo leer el pdb: " + pdb
		sys.exit(2)

	try:
		PSF=open(psf)
		PSFo=open('Data/'+psf,'w+')
		for line in PSF:
			PSFo.write(line)
		PSF.close()
		PSFo.close()
	except ValueError:			
		print "No se pudo abrir el psf: " + psf
		sys.exit(2)

	try:
		FIX=open(fix)
		FIXo=open('Data/'+fix,'w+')
		for line in FIX:
			FIXo.write(line)
		FIX.close()
		FIXo.close()
	except ValueError:			
		print "No se pudo abrir el fix: " + fix
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
	if debug == True:
		print 'xmin, ymin, zmin, xmax, ymax, zmax'
	for x, y, z in superpdb:
		if debug == True:
			if xmin > x or ymin > y or zmin > z or xmax < x or ymax < y or zmax < z:
				boo=1
		#Fijar cualquier valor a min y max
		xmin = x if xmin == None else xmin
		ymin = y if ymin == None else ymin
		zmin = z if zmin == None else zmin
		xmax = x if xmax == None else xmax
		ymax = y if ymax == None else ymax
		zmax = z if zmax == None else zmax
		
		#Comparar con los demas
		xmin = x if xmin > x else xmin
		ymin = y if ymin > y else ymin
		zmin = z if zmin > z else zmin
		xmax = x if xmax < x else xmax
		ymax = y if ymax < y else ymax
		zmax = z if zmax < z else zmax
		#xc1= xc1 + x*1/float(len(superpdb))
		#yc1= yc1 + y*1/float(len(superpdb))
		#zc1= zc1 + z*1/float(len(superpdb))
		if debug == True:	
			if boo == 1:	
				print str(xmin) + ", " + str(ymin) + ", " + str(zmin) + ", " + str(xmax) + ", " + str(ymax) + ", " + str(zmax) 
				boo = 0
	x = xmax - xmin
	y = ymax - ymin
	z = zmax - zmin

	#VMD toma como centro c1, estoy tomando c, habra alguna diferencia?
	xc= (xmax + xmin)/2
	yc= (ymax + ymin)/2
	zc= (zmax + zmin)/2
	#xc=xc1
	#yc=yc1
	#zc=zc1

	print "Dimensiones de la caja:\n\
xmin = " + str(xmin) + "\n\
xmax = " + str(xmax) + "\n\
ymin = " + str(ymin) + "\n\
ymax = " + str(ymax) + "\n\
zmin = " + str(zmin) + "\n\
zmax = " + str(zmax) + "\n\
Centro: " + str(xc) + ", " +  str(yc) + ", " + str(zc) + "\n\
Dimensiones: " + str(x) + ", " +  str(y) + ", " + str(z) + "\n\
Numero total de atomos: " + str(len(superpdb))

	#Olvidar un poco para hacer espacio
	superpdb=[]

	#Calcular el numero de pasos
	step_per_ns = 500.0 #Se suponen 500 pasos/ns
	steps = int(round(time * step_per_ns*1000,-2))

	#Escribir los archivos de configuracion
	print "Escribiendo los archivos de configuracion..."

	## Ubicacion de los archivos
	CONFS=((My_Soul+'/allmin-noprot.conf','Data/min-np.conf'),(My_Soul+'/allMD-noprot.conf','Data/minMD-np.conf'), (My_Soul+'/allmin.conf','Data/min-all.conf'),(My_Soul+'/allequil.conf','Data/equil-all.conf'),(My_Soul+'/allMD-ntp.conf','Data/MD-ntp.conf'),(My_Soul+'/allMD-ntv.conf','Data/MD-ntv.conf'),(My_Soul+'/allMD-cool.conf','Data/MD-cool.conf'))

	SCR=open('Dynamics.sh','w+')
	SCR.write('date\n')
	if IMDport <> 0:
		SCR.write('echo "La dinamica de ' +  pdb[:-4] +' se podra ver en el puerto ' + str(IMDport) + '"' +'\n')
		SCR.write('echo "VMD: vmd `pwd`/' + psf + ' `pwd`/' + pdb+ '"\n')
	else:
		SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha comenzado en:"\n')
		SCR.write('pwd\n')
	comm1=''
	comm2='catlog.py -o Fin/all.log '
	comm3='catdcd -o Fin/all.dcd '
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
			line=line.replace('$$CHARMM_PATH',str(My_Charmm))
			if IMDport <> 0:		
				line=line.replace('$$IMD','1')
			else:
				line=line.replace('$$IMD','0')
			CONFout.write(line)
		SCR.write(My_Namd + " " + Confout + " > Logs/" + Confout[5:-5] + ".log\n")
		comm1=comm1 + "if [ -e "+Confout+" ]; then mv " + Confout + " Conf/" + Confout[5:] + " ; fi \n"
		comm2=comm2 + "Logs/" + Confout[5:-5] + ".log "
		comm3=comm3 + "Data/" + Confout[5:-5] + ".dcd "
	comm2 = comm2 + "\n"
	comm3 = comm3 + "\n"
	SCR.write(comm1)
	SCR.write(comm2)
	SCR.write(comm3)
	SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha concluido"\n')
	SCR.write('date\n')
	SCR.close()
	CONFin.close()
	CONFout.close()
	print "Finalizacion con exito"
	print "Para ejecutar la dinamica utilize el comando:"
	print "cd " + My_Pos
	print "sh Dynamics.sh"

if __name__ == '__main__':
	main(sys.argv[1:])
	OriFiles = os.listdir('.')	#Lee los archivos originales
	core(pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug)

