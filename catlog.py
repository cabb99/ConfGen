#!/usr/bin/python
#Tomar los argumentos
import sys
import getopt
def main(argv):
	global logout
	global logins
	global marca
	logout=''
	logins=[]
	marca=False
	try:
		opts,args = getopt.getopt(argv, "o:m", ["help", "grammar="])
	except getopt.GetoptError:
		print "Error, getopt!?"
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-o", "-out"):     
			logout = arg 
			if logout == '':
				print "No se especifico un Log de salida"
				sys.exit(2)                
		elif opt in ("-m", "-marca"):     
			marca = True 
		else:
			print "El parametro " + opt + " no esta especificado"
			sys.exit(2)
	logins=args


if __name__ == '__main__':
	main(sys.argv[1:])

#Juntar los logs
iold=0
inew=0
ib=0
LOGOUT=open(logout,'w+')
for login in logins:
	LOGIN=open(login)
	print "Juntando log " + login
	for line in LOGIN:
		if len(line)>10:
			if line[0:10] == 'GPRESSURE:' or line[0:9] == 'PRESSURE:' or line[0:9] == 'PRESSAVG:' or line[0:10] == 'GPRESSAVG:' or line[0:7] == 'ENERGY:':
				inew=int(line.split()[1])
				i=inew + ib
				if inew == 0:
					ib=ib+iold 				
				iold=inew
				line=line.replace(' '+line.split()[1]+' ',' '+str(i)+' ')
				#Marca de union
				if inew == 0 and marca==True:
					for arg in line.split()[2:]:
						line=line.replace(arg,str(0))
				LOGOUT.write(line)
			if line[0:7] == 'ETITLE:':
				LOGOUT.write(line)

print "Archivos adjuntados con exito en " + logout
