#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import logging
import sys
import time
import socket





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
parser.add_argument('-p', '--puerto', help='Especifica el puerto a utilizar para la conexión ssh. Si no se especifica, se utiliza el puerto 22.', default='22',  required=False)
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
import yum

yb = yum.YumBase()
if yb.rpmdb.searchNevra(name='rsync'):
    logger.info("detectando rsync ... OK")
else:
   logger.error("El paquete rsync es requerido para le ejecución de este script. ")
   sys.exit()


#Hora de inicio del script
logger.info('Inicio de rsync')
logger.info("Intentando establecer conexión SSH por el puerto " + args.puerto)

#Comprobación conexión
ip=args.destino.split("@")[1].split(":")[0]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
result = sock.connect_ex((ip,int(args.puerto)))
if result != 0:
    logger.error("Conexión rechazada. Puerto utilizado: " + args.puerto + " - Dirección IP: " + ip)
    print bcolors.FAIL + "Estás utilizando el puerto " + args.puerto + " y la dirección IP: " + ip + " Asegúrate de utilizar la dirección y puertos correctos." + bcolors.ENDC
    sock.close()
    sys.exit()


logger.info("Intentando establecer conexión SSH por el puerto " + args.puerto + ' ... OK')



#rsync
#Se inicializa el contador del tiempo de ejecución
start = time.time()

#Si el directorioB no existe se crea
if args.identidad == False:
    os.system("rsync -ae \"ssh -o StrictHostKeyChecking=no -p \"" + args.puerto + " " + args.origen + " " + args.destino + " " + '2>/dev/null')
else:
    os.system("rsync -ae \"ssh -i " + args.identidad + " " + "-o StrictHostKeyChecking=no -p \"" + args.puerto + " " + args.origen + " " + args.destino + " " + '2>/dev/null')

#Finalia el contador del tiempo de ejecución
end = time.time()

print bcolors.OKGREEN

#Hora de finalización del script
logger.info("rsync ha finalizado satisfactoriamente. Tiempo total de transferencia: " +  str(end - start) + " segundos")

print "\nScript finalizado" + bcolors.ENDC

