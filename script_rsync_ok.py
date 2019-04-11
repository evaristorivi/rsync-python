#!/usr/bin/env python
# -*- coding: utf-8 -*-

#rsync - script
#Evaristo R Rivieccio Vega

import os
from subprocess import Popen, PIPE, STDOUT
import argparse
import logging
import sys
import time
import socket
import re
import os
import sys
 
def find_executable(executable, path=None):
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


def validIP(address): 
    coincide=True
    parts = address.split(".") 
    if len(parts) != 4:
        coincide = False 
        return coincide 
    for item in parts: 
        if not 0 <= int(item) <= 255:
            coincide=False 
            return coincide 
    return coincide

#def typechecker(puerto):
#    if isinstance(puerto, int):
#        return True
#    else:
#        return False

def connok(address,puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((address,int(puerto)))
    sock.close()
    if result != 0:
        return False

#######################################################################################################

print "\n"
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



#Variables
parser = argparse.ArgumentParser(description='Script - rsync || Para Cron: tener previamente un par de claves publica/privada')
#Parseo de argumentos
parser.add_argument('-o', '--origen', help='Indica la ubicación a copiar. Tener cuidado con la / final. Por ejemplo: /opt copiará el directorio /opt mientras que /opt/ copiará el contenido de dicho directorio. Ejemplo: -o directorioA/', required=True)
parser.add_argument('-d', '--destino', help='Indica la ubicación de destino SSH. Si no existe, se creará. Es indiferente la / del final. Ejemplo: -d evaristo@192.168.1.11:~/directorioB/', required=True)
parser.add_argument('-l', '--log', help='Especific la ubicación para el fichero de log de este script. Por defecto será la misma ubicación del script. Ejemplo -l rsync.log', default='./rsync.log', required=False)
parser.add_argument('-f', '--force', action='store_true', help='Si está presente esta opción, se forzará la ejecución del script, aun no teniendo permisos root', required=False)
parser.add_argument('-p', '--puerto', help='Especifica el puerto a utilizar para la conexión ssh. Si no se especifica, se utiliza el puerto 22.', type=int, default='22',  required=False)
parser.add_argument('-i', '--identidad', help='Especifica la ruta absoluta o relativa del fichero que contiene la clave privada', required=False, default=False)

#En caso de no introducir los argumentos requeridos, se muestra la ayuda además del mensaje de error.
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    print bcolors.FAIL + "\nLos argumentos -o y -d son obligatorios. \n"+ bcolors.ENDC
    sys.exit(2)
args = parser.parse_args()

#Comprobación root
if os.geteuid() != 0 and args.force != True:
    print bcolors.FAIL + 'Debes tener privilegios root para este script.' + bcolors.ENDC
    print bcolors.WARNING     + '\nBajo tu responsabilidad, puedes forzar la ejecución de este script sin ser root, con la opción -f \n' + bcolors.ENDC
    sys.exit(1)


###############################################

#Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# create a file handler
handler = logging.FileHandler(args.log)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


#Comprobación rsync instalado
if find_executable('rsync')==None:
    logger.error("El paquete rsync es requerido para la ejecución de este script. ")
    sys.exit()


logger.info('Inicio de rsync')
logger.info("Intentando establecer conexión ...")


#Comprobación conexión
ip=args.destino.split("@")[1].split(":")[0]



try:
    validIP(ip)
except ValueError:
    print "Error sintáctico en la dirección IP"
    sys.exit()

#Comprobación argumento conexión
if not validIP(ip):
    logger.error("La dirección IP no es válida")
    sys.exit()



#Comprobar si la conexión es posible
if connok(ip,args.puerto) == False:
    logger.error("Conexión rechazada. Puerto utilizado: " + str(args.puerto) + " - Dirección IP: " + ip)
    print bcolors.FAIL + "Estás utilizando el puerto " + str(args.puerto) + " y la dirección IP: " + ip + " Asegúrate de utilizar la dirección y puertos correctos." + bcolors.ENDC
    sys.exit()

args.puerto=str(args.puerto)


logger.info("Intentando establecer conexión SSH por el puerto " + args.puerto + ' ... OK')


#rsync
#Se inicializa el contador del tiempo de ejecución
start = time.time()

#Si el directorioB no existe se crea
if args.identidad == False:
    shell_command = "rsync -a " + args.origen + " -e \"ssh -o StrictHostKeyChecking=no -p " + args.puerto + "\" " + args.destino
    event = Popen(shell_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = event.communicate()
    #print (output)

else:
    shell_command = "rsync -a " + args.origen + " -e \"ssh -i " + args.identidad + " " + "-o StrictHostKeyChecking=no -p " + args.puerto + "\" " + args.destino
    event = Popen(shell_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = event.communicate()
    #print (output)

#Control de la salida de errores de rsync
if output[0]!='':
    logger.error(output)
    sys.exit()

#Finaliza el contador del tiempo de ejecución
end = time.time()

print bcolors.OKGREEN

#Hora de finalización del script
logger.info("rsync ha finalizado satisfactoriamente. Tiempo total de transferencia: " +  str(end - start) + " segundos")

print "\nScript finalizado" + bcolors.ENDC




