#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import logging

#Parseo de argumentos
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--origen')
parser.add_argument('--destino')
parser.add_argument('--log')

args = parser.parse_args()
###############################################

#Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler(args.log)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

#Hora de inicio del script
logger.info('Arrancando script')
################################################

#rsync
#Si el directorioB no existe se crea
os.system("rsync -avh " + args.origen + " " + args.destino)


#Hora de finalización del script
logger.info('Script finalizado')



