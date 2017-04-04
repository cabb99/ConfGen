#!/usr/bin/python
##################################################################################################
#Ideas para mejorar
#Imprimir en Fin/ el metodo usado
#Definir el tipo demolecula antes de generar los archivos y cambiar los parametros (n, p, l, pl, nl, np, npl, x?)
#Escoger los tipos de dinamicas a correr (estabilizacion, enfriamiento, cooling, steered)
##################################################################################################

import os,sys,getopt, errno, subprocess

#Caracteristicas del sistema (Modificar aca)
def soul(user):
	global My_Charmm, My_Namd
	#Usuario predeterminado
	user = "eduardo" if user == None else user 
	#Comandos de los usuarios
	if user == "Carlos":
		My_Charmm="/home/lammps/Programas/CHARMM_top"
		My_Namd="/usr/local/bin/charmrun ++local +p4 /usr/local/bin/namd2 +idlepoll +devices 1,2"
	elif user == "Mirko":
		My_Charmm="/home/mirko/Sebastian/CHARMM/toppar"
		My_Namd="/home/mirko/NAMD/charmrun +p4 /home/mirko/NAMD/namd2 +idlepoll +devices 1,2"
	elif user == "Hugo":
		My_Charmm="/home/lammps/Programas/CHARMM_top"
		My_Namd="/usr/local/bin/charmrun +p4 /usr/local/bin/namd2 +idlepoll"
	elif user == "cuda":
		My_Charmm="/home/cuda/Programas/CHARMM_top"
		My_Namd="/home/cuda/Programas/NAMD/charmrun +p4 /home/cuda/Programas/NAMD/namd2 +idlepoll +devices 0,1"
	elif user == "cuda2":
		My_Charmm="/home/cuda2/Programas/CHARMM_top"
		My_Namd="/home/cuda2/Programas/NAMD/charmrun +p4 /home/cuda2/Programas/NAMD/namd2 +idlepoll +devices 0,1"
	elif user == "cuda3":
		My_Charmm="/home/cuda3/Programas/CHARMM_top"
		My_Namd="/home/cuda3/Programas/NAMD/charmrun +p4 /home/cuda3/Programas/NAMD/namd2 +idlepoll +devices 0,1"
	elif user == "any":
		My_Charmm="$$Charm_path"
		My_Namd="$$Namd_cmd"
	elif user == "eduardo":
		My_Charmm="/home/eduardo/Programas/NAMD/toppar"
		My_Namd="/home/eduardo/Programas/NAMD/charmrun +p2 /home/eduardo/Programas/NAMD/namd2 +idlepoll +devices 0,1"
	elif user == "brad":
		My_Charmm="/home/brad/Programas/NAMD_2.9_Linux-x86_64-multicore-CUDA/toppar"
		My_Namd="/usr/local/bin/charmrun +p4 /usr/local/bin/namd2 +idlepoll +devices 0,1"
	elif user == "pitts":
		My_Charmm="/home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/toppar"
		My_Namd="/home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/charmrun +p2 /home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/namd2 +idlepoll +devices 0"
	else:
		print "El usuario no esta registrado, registrelo en el modulo soul"
		print user
		sys.exit(2)

#Informacion de ayuda
def usage():
	print "\n\
Modo de empleo:\n\
Confgen.py [-p *.pdb] [-s *.psf] [-f *_fixed.pdb] [-t tiempo(ns)]\n\
             [-P Presion(atm)] [-T Temp(C)] [- I Puerto_imd]\n\n\
Este programa permite crear archivos de configuracion para NAMD utilizando una\n\
metodologia estandar. En caso se requiera modificar esta metodologia modifique\n\
los archivos que se encuentran en el mismo directorio que este programa.\n\n\
-p,   --pdb       Archivo pdb con informacion de coordenadas [ionized.pdb]\n\
-s,   --psf       Archivo psf con informacion de coordenadas [ionized.psf]\n\
-c,   --conf      Archivos de configuracion usado para la dinamica [Original]\n\
-f,   --fixed     Archivo fixed con informacion de partes del\n\
                  pdb que se mantendran fijas [autofix.pdb]\n\
      --restraint Si se usa se ejercera restraint\n\
      --res_force Fuerza que se ejercera para el restraint\n\
      --res_file  Archivo con coordenadas del pdb a las que se ejercera\n\
                  restraint y multiplicador de fuerza [restraint.pdb]\n\
-t,   --tiempo    Tiempo en ns que dura la simulacion [1ns]\n\
-T,   --temp      Temperatura en grados Celcius [37C]\n\
-P,   --press     Presion del sistema en atmosferas [1atm]\n\
-I,   --imd       Puerto IMD al que se conectara, Rec: 3000-3200 [nulo]\n\
      --freq      Frecuencia del IMD [4ps]\n\
-r,   --recursive Trabaja con todos los pdbs de la carpeta\n\
-u,   --usuario   Selecciona el usuario de la computadora en la que correra\n\
                  la dinamica: Mirko, Carlos, Hugo, Ana, any\n\
      --auto      Comienza la dinamica apenas termine con el archivo de configuracion\n\
      --debug     Otorga datos para debug (Guardelos en un log)\n\
-h,   --help      Escribe informacion de ayuda y sale\n\n\
Archivos de configuracion:\n\
Original, MHC\n\n\
Recuerde escribir los archivos de entrada y el tiempo"

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

#Tomar los argumentos con calma
def main(argv):
	global pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug, user, recursive, auto, conf, resgen ,restraint, restraint_file, restraint_force
	
	#Booleans
	psf_b=fix_b=res_b=tim_b=False
	#Archivos
	pdb=psf=fix=restraint_file=''
	#Generadores
	psfgen=fixgen=resgen=False
	#Valores por defecto
	temp = 310
	press = 1.0
	time = 1
	IMDport = 0
	IMDfreq = 4
	debug = False
	user = None
	recursive=False
	auto=False
	conf='Original'
	restraint=0
	restraint_force=0.1
		
	try:
		opts,args = getopt.getopt(argv, "p:s::c::f::T::t:I::i::Hu:rP:", ["help", "pdb=", "psf=", "conf=", "fixed=", "Temp=", "temp=", "press=", "Press=", "time=", "tiempo=", "IMD=", "imd=", "freq=", "recursive", "usuario=", "auto", "debug","restraint","res_force=","res_file="])	
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	for opt, arg in opts:
		#Archivo pdb
		if opt in ("-p", "--pdb"):     
			pdb = arg
			try:
				PDB=open(pdb)
				PDB.close
			except IOError:			
				print "No se pudo leer el pdb"
				sys.exit(2)
			if pdb == '':
				print "Error: no se especifico un pdb"
				sys.exit(2)                
			
			
		#Archivo psf
		elif opt in ("-s", "--psf"): 
			psf = arg
			psf_b=True
			try:
				PSF=open(psf)
				PSF.close
			except IOError:			
				print "No se pudo leer el psf"
				sys.exit(2)
			if psf == '':
				print "No se especifico un psf"
				sys.exit(2)                   
		
		#Opciones de configuracion
		elif opt in ("-c", "--conf"):
			if arg in ['MHC','Original']:
				conf=arg
			else:
				print "Error: Archivos de configuracion no especificado"
				sys.exit(2) 
		
		#Archivo fixed:	
		elif opt in ("-f", "--fixed"):			
			fix = arg
			fix_b=True
			try:
				FIX=open(fix)
				FIX.close
			except IOError:			
				print "No se pudo leer el fixed"
				sys.exit(2)
			if fix == '':
				print "No se especifico un fix, se creara uno"      
		
		#Archivo del restraint
		elif opt in ("res_file"):
			restraint=1
			restraint_file=arg
			res_b=True
			try:
				RES_FILE=open(restraint_file)
				RES_FILE.close
			except IOError:			
				print "No se pudo leer el archivo restraint"
				sys.exit(2)
			if restraint_file == '':
				print "Error: no se especifico un archivo de restraint"
				sys.exit(2)  
		 
		#Opcion restraint
		elif opt in ("restraint"):
			restraint=1
		
		#Fuerza del restraint
		elif opt in ("res_force"):
			restraint=1
			try:
				restraint_force=float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para la fuerza de restraint"
				sys.exit(2)
			
		#Temperatura		
		elif opt in ("--temp","-T", "--Temp"):
			try:
				temp = int(arg) + 273
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la temperatura"
				sys.exit(2)
		
		#Presion
		elif opt in ("--press","-P", "--Press"):
			try:
				press = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para la presion"
				sys.exit(2)
		
		#Tiempo de dinamica
		elif opt in ("--time", "-t", "--tiempo"):
			tim_b=True
			try:
				time = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para el tiempo"
				sys.exit(2)
		
		#Puerto IMD
		elif opt in ("-I", "-IMD", "--imd"):
			try:
				IMDport = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para el puerto IMD"
				sys.exit(2)
	
		#Frecuencia de IMD
		elif opt in ("--freq"):
			try:
				IMDfreq = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la frecuencia de IMD"
				sys.exit(2)
		
		#Opcion de Usuario
		elif opt in ("-u, --usuario"):
			try:
				user = arg
			except ValueError:			
				print "No se especifico un valor para el usuario"
				sys.exit(2)
		
		#Opcion recursivo
		elif opt in ("-r", "--recursive"):
			recursive = True
		
		#Opcion debug
		elif opt in ("--debug"):
			debug = True
		
		#Opcion auto
		elif opt in ("--auto"):
			auto = True			
		
		#Opcion help
		elif opt in ("-h", "--help"):
			usage()
			sys.exit(2)		
		
		#Opciones invalidas
		else:
			print "Opcion invalida: " + opt + "\n pruebe ConfGen.py --help para mas informacion"
			usage()
			sys.exit(2) 
	
	#Calculo de opciones correlacionadas
	if not psf_b:
		psfgen=True
	if not fix_b:
		fixgen=True
	if conf=='MHC':
		if not tim_b:
			time=40
		restraint=1
	if restraint:
		resgen=True
			
	#Imprimir las opciones elegidas
			
#Crear el psf y fixed
def core(pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug, Conf,resgen ,restraint, restraint_file, restraint_force):
	if psfgen:
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
		subprocess.call('vmd -dispdev text ' + pdb + ' -e psfgen.pgn > psfgen.log',shell=True)
		#Ahora el pdb y el psf activos son:
		psf=str(pdb[:-4])+'_ionized.psf'	
		pdb=str(pdb[:-4])+'_ionized.pdb'
		try:
			PSF=open(psf)
			PSF.close()
		except IOError:
			print "No se creo el psf correctamente"
			sys.exit(2)

	#Crear el fixed
	if fixgen:
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
		subprocess.call("vmd -dispdev text " + psf + " " + pdb + " -e fixgen.pgn > fixgen.log",shell=True)
		#Ahora el fix activo es:
		fix='autofix.pdb'
		try:
			FIX=open(fix)
			FIX.close()
		except IOError:
			print "No se creo el fixed correctamente"
			sys.exit(2)
	
	#Crear el restraint
	if resgen:
		print "No se ha especificado un archivo restraint"		
		print "Creando restraint..."
		#Copiar el archivo para crear restraint
		if conf=='MHC':
			GEN=open(My_Soul + '/MHC_resgen.pgn')
			GENo=open('MHC_resgen.pgn','w+')
			for line in GEN:
				line=line.replace('$$THIS_PATH',str(My_Pos))
				line=line.replace('$$NAME',str(pdb[:-4]))
				GENo.write(line)
			GEN.close	
			GENo.close
			GENo=open('MHC_resgen.pgn')
			GENo.close
			GENlog=open('MHC_resgen.log','w+')
			subprocess.call(['vmd', '-dispdev', 'text', '-e', 'MHC_resgen.pgn', psf, pdb], stdout=GENlog)
			GENlog.close()
			restraint_file='restraint.pdb'
			try:
				RES=open(restraint_file)
				RES.close()
			except IOError:
				print "No se creo el restraint correctamente"
				sys.exit(2)
		else:
			try:
				RES_FILE=open(restraint_file)
				RES_FILE.close
			except ValueError:			
				print 'Algoritmo para crear restraint no especificado'
				sys.exit(2)	
	
	#Confirmacion de los datos
	print "El pdb es " + pdb
	print "El psf es " + psf
	if restraint:
		print "El restraint es " + str(restraint_file)
		print "La fuerza del restraint es " + str(restraint_force)
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
		try:
			Files.remove(restraint_file)
		except ValueError:
			pass
		
		for ori in OriFiles:
				try:
					Files.remove(ori)
				except ValueError:
					ori=ori
		for f in Files:
			os.system ("mv " + f + " Build")

	#Abrir los otros archivos para asegurarse que existan (y conservar el pdb)
	parts=10.0
	part=0.0	

	#Copiar el pdb a Data
	try:
		PDB=open(pdb)
		pdblen=0
		for line in PDB:
			pdblen+=1
		PDB.close()
		pdbi=0
	except ValueError:			
		print "No se pudo leer el pdb: " + pdb
		sys.exit(2)
	#Copiar el psf a Data
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
	#Copiar el fixed a Data
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
	#Copiar el restraint a Data
	if restraint:
		try:
			RES=open(restraint_file)
			RESo=open('Data/'+restraint_file,'w+')
			for line in RES:
				RESo.write(line)
			RES.close()
			RESo.close()
		except ValueError:			
			print "No se pudo abrir el restraint: " + restraint_file
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
	a=0
	boo=0
	print 'Obteniendo dimensiones de la caja...'
	if debug == True:
		print 'xmin, ymin, zmin, xmax, ymax, zmax'
	PDB=open(pdb)
	PDBo=open('Data/'+pdb,'w+')
	for line in PDB:
		pdbi+=1
		PDBo.write(line)
		if len(line)>4:
			if line[0:4]=='ATOM':
				x,y,z=[float(line[30:38]),float(line[38:46]),float(line[46:54])]
				a=a+1
				#Encontrar limites de la caja
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
				if x<>None:
					xmin = x if xmin > x else xmin
					xmax = x if xmax < x else xmax
				if y<>None:
					ymin = y if ymin > y else ymin
					ymax = y if ymax < y else ymax
				if z<>None:
					zmin = z if zmin > z else zmin
					zmax = z if zmax < z else zmax
				#xc1= xc1 + x
				#yc1= yc1 + y
				#zc1= zc1 + z
			#xc1=xc1/a
			#yc1=yc1/a
			#zc1=zc1/a
			if debug == True:	
				if boo == 1:	
					print str(xmin) + ", " + str(ymin) + ", " + str(zmin) + ", " + str(xmax) + ", " + str(ymax) + ", " + str(zmax) 
					boo = 0
		if pdbi % int(pdblen/parts) == 0 :
			per= (part/parts) * 100			
			print str(int(per)) + '%'
			part +=1
	PDB.close()
	PDBo.close()
	print '100%'	
	print "El pdb se leyo correctamente"

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
Numero total de atomos: " + str(a)

	#Calcular el numero de pasos
	step_per_ns = 500.0 #Se suponen 500 pasos/ns
	steps = int(round(time * step_per_ns*1000,-2))
	
	#Calcular el tiempo de equilibracion
	equil_time=int(round((temp-10)*100+20000,-4))

	#Escribir los archivos de configuracion
	print "Escribiendo los archivos de configuracion..."

	## Ubicacion de los archivos
	if Conf=='Original':
		CONFS=((My_Soul+'/Confs/Original/allmin-noprot.conf','min-np.conf'),	(My_Soul+'/Confs/Original/allMD-noprot.conf','minMD-np.conf'), (My_Soul+'/Confs/Original/allmin.conf','min-all.conf'),(My_Soul+'/Confs/Original/allequil.conf','equil-all.conf'),(My_Soul+'/Confs/Original/allMD-ntp.conf','MD-ntp.conf'),(My_Soul+'/Confs/Original/allMD-ntv.conf','MD-ntv.conf'),(My_Soul+'/Confs/Original/allMD-cool.conf','MD-cool.conf'))
	elif Conf=='MHC':
		CONFS=(
		(My_Soul+'/Confs/MHC/min-np.conf'   ,'min-np.conf'   ),
		(My_Soul+'/Confs/MHC/minMD-np.conf' ,'minMD-np.conf' ),
		(My_Soul+'/Confs/MHC/min-all.conf'  ,'min-all.conf'  ),
		(My_Soul+'/Confs/MHC/equil-all.conf','equil-all.conf'), 
		(My_Soul+'/Confs/MHC/MD-ntp.conf'   ,'MD-ntp.conf'   ),
		(My_Soul+'/Confs/MHC/MD-ntv.conf'   ,'MD-ntv.conf'   ))
	SCR=open('Dynamics.sh','w+')
	SCR.write('date\n')
	if IMDport <> 0:
		SCR.write('echo "La dinamica de ' +  pdb[:-4] +' se podra ver en el puerto ' + str(IMDport) + '"' +'\n')
		SCR.write('echo "VMD: vmd `pwd`/' + psf + ' `pwd`/' + pdb+ '"\n')
	else:
		SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha comenzado en:"\n')
		SCR.write('pwd\n')
	comm0=''
	comm1=''
	comm2=''
	comm3='catlog.py -o Fin/all.log '
	comm4='catdcd -o Fin/all.dcd '
	
	#Reemplaza los valores deseados en los archivos de configuracion (*.conf)
	for Confin,Confout in CONFS:
		CONFin=open(Confin)
		CONFout=open("Conf/"+Confout,'w+')
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
			line=line.replace('$$equil_time',str(equil_time))
			line=line.replace('$$restraint_on',str(restraint))
			line=line.replace('$$restraint_f',str(restraint_force))
			line=line.replace('$$restraint',str(restraint_file))

			if IMDport <> 0:		
				line=line.replace('$$IMD','1')
			else:
				line=line.replace('$$IMD','0')
			CONFout.write(line)
		#Escribe los comandos necesarios para Dynamics.sh
		comm0=comm0 + "if [ -e Conf/" + Confout + " ]; then mv Conf/" + Confout + " Data/" + Confout + " ; fi \n"		
		comm1=comm1 + My_Namd + " Data/" + Confout + " > Logs/" + Confout[:-5] + ".log\n"
		comm2=comm2 + "if [ -e Data/" + Confout + " ]; then mv Data/" + Confout + " Conf/" + Confout + " ; fi \n"		
		comm3=comm3 + "Logs/" + Confout[:-5] + ".log "
		comm4=comm4 + "Data/" + Confout[:-5] + ".dcd "
	comm3 = comm3 + "\n"
	comm4 = comm4 + "\n"
	comm5 = 'cp ' + psf + ' Fin/\n'
	comm6 = 'catdcd -stride 100 -o Fin/all_stride100.dcd Fin/all.dcd\n'
	comm7 = 'ssh lammps@192.168.0.249 mkdir /home/lammps/Escritorio/Resultados_Dinamicas/'+pdb[:-4]+'\n'   
	comm8 = 'scp Fin/all_stride100.dcd Fin/'+psf+' lammps@192.168.0.249:/home/lammps/Escritorio/Resultados_Dinamicas/'+pdb[:-4]+'\n'
	
	SCR.write('#Mover de Conf a Data\n')
	SCR.write(comm0)
	SCR.write('#Correr las dinamicas\n')
	SCR.write(comm1)
	SCR.write('#Mover de Data a Conf\n')
	SCR.write(comm2)
	SCR.write('#Unir los logs\n')	
	SCR.write(comm3)
	SCR.write('#Unir los dcds\n')
	SCR.write(comm4)
	SCR.write('#Copiar el psf\n')
	SCR.write(comm5)
	SCR.write('#Crear un resumen\n')
	SCR.write(comm6)
	#SCR.write('#Crear un directorio de resumen en lammps\n')
	#SCR.write(comm7)
	#SCR.write('#Copiar el dcd y el psf a lammps\n')
	#SCR.write(comm8)
	SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha concluido"\n')
	SCR.write('date\n')
	SCR.close()
	CONFin.close()
	CONFout.close()
	print "Finalizacion con exito"

if __name__ == '__main__':
	main(sys.argv[1:])
	My_Pos=get_pos()[:-1]
	My_Soul=get_path()[:-1]
	if recursive==False:
		OriFiles = os.listdir('.')	#Lee los archivos originales
		soul(user)
		core(pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug,conf,resgen ,restraint, restraint_file, restraint_force)
		if auto==False:
			print "Para ejecutar la dinamica utilize el comando:"
			print "cd " + My_Pos
			print "sh Dynamics.sh"
		else:
			os.system("cd " + My_Pos)
			os.system("sh Dynamics.sh")
	else:
		import shutil
		#Buscar lista de pdb
		PDBlist=[]
		for files in os.listdir("."):
			if files.endswith(".pdb"):
				PDBlist=PDBlist + [files]
		TASK=open("Task.sh","w+")
		if not os.path.exists("PDBs"):
			try:
				os.makedirs("PDBs")
			except OSError, e:
				if e.errno != errno.EEXIST:
					raise
		for pdb in PDBlist:
			print "Trabajando con " + pdb
			#Crear directorios
			if not os.path.exists(pdb[:-4]):
				try:
					os.makedirs(pdb[:-4])
				except OSError, e:
					if e.errno != errno.EEXIST:
						raise
			#Mover pdb al directorio y a un backup
			shutil.copy(pdb, "PDBs")	
			shutil.move(pdb, pdb[:-4])
			#Correr Confgen -p * en cada directorio
			try:	
				os.chdir("./" + pdb[:-4])
				My_Pos=get_pos()[:-1]
				fixgen=True
				psfgen=True
				psf=''
				fix=''
				OriFiles = os.listdir('.')
				soul(user)
				core(pdb, psf, fix, temp, press, time, IMDport, IMDfreq, psfgen, fixgen, debug, conf,resgen ,restraint, restraint_file, restraint_force)
				os.chdir("..")
			except OSError, e:
				if e.errno != errno.EEXIST:
					raise
			#Escribe un archivo para correr todas las dinamicas
			My_Pos=get_pos()[:-1]
			TASK.write("cd " + My_Pos + "/" + pdb[:-4] + "\n")
			TASK.write("sh Dynamics.sh\n\n")
		TASK.close()
		if auto ==False:
			print "Para correr la dinamica de todas las carpetas utilize el comando:\n sh Task.sh"
		else:
			os.system("sh Task.sh")
	


