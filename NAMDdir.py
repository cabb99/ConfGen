#!/usr/bin/python
import os, shutil, errno, sys, time

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

#Caracteristicas del sistema
My_Pos=get_pos()[:-1]
My_Soul=get_path()[:-1]

#Tomar los argumentos con calma
import sys, getopt, os, errno, subprocess
def main(argv):
	global time_out
	time_out = 6
	try:
		opts,args = getopt.getopt(argv, "o::h::", ["help", "time_out"])	
	except getopt.GetoptError:
		print "Error, getopt!?"
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-o", "--time_out"):     
			try:
				time_out = int(arg)
			except ValueError:			
				print "No se especifico un valor numerico (entero) para la temperatura"
				sys.exit(2)			
		elif opt in ("-h", "--help"):
				print "\
\nModo de empleo: NAMDdir.py [-t time_out] \n\n\
Este programa permite crear directorios para dinamicas con NAMD utilizando\n\
el programa ConfGen.py. Ademas crea un archivo Task.py para ejecutarlas\n\
de forma serial. \n\n\
-o,   --time_out  Indica el tiempo de espera entre creacion de directorios\n\
                  El tiempo de espera [6] se calcula como: \n\
     [time_out] = [tiempo de creacion de carpeta]/[numero de procesadores] \n\
-h,   --help      Escribe informacion de ayuda y sale"
				sys.exit(2)		
		else:
			print "Opcion invalida: " + opt + "\n pruebe NAMDdir.py --help para mas informacion"
			sys.exit(2) 
			
if __name__ == '__main__':
	main(sys.argv[1:])

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
		os.system(My_Soul + "/ConfGen.py -p " + pdb + " > ConfGen.log &")
		os.chdir("..")
		time.sleep(time_out)	
	except OSError, e:
		if e.errno != errno.EEXIST:
			raise
	#Escribe un archivo para correr todas las dinamicas
	TASK.write("cd " + My_Pos + "/" + pdb[:-4] + "\n")
	TASK.write("sh Dynamics.sh\n\n")
TASK.close()

print "Para correr la dinamica de todas las carpetas utilize el comando:\n sh Task.sh"


	
