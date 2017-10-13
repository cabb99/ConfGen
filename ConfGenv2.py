#!/usr/bin/python
##################################################################################################
#Ideas para mejorar
#Imprimir en Fin/ el metodo usado
#Definir el tipo demolecula antes de generar los archivos y cambiar los parametros (n, p, l, pl, nl, np, npl, x?)
#Escoger los tipos de dinamicas a correr (estabilizacion, enfriamiento, cooling, steered)
##################################################################################################

import os,sys,getopt, errno, subprocess

#Caracteristicas del sistema (Modificar aca)

NAMD_parameters={"Carlos":
                {'Charmm':"/home/cab22/Programs/vmd/plugins/noarch/tcl/trunctraj1.5/toppar/",
                'Namd':"./charmrun ++local +p2 ./namd2 +idlepoll",
                "namd_path":'/home/cab22/Programs/namd/namd2',
                "charmrun_path":'/home/cab22/Programs/namd/charmrun'
                }
            ,"Mirko":
                {'Charmm':"/home/mirko/Sebastian/CHARMM/toppar"
                ,'Namd':"/home/mirko/NAMD/charmrun +p4 /home/mirko/NAMD/namd2 +idlepoll +devices 1,2"}
            ,"Hugo":
                {'Charmm':"/home/lammps/Programas/CHARMM_top"
                ,'Namd':"/usr/local/bin/charmrun +p4 /usr/local/bin/namd2 +idlepoll"}
            ,"cuda":
                {'Charmm':"/home/cuda/Programas/CHARMM_top"
                ,'Namd':"/home/cuda/Programas/NAMD/charmrun +p4 /home/cuda/Programas/NAMD/namd2 +idlepoll +devices 0,1"}
            ,"cuda2":
                {'Charmm':"/home/cuda2/Programas/CHARMM_top"
                ,'Namd':"/home/cuda2/Programas/NAMD/charmrun +p4 /home/cuda2/Programas/NAMD/namd2 +idlepoll +devices 0,1"}
            ,"cuda3":
                {'Charmm':"/home/cuda3/Programas/CHARMM_top"
                ,'Namd':"/home/cuda3/Programas/NAMD/charmrun +p4 /home/cuda3/Programas/NAMD/namd2 +idlepoll +devices 0,1"}
            ,"any":
                {'Charmm':"$$Charm_path"
                ,'Namd':"$$Namd_cmd"}
            ,"eduardo":
                {'Charmm':"/home/eduardo/Programas/NAMD/toppar"
                ,'Namd':"/home/eduardo/Programas/NAMD/charmrun +p2 /home/eduardo/Programas/NAMD/namd2 +idlepoll +devices 0,1"}
            ,"brad":
                {'Charmm':"/home/brad/Programas/NAMD_2.9_Linux-x86_64-multicore-CUDA/toppar"
                ,'Namd':"/usr/local/bin/charmrun +p4 /usr/local/bin/namd2 +idlepoll +devices 0,1"}
            ,"pitts":
                {'Charmm':"/home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/toppar"
                ,'Namd':"/home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/charmrun +p2 /home/pitts/Documents/NAMD_CVS-2016-05-02_Linux-x86_64-multicore-CUDA/namd2 +idlepoll +devices 0"}
            }
 

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

#Crear el psf y fixed
def core(pdb, args):
    #Create the psf
    if args.psfgen:
        print "No se ha especificado un archivo psf"
        print "Creando pdb y psf..."
        #Copiar y modificar el archivo psfgen
        print pdb
        with open(args.path + '/psfgen.pgn') as GEN, open('psfgen.pgn','w+') as GENo:
            for line in GEN:
                line=line.replace('$$THIS_PATH',str(args.pos))
                line=line.replace('$$NAME',str(pdb[:-4]))
                GENo.write(line)
        subprocess.call('vmd -dispdev text ' + pdb + ' -e psfgen.pgn > psfgen.log',shell=True)
        #Ahora el pdb y el psf activos son:
        args.psf=str(pdb[:-4])+'_ionized.psf'
        pdb=str(pdb[:-4])+'_ionized.pdb'
        try:
            PSF=open(args.psf)
            PSF.close()
        except IOError:
            print "No se creo el psf correctamente"
            sys.exit(2)
    else:
        shutil.copy("../"+args.psf, ".")

    #Crear el fixed
    if args.fixgen:
        print "No se ha especificado un archivo fixed"
        print "Creando fixed..."
        #Copiar el archivo fixgen
        with open(args.path + '/fixgen.pgn') as GEN, open('fixgen.pgn','w+') as GENo:
            for line in GEN:
                line=line.replace('$$THIS_PATH',str(args.pos))
                line=line.replace('$$NAME',str(pdb[:-4]))
                GENo.write(line)
        subprocess.call("vmd -dispdev text " + args.psf + " " + pdb + " -e fixgen.pgn > fixgen.log",shell=True)
        #Ahora el fix activo es:
        args.fix='autofix.pdb'
        try:
            FIX=open(args.fix)
            FIX.close()
        except IOError:
            print "No se creo el fixed correctamente"
            sys.exit(2)
    else:
        shutil.copy("../"+args.fix, ".")

    #Crear el restraint
    if args.resgen:
        print "No se ha especificado un archivo restraint"
        print "Creando restraint..."
        #Copiar el archivo para crear restraint
        if args.conf=='MHC':
            with open(args.path + '/MHC_resgen.pgn') as GEN, open('MHC_resgen.pgn','w+') as GENo:
                for line in GEN:
                    line=line.replace('$$THIS_PATH',str(args.pos))
                    line=line.replace('$$NAME',str(pdb[:-4]))
                    GENo.write(line)
            with open('MHC_resgen.log','w+') as GENlog:
                subprocess.call(['vmd', '-dispdev', 'text', '-e', 'MHC_resgen.pgn', psf, pdb], stdout=GENlog)
            args.restraint_file='restraint.pdb'
            try:
                RES=open(args.restraint_file)
                RES.close()
            except IOError:
                print "No se creo el restraint correctamente"
                sys.exit(2)
        else:
            try:
                RES_FILE=open(args.restraint_file)
                RES_FILE.close()
            except ValueError:
                print 'Algoritmo para crear restraint no especificado'
                sys.exit(2)
    elif args.restraint_file:
        shutil.copy("../"+args.restraint_file, ".")

    #Confirmacion de los datos
    print "El pdb es " + pdb
    print "El psf es " + args.psf
    if args.restraint:
        print "El restraint es " + str(args.restraint_file)
        print "La fuerza del restraint es " + str(args.restraint_force)
    print "El fixed es " + str(args.fix)
    print "La temperatura es " + str(args.temp) + " K"
    print "La presion es de " + str(args.press) + " atm"
    print "La dinamica sera de " + str(args.time) + " ns"
    if args.imd <> 0:
        print "Se conectara con el IMD en el puerto " + str(args.imd)
        print "La frecuencia de la simulacion es de " + str(args.IMDfreq)
    else:
        print "La simulacion no se conectara con IMD"

    #Ajustes menores
    press=args.press*1.01325 #La presion en el conf se da en bares

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

    if not os.path.exists('Build') and args.psfgen == True:
        try:
            os.makedirs('Build')
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

    if args.psfgen:
        Files = os.listdir('.')
        Files.remove('Build')
        Files.remove('Data')
        Files.remove('Fin')
        Files.remove('Logs')
        Files.remove('Conf')
        Files.remove(args.psf)
        Files.remove(pdb)
        Files.remove(args.fix)
        try:
            Files.remove(args.restraint_file)
        except ValueError:
            pass

        for ori in args.orifiles:
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
        PSF=open(args.psf)
        PSFo=open('Data/'+args.psf,'w+')
        for line in PSF:
            PSFo.write(line)
        PSF.close()
        PSFo.close()
    except ValueError:
        print "No se pudo abrir el psf: " + args.psf
        sys.exit(2)
    #Copiar el fixed a Data
    try:
        FIX=open(args.fix)
        FIXo=open('Data/'+args.fix,'w+')
        for line in FIX:
            FIXo.write(line)
        FIX.close()
        FIXo.close()
    except ValueError:
        print "No se pudo abrir el fix: " + args.fix
        sys.exit(2)
    #Copiar el restraint a Data
    if args.restraint:
        try:
            RES=open(args.restraint_file)
            RESo=open('Data/'+args.restraint_file,'w+')
            for line in RES:
                RESo.write(line)
            RES.close()
            RESo.close()
        except ValueError:
            print "No se pudo abrir el restraint: " + args.restraint_file
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
    if args.debug == True:
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
                if args.debug == True:
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
            if args.debug == True:
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
    steps = int(round(args.time * step_per_ns*1000,-2))

    #Calcular el tiempo de equilibracion
    equil_time=int(round((args.temp-10)*100+20000,-4))

    #Escribir los archivos de configuracion
    print "Escribiendo los archivos de configuracion..."

    ## Ubicacion de los archivos
    if args.conf=='Original':
        CONFS=((args.path+'/Confs/Original/allmin-noprot.conf','min-np.conf'),    (args.path+'/Confs/Original/allMD-noprot.conf','minMD-np.conf'), (args.path+'/Confs/Original/allmin.conf','min-all.conf'),(args.path+'/Confs/Original/allequil.conf','equil-all.conf'),(args.path+'/Confs/Original/allMD-ntp.conf','MD-ntp.conf'),(args.path+'/Confs/Original/allMD-ntv.conf','MD-ntv.conf'),(args.path+'/Confs/Original/allMD-cool.conf','MD-cool.conf'))
    elif args.conf=='MHC':
        CONFS=(
        (args.path+'/Confs/MHC/min-np.conf'   ,'min-np.conf'   ),
        (args.path+'/Confs/MHC/minMD-np.conf' ,'minMD-np.conf' ),
        (args.path+'/Confs/MHC/min-all.conf'  ,'min-all.conf'  ),
        (args.path+'/Confs/MHC/equil-all.conf','equil-all.conf'),
        (args.path+'/Confs/MHC/MD-ntp.conf'   ,'MD-ntp.conf'   ),
        (args.path+'/Confs/MHC/MD-ntv.conf'   ,'MD-ntv.conf'   ))
    SCR=open('Dynamics.sh','w+')
    SCR.write('date\n')
    if args.imd <> 0:
        SCR.write('echo "La dinamica de ' +  pdb[:-4] +' se podra ver en el puerto ' + str(args.imd) + '"' +'\n')
        SCR.write('echo "VMD: vmd `pwd`/' + args.psf + ' `pwd`/' + pdb+ '"\n')
    else:
        SCR.write('echo "La dinamica de ' +  pdb[:-4] +' ha comenzado en:"\n')
        SCR.write('pwd\n')
    comm0=''
    comm1=''
    comm2=''
    comm3='catlog.py -o Fin/all.log '
    comm4='catdcd -o Fin/all.dcd '
    My_Charmm=NAMD_parameters[args.user]['Charmm']
    My_Namd=NAMD_parameters[args.user]['Namd']
    
    #Copy the program to the folder
    if 'namd_path' in NAMD_parameters[args.user]:
        namd_path=NAMD_parameters[args.user]['namd_path']
        shutil.copy(namd_path,'.')
    if 'charmrun_path' in NAMD_parameters[args.user]:
        charmrun_path=NAMD_parameters[args.user]['charmrun_path']
        shutil.copy(charmrun_path,'.')
    
    #Copy the parameters to the folder
    shutil.copy(NAMD_parameters[args.user]['Charmm']+'/par_all27_prot_na.prm','Data')
    
    

    #Reemplaza los valores deseados en los archivos de configuracion (*.conf)
    for Confin,Confout in CONFS:
        CONFin=open(Confin)
        CONFout=open("Conf/"+Confout,'w+')
        for line in CONFin:
            line=line.replace('$$pdb',str(pdb))
            line=line.replace('$$psf',str(args.psf))
            line=line.replace('$$temp',str(args.temp))
            line=line.replace('$$press',str(args.press))
            line=line.replace('$$fix',str(args.fix))
            line=line.replace('$$xc',str(xc))
            line=line.replace('$$yc',str(yc))
            line=line.replace('$$zc',str(zc))
            line=line.replace('$$x',str(x))
            line=line.replace('$$y',str(y))
            line=line.replace('$$z',str(z))
            line=line.replace('$$steps',str(steps))
            line=line.replace('$$IMDport',str(args.imd))
            line=line.replace('$$IMDfreq',str(args.IMDfreq))
            line=line.replace('$$CHARMM_PATH',str('.'))
            line=line.replace('$$equil_time',str(equil_time))
            line=line.replace('$$restraint_on',str(args.restraint))
            line=line.replace('$$restraint_f',str(args.restraint_force))
            line=line.replace('$$restraint',str(args.restraint_file))

            if args.imd <> 0:
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
    comm5 = 'cp ' + args.psf + ' Fin/\n'
    comm6 = 'catdcd -stride 100 -o Fin/all_stride100.dcd Fin/all.dcd\n'
    comm7 = 'ssh lammps@192.168.0.249 mkdir /home/lammps/Escritorio/Resultados_Dinamicas/'+pdb[:-4]+'\n'
    comm8 = 'scp Fin/all_stride100.dcd Fin/'+ args.psf +' lammps@192.168.0.249:/home/lammps/Escritorio/Resultados_Dinamicas/'+pdb[:-4]+'\n'

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

#Read the arguments
if __name__=="__main__":
    import argparse
    import sys
    import os
    import shutil
    parser = argparse.ArgumentParser(description='Creates multiple NAMD configuration files using several minimization steps. The template configuration files are found in the program folder',
                                     epilog='Recuerde escribir los archivos de entrada y el tiempo')
    parser.add_argument('pdb',action='append',
                        help='Archivo pdb con informacion de coordenadas')
    parser.add_argument('-s','--psf',default='',
                        help='Archivo psf con informacion de coordenadas') 
    parser.add_argument('-c','--conf',choices=['Original','MHC'],default='Original',
                        help='Archivos de configuracion usado para la dinamica')
    parser.add_argument('-f','--fix', default='',
                        help='Archivo fixed con informacion de partes del pdb que se mantendran fijas')
    parser.add_argument('--restraint',action='store_true')
    parser.add_argument('--restraint_force',default=0.1,type=float,
                        help='Fuerza que se ejercera para el restraint')
    parser.add_argument('--restraint_file',default='',
                        help='Archivo con coordenadas del pdb a las que se ejercera restraint y multiplicador de fuerza.')
    parser.add_argument('-t','--time', default=1, type=int,
                        help='Tiempo en ns que dura la simulacion') 
    parser.add_argument('-T','--temp',default=273.15+37, type=float,
                        help='Temperatura en grados Celcius')
    parser.add_argument('-P','--press', default=1., type=float,
                        help='Presion del sistema en atmosferas')
    parser.add_argument('-I','--imd', default=0, type=int,
                        help='Puerto IMD al que se conectara')
    parser.add_argument('--IMDfreq',default=1, type=int,
                        help='Frecuencia del IMD')
    #parser.add_argument('-r','--recursive', 
    #                    help='Trabaja con todos los pdbs de la carpeta)
    parser.add_argument('-u','--user',choices=NAMD_parameters.keys(),default='Carlos',
                        help='Selecciona el usuario de la computadora en la que correra la dinamica')
    parser.add_argument('--auto',action='store_true',
                        help='Comienza la dinamica apenas termine con el archivo de configuracion')
    parser.add_argument('--debug',action='store_true',
                        help='Otorga datos para debug (Guardelos en un log)')

    #Read args
    args = parser.parse_args()
    
    #Check pdb exists
    for pdb in args.pdb:
        try:
            PDB=open(pdb)
            PDB.close()
        except IOError:
            print "No se pudo leer el pdb %s"%pdb
            sys.exit(2)
    
    #Check if pdf exists
    if args.psf:
        try:
            PSF=open(args.psf)
            PSF.close
        except IOError:
            print "No se pudo leer el psf %s"%args.psf
            sys.exit(2)
    else:
        print "No se especifico un archivo psf, se creara"
    
    #Check if fix exists
    if args.fix:
        try:
            FIX=open(args.fix)
            FIX.close
        except IOError:
            print "No se pudo leer el fixed"
            sys.exit(2)
    else:
         print "No se especifico un fix, se creara"
    
    #Check if restraint exists
    if args.restraint_file:
        try:
            RES_FILE=open(args.restraint_file)
            RES_FILE.close
            args.restraint=True
        except IOError:
            print "No se pudo leer el archivo restraint"
            sys.exit(2)
    else:
        print "No se especifico un archivo de restraint, no se ejecutara restraint"

    #Related options
    
    args.psfgen= True if not args.psf else False
    args.fixgen=True if not args.fix else False
        
    if args.conf=='MHC':
        if not args.time:
            time=40
        args.restraint=True
    if args.restraint and not args.restraint_file:
        args.resgen=True
    else:
        args.resgen=False
    
    return_path=os.getcwd() #Where the program was called
    args.path=get_path()[:-1] #Where the program is
    
    #Copy the pdbs somewhere
    if not os.path.exists("PDBs"):
        try:
            os.makedirs("PDBs")
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
    
    #Execute main
    with open("Task.sh","w+") as TASK:
        for pdb in args.pdb:
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
            shutil.copy(pdb, pdb[:-4])
            
            try:
                os.chdir("./" + pdb[:-4])
                args.pos=get_pos()[:-1]
                args.orifiles = os.listdir('.')
                core(pdb,args)
                os.chdir(return_path)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            
            #Escribe un archivo para correr todas las dinamicas
            TASK.write("cd " + return_path + "/" + pdb[:-4] + "\n")
            TASK.write("sh Dynamics.sh\n\n")

    if args.auto == False:
        print "Para correr la dinamica de todas las carpetas utilize el comando:\n sh Task.sh"
    else:
        os.system("sh Task.sh")
    
    if args.auto==False:
        print "Para ejecutar la dinamica utilize el comando:"
        print "cd " + return_path
        print "sh Task.sh"
    else:
        os.system("cd " + return_path)
        os.system("sh Task.sh")
    
    
    



    



