#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import re
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk



# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/lib/security/howdy/recorders')

def get_value(variable):
    config_file = '/lib/security/howdy/config.ini'
    call = subprocess.getstatusoutput("cat "+config_file)[1]
    patron = variable+".*=[ ](.*)"
    patron_res = re.compile(patron)
    value = patron_res.search(call).group(1)
    return value


def main(accion, arg2):
    if accion == 'enable':
        os.system('sudo howdy disable 0')

    elif accion == 'test':
        os.system('''sudo howdy test &
        sleep 5
        xdotool key space ''')

    elif accion == 'disable':
        os.system('sudo howdy disable 1')

    if accion == 'enable_login':
        os.system('sudo sh /usr/share/slimbookface/bin/disable_login.sh enable')

    if accion == 'disable_login':
        os.system('sudo sh /usr/share/slimbookface/bin/disable_login.sh disable')

    elif accion == 'add':
        print("Adding")
        #arg2 --> face
        os.system('echo '+ arg2 + ' | sudo howdy add')

    elif accion == 'delete':
        #arg2 --> face
        os.system('sudo howdy remove '+ arg2 +' -y')
        
    elif accion == 'update_config':
        
        #arg2 --> variable==value
        variable = arg2.split("==")[0]
        #print(variable)
        value = arg2.split("==")[1]

        #print(str(variable))
 
        config_file = '/lib/security/howdy/config.ini'
        patron = variable + ".*=.*"

        #print("sudo sed -i 's|"+patron+"|"+variable+" = "+value+"|g' "+config_file)
        subprocess.getstatusoutput("sudo sed -i 's|"+patron+"|"+variable+" = "+value+"|g' "+config_file)
        if variable == "device_path":
            subprocess.getstatusoutput("sudo howdy snapshot")
            

        

if __name__ == "__main__":
    #Se obtiene las variables que se le pasa desde el archivo /usr/share/slimbookface/slimbookface
    main(sys.argv[1], sys.argv[2])