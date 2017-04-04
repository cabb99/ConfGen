#!/usr/bin/python
import sys, getopt, os, shutil
import ConfGen

#Tomar los argumentos con calma
def main(argv):
	#Argumentos por defecto	
	global task, time, carpetas
	task=''
	dynamics=''
	mdntv=''
	carpeta=''	
	carpetas=[]
	time = 0
	#Tomar argumentos
	try:
		opts,args = getopt.getopt(argv, "t:T::h::", ["help"])
	except getopt.GetoptError:
		print "Error: No se pudieron encontrar los parametros de entrada"
		opts=[('--help','')]

	#Asignar una variable a cada argumento	
	if args <> []:
		for arg in args:
			if arg[-1]=='/':
				carpeta=arg[:-1]
			else:
				carpeta = arg			
			carpetas.append(carpeta)

	for opt, arg in opts:
		if opt in ("-T"):     
			task = arg
		
		elif opt in ("-t"):
			try:
				time = float(arg)
			except ValueError:			
				print "No se especifico un valor numerico para el tiempo"
				sys.exit(2)

#Ayuda acerca del comando
		elif opt in ("--help"):
				print "\n\
Modo de empleo:\n\
addtime.py -t tiempo(ns) [-T ../Task.sh] Directorio(s) \n\n\
Este programa permite aumentar el tiempo de la dinamica una vez haya concluido\n\
utilizando los mismos parametros utilizados en el archivo MD-ntv. Se puede indicar\n\
el directorio de la dinamica o los archivos de la dinamica independientemente.\n\n\
-t                Tiempo extra en nanosegundos\n\
-T                Archivo donde se incluira la tarea(Normalmente Task.sh)\n\
-h,   --help      Escribe informacion de ayuda y sale\n"
				sys.exit(2)		
		else:
			print "Opcion invalida: " + opt + "\n pruebe addtime.py --help para mas informacion"
			sys.exit(2) 

#Revisar que la informacion sea correcta
	if time == 0:
		sys.exit(2)

	if task<>'':
		try:
			TASK=open(task)
			TASK.close()
		except IOError:			
			print "Error: No se pudo leer el archivo de Task"
			sys.exit(2)
	
	#Limpiar la lista de carpetas
	carpetas=list(set(carpetas))

	for carpeta in carpetas:
		Found=0			
		for c in os.listdir('.'):
			if carpeta==c:
				Found=1
		if Found==0:
			print "Error: No se encontro la carpeta " + carpeta
			sys.exit(2)
		
		dynamics= carpeta + '/Dynamics.sh'
		mdntv= carpeta + '/Conf/MD-ntv.conf'

		try:
			DYNAMICS=open(dynamics)
			DYNAMICS.close()
		except IOError:			
			print "Error: No se pudo leer el archivo de Dynamics en la carpeta " + carpeta
			sys.exit(2)

		try:
			MDNTV=open(mdntv)
			MDNTV.close()
		except IOError:			
			print "Error: No se pudo leer el ultimo archivo de MD-ntv en la carpeta " + carpeta
			sys.exit(2)

if __name__ == '__main__':
	main(sys.argv[1:])


for carpeta in carpetas:
	dynamics= carpeta + '/Dynamics.sh'
	#Encontrar el ultimo MD-ntv
	n=1	
	while n<100:
		n=n+1		
		mdntv= carpeta + '/Conf/MD-ntv%i.conf'%n
		try:
			MDNTV=open(mdntv)
			MDNTV.close()
		except IOError:			
			break
	if n>99:
		print 'Realmente mas de 100 dinamicas?'
		sys.exit(2)

	#Modificar Dynamics.sh
	shutil.copyfile(dynamics,'dyn.temp')
	DYNTEMP=open('dyn.temp')
	DYNAMICS=open(dynamics,'w+')
	for line in DYNTEMP:
		if line == 'date\n':
			DYNAMICS.write(line)
		elif line == 'pwd\n':
			DYNAMICS.write(line)
		elif line[0]=='#':
			DYNAMICS.write(line)
		elif len(line)>10:
			if line[0:6]=='catlog':
				DYNAMICS.write(ConfGen.My_Namd + ' Data/MD-ntv%i.conf > Logs/MD-ntv%i.log\n'%(n,n))
				DYNAMICS.write('mv Data/MD-ntv%i.conf Conf/MD-ntv%i.conf\n'%(n,n))
				DYNAMICS.write(line[:-1]+'Logs/MD-ntv%i.log \n' %n)
			elif line[0:6]=='catdcd':
				DYNAMICS.write(line[:-1]+'Data/MD-ntv%i.dcd \n' %n)
			elif line[0:4]=='echo':
				DYNAMICS.write(line)
			else:			
				DYNAMICS.write('#'+line)
		else:
			DYNAMICS.write('#'+line)
	DYNAMICS.close()
	DYNTEMP.close()

	#Crear MD-ntv%i.conf %n
	if n==2:		
		MDNTV=open(carpeta + '/Conf/MD-ntv.conf')
		mdntv1=('MD-ntv','MD-ntv2')
		mdntv2=('MD-ntp','MD-ntv')
	elif n==3:
		MDNTV=open(carpeta + '/Conf/MD-ntv%i.conf'%(n-1))
		mdntv1=('MD-ntv2','MD-ntv3')
		mdntv2=('MD-ntv','MD-ntv2')
	else:
		MDNTV=open(carpeta + '/Conf/MD-ntv%i.conf'%(n-1))
		mdntv1=('MD-ntv%i'%(n-1),'MD-ntv%i'%n)
		mdntv2=('MD-ntv%i'%(n-2),'MD-ntv%i'%(n-1))
	MDNTVb=open(carpeta + '/Data/MD-ntv%i.conf'%n,'w+')
	for line in MDNTV:
		if len(line)>15:
			if line[0:10]=='outputName':
				line=line.replace(mdntv1[0],mdntv1[1])
			if line[0:13]=='set inputname':
				line=line.replace(mdntv2[0],mdntv2[1])
			if line[0:3]=='run':
				line='run %i00000 ;#500/ps'%(time*5) 
		MDNTVb.write(line)
	MDNTV.close()
	MDNTVb.close
	
	#Modificar Task.sh
	if task=='':
		print 'cd '+ConfGen.My_Pos+'/'+carpeta
		print 'sh Dynamics.sh'
	else:
		TASK=open(task,'a')
		TASK.write('\ncd '+ConfGen.My_Pos+'/'+carpeta+'\n')
		TASK.write('sh Dynamics.sh\n')
		TASK.close()
	
	ConfGen.My_Pos
	os.remove('dyn.temp')

