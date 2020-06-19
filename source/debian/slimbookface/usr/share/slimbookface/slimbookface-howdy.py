#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def main(accion, face):
    if accion == 'enable':
        os.system('sudo howdy disable 0')
    elif accion == 'disable':
        os.system('sudo howdy disable 1')
    elif accion == 'add':
        os.system('echo '+ face + ' | sudo howdy add')
    elif accion == 'delete':
        os.system('sudo howdy remove '+ face +' -y')

if __name__ == "__main__":
    #Se obtiene las variables que se le pasa desde el archivo /usr/share/slimbookface/slimbookface
    main(sys.argv[1], sys.argv[2])