#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import logging
import sys
import time

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
parser = argparse.ArgumentParser(description='Script - rsync')
#Parseo de argumentos
parser.add_argument('-o', '--origen', help='Indica la ubicación a copiar. Tener cuidado con la / final. Por ejemplo: /opt copiará el directorio /opt mientras que /opt/ copiará el contenido de dicho directorio. Ejemplo: -o directorioA/', required=True)
parser.add_argument('-d', '--destino', help='Indica la ubicación de destino SSH. Si no existe, se creará. Es indiferente la / del final. Ejemplo: -d evaristo@192.168.1.11:~/directorioB/', required=True)
parser.add_argument('-l', '--log', help='Indica la ubicación para el fichero de log de este script. Ejemplo -l rsync.log', required=True)
parser.add_argument('-f', '--force', action='store_true', help='Si está presente esta opción, se forzará la ejecución del script, aun no teniendo permisos root', required=False)
parser.add_argument('-p', '--puerto', help='Especifica el puerto a utilizar para la conexión ssh. Si no se especifica, se utiliza el puerto 22.', default='22',  required=False)

#En caso de no introducir los argumentos requeridos, se muestra la ayuda además del mensaje de error.
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    print bcolors.FAIL + "\nLos argumentos -o -d y -l son obligatorios. \n"+ bcolors.ENDC
    sys.exit(2)
args = parser.parse_args()

print args.puerto
#Comprobación root
if os.geteuid() != 0 and args.force != True:
    print bcolors.FAIL + 'Debes tener privilegios root para este script.' + bcolors.ENDC
    print bcolors.WARNING     + '\nBajo tu responsabilidad, puedes forzar la ejecución de este script sin ser root, con la opción -f \n' + bcolors.ENDC
    sys.exit(1)


###############################################

#Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler(args.log)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


#Hora de inicio del script
logger.info('Inicio de rsync')

#rsync
#Se inicializa el contador del tiempo de ejecución
start = time.time()

#Si el directorioB no existe se crea
os.system("rsync -ae \"ssh -p \"" + args.puerto + " " + args.origen + " " + args.destino)

#Finalia el contador del tiempo de ejecución
end = time.time()

print bcolors.OKGREEN
print "rsync ha finalizado satisfactoriamente. Tiempo total de transferencia: " +  str(end - start) + " segundos" + bcolors.ENDC

#Hora de finalización del script
logger.info("rsync ha finalizado satisfactoriamente. Tiempo total de transferencia: " +  str(end - start) + " segundos")


