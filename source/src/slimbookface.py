#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
import os
import sys
import subprocess
import json
import time
import gettext, locale
import getpass
import re
import time
from datetime import datetime
from os.path import expanduser


sys.path.insert(1, str('../src'))

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, GdkPixbuf


#VARIABLES
userpath = expanduser("~")
user = getpass.getuser()
print(user)
currpath = os.path.dirname(os.path.realpath(__file__))
models_path = '/lib/security/howdy/models/'+ user +'.dat'

try:
    entorno_usu = locale.getlocale()[0]
    if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0:
        idiomas = [entorno_usu]
    else:
        idiomas = ['en']
except:
    idiomas = ['en']

t = gettext.translation('slimbookface',
						currpath+'/locale',
						languages=idiomas,
						fallback=True,)
_ = t.gettext


class SlimbookFace(Gtk.Window):

    def __init__(self):

    # Window set
        Gtk.Window.__init__(self, title='Slimbook Face - Howdy GUI')
        #self.set_resizable(False)
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file(currpath+"/images/iconoface.png")
        self.get_style_context().add_class("bg-image")

    # Window container

        window_grid = Gtk.Grid(column_homogeneous=True,
                                row_homogeneous=True,
                                column_spacing=0,
                                row_spacing=0)
    

        # Logo
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/logo.png',
            width=300,
            height=150,
            preserve_aspect_ratio=True)

        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)
        iconApp.set_halign(Gtk.Align.CENTER)
        
        #Main container
        notebook = Gtk.Notebook.new()
        notebook.set_halign(Gtk.Align.CENTER)
        notebook.set_size_request(850,500)

        window_grid.attach(iconApp, 0, 0, 10, 1)
        window_grid.attach(notebook, 0, 1, 10, 10)

        self.add(window_grid)

    # Load face models from encoded JSON
        
        try:
            encodings = json.load(open(models_path))
        except FileNotFoundError:
            print("No face model known for the user " + user)
            encodings = ""
            
        self.facesTreeView = self.faceList()

    # Creating page grids
        grid_main = Gtk.Grid(column_homogeneous=True,
                              column_spacing=15,
                              row_spacing=20)
        grid_info = Gtk.Grid(column_homogeneous=True,
                              column_spacing=0,
                              row_spacing=20)

        notebook.append_page(grid_main, Gtk.Label.new(_('strmainpage')))
        notebook.append_page(grid_info, Gtk.Label.new(_('strinfopage')))

    # Grid_main components

    # DOWNLOAD DRIVER

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/img01.png',
            width=100,
            height=100,
            preserve_aspect_ratio=True)

        iconDownload = Gtk.Image.new_from_pixbuf(pixbuf)
        iconDownload.set_halign(Gtk.Align.CENTER)

        lbl_download = Gtk.Label(halign=Gtk.Align.CENTER, 
                                 justify=Gtk.Justification.CENTER,
                                 wrap=True)

        if os.system("which howdy")==0:
            lbl_download.set_name("clicked")
            iconDownload.set_name("clicked")
            
        else:
            lbl_download.set_name("released") 
            iconDownload.set_name("released") 


        evnt_download = Gtk.EventBox()
        evnt_download.set_property("name" ,"howdy_download")
        evnt_download.add(iconDownload)
        evnt_download.connect("button_press_event", self._btnDownload_clicked, iconDownload, lbl_download)

        self.button_change(evnt_download, iconDownload, lbl_download)
        
    # ACTIVATE HOWDY
        
        iconActivate = Gtk.Image()
        iconActivate.set_halign(Gtk.Align.CENTER)

        lbl_activate = Gtk.Label(label="",
                                 halign=Gtk.Align.CENTER, 
                                 justify=Gtk.Justification.CENTER,
                                 wrap=True)

        evnt_activate = Gtk.EventBox()
        evnt_activate.set_property("name" ,"howdy_activate")
        evnt_activate.add(iconActivate)
        evnt_activate.connect("button_press_event", self._btnActivate_clicked, iconActivate, lbl_activate)

        # Loading state
        if os.system('cat /lib/security/howdy/config.ini | grep disabled | grep false') == 0:
            iconActivate.set_name("clicked")

        else:
            iconActivate.set_name("released")
            

        self.button_change(evnt_activate, iconActivate, lbl_activate)

    # ACTIVATE LOGIN
    
        iconLogin = Gtk.Image()
        iconLogin.set_halign(Gtk.Align.CENTER)

        lbl_login = Gtk.Label(label="",
                            halign=Gtk.Align.CENTER, 
                            justify=Gtk.Justification.CENTER,
                            wrap=True)

        evnt_login = Gtk.EventBox()
        evnt_login.set_property("name" ,"howdy_login")
        evnt_login.add(iconLogin)
        evnt_login.connect("button_press_event", self._btnLogin_clicked, iconLogin, lbl_login )      


        # Loading state
        if os.path.isfile('/lib/security/howdy/config.ini'):

            if subprocess.getstatusoutput('cat /etc/pam.d/common-auth | grep howdy | grep "#"')[0] == 0:
                iconLogin.set_name("released")
                
            else:
                desktop_env = subprocess.getoutput("echo $XDG_CURRENT_DESKTOP")
                print(desktop_env)

                if not desktop_env.lower().find('kde') == -1:
                    iconLogin.set_name("released")
                else:
                    iconLogin.set_name("clicked")
                

        self.button_change(evnt_login, iconLogin, lbl_login)
        
    # ADD FACE

        iconFace = Gtk.Image()
        iconFace.set_halign(Gtk.Align.CENTER)
        iconFace.set_name("released")

        lbl_face= Gtk.Label(label="Añadir nuevo rostro",
                                 halign=Gtk.Align.CENTER, 
                                 justify=Gtk.Justification.CENTER,
                                 wrap=True)

        evnt_face = Gtk.EventBox()
        evnt_face.set_property("name" ,"howdy_addface")
        evnt_face.add(iconFace)
        evnt_face.connect("button_press_event", self._btnFace_clicked, iconFace, lbl_face)


        lbl_faces = Gtk.Label(halign=Gtk.Align.CENTER, 
                                 justify=Gtk.Justification.CENTER,
                                 wrap=True, 
                                 name = "faces")

        lbl_faces.set_markup("<span><b>"+(_("str_faces"))+"</b></span>")

        self.button_change(evnt_face, iconFace, lbl_face)

    # Scroll window 1

        self.faces = ""
        if encodings == "":
            self.faces = Gtk.Label(label=_('facemodelsempty'))
        else:
            self.faces = Gtk.VBox(spacing=5)
            self.faces.add(self.facesTreeView)

        scrolled_window1 = Gtk.ScrolledWindow()
        scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window1.set_min_content_height(125)
        scrolled_window1.set_min_content_width(300)
        scrolled_window1.add(self.faces)
        

        self.buttonDeleteFace = Gtk.Button(label=(_('removefaceselected')))
        self.buttonDeleteFace.set_sensitive(False)
        self.buttonDeleteFace.set_name("detele_face")
        self.buttonDeleteFace.connect("clicked", self.on_faceDelBtn_clicked, self.facesTreeView.get_selection(), self.facesTreeView)
        
        self.tree_selection = self.facesTreeView.get_selection()
        self.tree_selection.connect("changed", self.onSelectionChanged, self.buttonDeleteFace)

    # Scroll window 2

        self.deviceList()

        scrolled_window2 = Gtk.ScrolledWindow()
        scrolled_window2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window2.set_min_content_height(125)
        scrolled_window2.set_min_content_width(300)
        scrolled_window2.add(self.devices)

        self.tree_selection2 = self.devicesTreeView.get_selection()
        self.tree_selection2.connect("changed", self.onDeviceSelectionChanged, self.buttonDeleteFace)

        lbl_devices = Gtk.Label()
        lbl_devices.set_markup("<span><b>"+_("str_devices")+"</b></span>")

    # Radiobuttons

        rb_box = Gtk.Box()
        
        # Etiqueta reconocimiento
        mode_lbl =Gtk.Label()
        mode_lbl.set_markup("<span><b>"+_("str_recognition")+"</b></span>")
        mode_lbl.set_halign(Gtk.Align.START)
        
    
        rb_fast = Gtk.RadioButton(label=_("Fast"))
        rb_fast.set_name("fast")
        
        rb_box.pack_start(rb_fast, True, True, 0)
        rb_fast.set_halign(Gtk.Align.CENTER)

        rb_balanced = Gtk.RadioButton(label=_("Balanced"), group=rb_fast)
        rb_balanced.set_name("balanced")
        
        rb_box.pack_start(rb_balanced, True, True, 0)
        rb_balanced.set_halign(Gtk.Align.CENTER)

        rb_secure = Gtk.RadioButton(label=_("Secure"), group=rb_fast)
        rb_secure.set_name("secure")
        
        rb_box.pack_start(rb_secure, True, True, 0)
        rb_secure.set_halign(Gtk.Align.CENTER)

        rb_box.set_name("radios")

        try:
            config_file = '/lib/security/howdy/config.ini'
            call = subprocess.getstatusoutput("cat "+config_file)[1]
            patron = "certainty.*=[ ](.*)"
            patron_res = re.compile(patron)
            value = patron_res.search(call).group(1)
            #print(value)

            if value == "4.2":
                rb_fast.set_active(True)
            elif value == "2.8":
                rb_balanced.set_active(True)
            elif value == "2":
                rb_secure.set_active(True)
            else: 
                print("no encajan")
        except:
            print("No se encuentra conf")  

        rb_fast.connect("toggled", self.on_radio_button_toggled)
        rb_balanced.connect("toggled", self.on_radio_button_toggled)
        rb_secure.connect("toggled", self.on_radio_button_toggled)

    # Grid_main attach

        grid_main.attach(evnt_download, 0, 0, 1, 1)
        grid_main.attach(lbl_download, 0, 1, 1, 1)

        grid_main.attach(evnt_activate, 1, 0, 1, 1)
        grid_main.attach(lbl_activate, 1, 1, 1, 1)

        grid_main.attach(evnt_login, 2, 0, 1, 1)
        grid_main.attach(lbl_login, 2, 1, 1, 1)

        grid_main.attach(evnt_face, 3, 0, 1, 1)
        grid_main.attach(lbl_face, 3, 1, 1, 1)

        grid_main.attach(lbl_faces, 0, 2, 2, 1)
        grid_main.attach(lbl_devices, 2, 2, 2, 1)


        grid_main.attach(scrolled_window1, 0, 3, 2, 2)
        grid_main.attach(scrolled_window2, 2, 3, 2, 1)

        grid_main.attach(self.buttonDeleteFace, 0, 5, 2, 1)        
        grid_main.attach(mode_lbl, 2, 4, 2, 1)
        grid_main.attach(rb_box, 2, 5, 2, 1)

        #grid_main.attach(evnt_download, 0, 0, 1, 1)

    # Grid_info components

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/logo.png',
            width=300,
            height=500,
            preserve_aspect_ratio=True)
        SlimbookIcon = Gtk.Image.new_from_pixbuf(pixbuf)
        SlimbookIcon.set_halign(Gtk.Align.CENTER)

        web_link = Gtk.Label()
        web_link.set_markup("<span><b><a href='https://slimbook.es/'>"+_('strvisitwebsite')+"</a></b>    </span>")
        web_link.set_halign(Gtk.Align.CENTER)

        tutorial_link = Gtk.LinkButton(uri=(_('strusermanual')), label=(_('strlabelusermanual')))
        tutorial_link.set_halign(Gtk.Align.CENTER)

        tutorial_link = Gtk.Label()
        tutorial_link.set_markup("<span><b><a href='"+_('strusermanual')+"'>"+_('strlabelusermanual')+"</a></b>    </span>")
        tutorial_link.set_halign(Gtk.Align.CENTER)

        social_media = Gtk.Label()
        social_media.set_markup('<span>'+(_('strsocialnetworks1')) + "<a href='https://www.patreon.com/slimbook'> patreon </a>" +(_('strsocialnetworks2'))+'</span>')
        social_media.set_line_wrap(True)
        social_media.set_justify(Gtk.Justification.CENTER)

        thanks_lbl = Gtk.Label()
        thanks_lbl.set_markup('<span><b>'+_("strthanks1") +'\n'+_("strthanks2")+'</b></span>')
        thanks_lbl.set_justify(Gtk.Justification.CENTER)

        info_lbl = Gtk.Label()
        info_lbl.set_markup("\n<span><b>"+ (_("strinfo1")) +" </b>"+ (_("strinfo2")) +"</span>")
        info_lbl.set_justify(Gtk.Justification.CENTER)


        hbox2 = Gtk.HBox(spacing=5)

        label = Gtk.Label(label=' ')
        label.set_markup("<span><b>"+ (_("strsendemail"))+ "</b></span>")
        label.set_justify(Gtk.Justification.CENTER)
        hbox2.pack_start(label, False, False, 0)
        
        icon = Gtk.Image()
        icon_path = currpath+'/images/copy.png'
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('strcopyemail'))
        
        buttonCopyEmail = Gtk.Button()
        buttonCopyEmail.add(icon)
        buttonCopyEmail.connect("clicked", self.on_buttonCopyEmail_clicked)
        buttonCopyEmail.set_halign(Gtk.Align.CENTER)
        hbox2.pack_start(buttonCopyEmail, False, False, 0)
        hbox2.set_halign(Gtk.Align.CENTER)


        license = Gtk.Label(label='')
        license.set_markup('<b>'+ (_('strlicense1')) +'</b>\n<span size="smaller"><b>'+ (_('strlicense2')) +'</b> '+ (_('strlicense3')) +' '+ (_('strlicense4'))+ '\n'+ (_('strlicense5')) +'</span>')
        license.set_justify(Gtk.Justification.CENTER)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/cc.png',
            width=100,
            height=200,
            preserve_aspect_ratio=True)
        CCIcon = Gtk.Image.new_from_pixbuf(pixbuf)
        CCIcon.set_halign(Gtk.Align.CENTER)

    # SOCIAL
        social_box = Gtk.HBox(spacing=5)
        social_box.set_halign(Gtk.Align.CENTER)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/twitter.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)

        twitter = Gtk.Image.new_from_pixbuf(pixbuf)
        twitter.set_halign(Gtk.Align.CENTER)
        social_box.pack_start(twitter, False, False, 0)
        twitter_link = Gtk.Label(label=' ')
        twitter_link.set_markup("<span><b><a href='https://twitter.com/SlimbookEs'>@SlimbookEs</a></b>	</span>")
        twitter_link.set_justify(Gtk.Justification.CENTER)
        social_box.pack_start(twitter_link, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/facebook.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        
        facebook = Gtk.Image.new_from_pixbuf(pixbuf)
        facebook.set_halign(Gtk.Align.CENTER)
        social_box.pack_start(facebook, False, False, 0)
        
        facebook_link = Gtk.Label(label=' ')
        facebook_link.set_markup("<span><b><a href='https://www.facebook.com/slimbook.es'>Slimbook</a></b>	</span>")
        facebook_link.set_justify(Gtk.Justification.CENTER)
        social_box.pack_start(facebook_link, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/insta.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        
        instagram = Gtk.Image.new_from_pixbuf(pixbuf)
        instagram.set_halign(Gtk.Align.CENTER)
        social_box.pack_start(instagram, False, False, 0)
        
        instagram_link = Gtk.Label(label=' ')
        instagram_link.set_markup("<span><b><a href='https://www.instagram.com/slimbookes/?hl=es'>@slimbookes</a></b></span>")
        instagram_link.set_justify(Gtk.Justification.CENTER)
        social_box.pack_start(instagram_link, False, False, 0)

    # Grid_info attach
        grid_info.attach(web_link, 0, 0, 5, 1)
        grid_info.attach(tutorial_link, 0, 1, 5, 1)
        grid_info.attach(thanks_lbl, 0, 2, 5, 1)
        grid_info.attach(hbox2, 0, 3, 5, 1)

        grid_info.attach(social_media, 0, 4, 5, 1)
        grid_info.attach(social_box, 0, 5, 5, 1)
        grid_info.attach(license, 0, 6, 5, 1)
        grid_info.attach(CCIcon, 0, 7, 5, 1)

    

    def _btnDownload_clicked(self, EventBox, EventButton, iconDownload, lbl_download):


        if iconDownload.get_name() == "released":
            
            self.button_change(EventBox, iconDownload, lbl_download)

            print(iconDownload.get_name())

            self.installDriver()       

            # Release 

            self.hide()
            win = SlimbookFace()
            win.show_all()
            win.connect("destroy", Gtk.main_quit)

            iconDownload.set_name("released") 
            self.button_change(EventBox, iconDownload, lbl_download)
            

            #If there's no selected path for cam, we select one
            if self.get_value("device_path")[-4:] == "none":
                print("No device selected -- triying to select one.")
                device = (self.devicesTreeView.get_model()[0][1])

                # Updating conf
                if self.update_config_file("device_path", "/dev/v4l/by-path/"+device) == 0:
                    print("Device updated to "+device)
            
                print("\nActual conf value: "+self.get_value("device_path"))
        
        else:
            #Software is already downloaded, ask if they want to reinstall
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename='/usr/share/slimbookface/images/icono.png',
                width=90,
                height=90,
                preserve_aspect_ratio=True)
            icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
            icon_MsgDialog.show()

            dialog = Gtk.MessageDialog(message_type= Gtk.MessageType.WARNING,
                image = icon_MsgDialog,
                buttons= Gtk.ButtonsType.YES_NO,
                text=(_('dialogwarning1')))
            
            dialog.format_secondary_text(_("str_reinstallWarn"))
            response = dialog.run()
            
            #En caso afirmativo se le pide la contraseña al usuario y se envian 2 variables, una indicando la operación a realizar y otra con el id del rostro para poder eliminarlo
            if response == Gtk.ResponseType.YES:
                print("Install driver")
                self.installDriver()


            elif response == Gtk.ResponseType.NO:
                print('Operation canceled')

            dialog.destroy()

    def installDriver(self):
        try:
            subprocess.Popen(
                ["x-terminal-emulator --new-tab --hold -e $SHELL -c '"+
                "echo \033[34m---SLIMBOOK FACE---\033[0m;"+
                "echo ;"+
                "echo \033[91m"+ (_('strterminalfollowsteps')) +"\033[0m;"+
                "echo ;"+
                "echo \033[91m"+ (_('strterminalfollowsteps2')) +"\033[0m;"+
                "echo ;"+
                "echo "+ (_('strterminalfollowsteps3')) +";"+
                "read -n 1;"+
                "echo ;"+
                "sudo apt purge howdy -y;"+
                "sudo add-apt-repository ppa:boltgolt/howdy -y;"+
                "sudo apt install howdy;"+
                "echo \033[91m"+ (_('strterminalcompleted')) +"\033[0m;"+
                "touch /tmp/install_completed; "+
                "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

            while not os.path.exists("/tmp/install_completed"):
                time.sleep(2)
            try:
                os.remove("/tmp/install_completed")
            except:
                print("/tmp/install_completed couldn't be removed")
        except:
            print("Installation Failed")

        self.hide()
        win = SlimbookFace()
        win.show_all()
        win.connect("destroy", Gtk.main_quit)

    def _btnActivate_clicked(self, EventBox, EventButton, iconActivate, lbl_activate):
        print("\nActivate clicked")  

        if subprocess.getstatusoutput('which howdy')[0] == 0:
            
            if os.path.isfile('/lib/security/howdy/config.ini'):                
                # If howdy is DISabled
                if os.system('cat /lib/security/howdy/config.ini | grep disabled | grep true') == 0:          
                    # If command enable works

                    cmd = 'pkexec slimbookface-howdy-pkexec enable none'

                    try:
                        subprocess.Popen(
                            ["x-terminal-emulator --new-tab -e $SHELL -c '"+
                            cmd+"; "+
                            "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

                    except:
                        print("Command Failed")
            
                    #subprocess.Popen(["gnome-terminal", "--command="+cmd]) # Funciona a medias ok
                 
                    lbl_activate.set_label(_('disablefacerecognition'))
                    iconActivate.set_name("clicked")
                    self.button_change(EventBox, iconActivate, lbl_activate)
                       
                  
                        
                else:
                    print("howdy recognition wasn't disabled, going to disable")
                    cmd = 'pkexec slimbookface-howdy-pkexec disable none'
            
                    try:
                        subprocess.Popen(
                            ["x-terminal-emulator --new-tab -e $SHELL -c '"+
                            cmd+"; "+
                            "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

                    except:
                        print("Command Failed")

                    #subprocess.Popen(["gnome-terminal", "--command="+cmd]) # Funciona a medias ok

                                   
                    lbl_activate.set_label(_("disablefacerecognition"))
                    iconActivate.set_name("released")
                    self.button_change(EventBox, iconActivate, lbl_activate)
                        
                        
        else:
            print("Needs to install driver")
            self.shoutDriverWarning()

    def _btnLogin_clicked(self, EventBox, EventButton, iconLogin, lbl_login):
        #print("Login clicked")
        if subprocess.getstatusoutput('which howdy')[0] == 0:

            if os.path.isfile('/lib/security/howdy/config.ini'):

                if subprocess.getstatusoutput('cat /etc/pam.d/common-auth | grep howdy | grep "#"')[0] == 0: #if disabled
                    
                    desktop_env = subprocess.getoutput("echo $XDG_CURRENT_DESKTOP")
                    print(desktop_env)

                    if not desktop_env.lower().find('kde') == -1:
                        if os.system('pkexec slimbookface-howdy-pkexec disable_login none') == 0:
                                iconLogin.set_name("released")
                                print("This function is not able for your desktop environment")

                                warn = Gtk.MessageDialog(message_type= Gtk.MessageType.WARNING,
                                    buttons = Gtk.ButtonsType.OK,
                                    text=(_(':(')))
                                
                                warn.format_secondary_text(_("str_kde"))
                                warn.run()
                                warn.close()

                        else: 
                            print("Error disabling in login")

                    else:
                        if os.system('pkexec slimbookface-howdy-pkexec enable_login none') == 0:
                            #Si sale bien, activamos:
                            print("Enabled\n")
                            iconLogin.set_name("clicked")           
                else:
                    
                    if os.system('pkexec slimbookface-howdy-pkexec disable_login none') == 0:
                        print("Disabled\n")
                        iconLogin.set_name("released")
            else: 
                print("El path no existe")

            self.button_change(EventBox, iconLogin, lbl_login)

        else:
            print("Needs to install driver")
            self.shoutDriverWarning()

    def _btnFace_clicked(self, EventBox, EventButton, iconFace, lbl_face): #este no es un toggle button (mec)
        print("Face clicked")

        if subprocess.getstatusoutput('which howdy')[0] == 0:

            iconFace.set_name("clicked") 
            self.button_change(EventBox, iconFace, lbl_face)

            #Saving datetime of file modification
            try:
                dtBefore = os.path.getmtime('/lib/security/howdy/models/'+ user +'.dat')
                lastModModelFileBefore = datetime.fromtimestamp(dtBefore)
            except:
                lastModModelFileBefore = ""
            
            #Opens addface window
            addFace_dialog = AddFaceDialog()
            addFace_dialog.set_modal(True)
            resultado = addFace_dialog.run()

            if resultado == Gtk.ResponseType.ACCEPT:
                addFace_dialog.close_ok()
                addFace_dialog.destroy()

                #Saving again datetime of file modification to check if it has been saved
                #dtAfter = os.path.getmtime('/lib/security/howdy/models/'+ user +'.dat')
                #lastModModelFileAfter = datetime.fromtimestamp(dtAfter)
                
                os.system("sleep 5")

                self.hide()
                win = SlimbookFace()
                win.show_all()
                win.connect("destroy", Gtk.main_quit)

            else:
                addFace_dialog.destroy()        
                iconFace.set_name("released") 
                self.button_change(EventBox, iconFace, lbl_face)           

        else:
            print("Install driver")
            self.shoutDriverWarning()

        iconFace.set_name("released") 
        self.button_change(EventBox, iconFace, lbl_face)

        '''self.hide()
        win = SlimbookFace()
        win.show_all()
        win.connect("destroy", Gtk.main_quit)'''

    def onSelectionChanged(self, tree_selection, buttonDelete):
        buttonDelete.set_sensitive(True)
        
    def onDeviceSelectionChanged(self, tree_selection, button):
    
        os.system("notify-send 'Slimbook Face' '"+ ("We recommend you to choose the IR cam (red light)") +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")
 
        # Getting selection info
        (model, path) = tree_selection.get_selected_rows()

        tree_iter = model.get_iter(path)
        camid = model.get_value(tree_iter, 0)
        device = model.get_value(tree_iter, 1)

        #print(camid+" --- "+device)

        # Updating conf
        if self.update_config_file("device_path", "/dev/v4l/by-path/"+device) == 0:
            print("Device updated to "+device)
        
        print("\nActual conf value: "+self.get_value("device_path"))

    def on_faceDelBtn_clicked(self, button, tree_selection, treeview) :

        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            faceid = model.get_value(tree_iter,0)
            facename = model.get_value(tree_iter, 1)
        
        # Dialog ----------------------------------------
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookface/images/icono.png',
            width=90,
            height=90,
            preserve_aspect_ratio=True)
        icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
        icon_MsgDialog.show()

        dialog = Gtk.MessageDialog(message_type= Gtk.MessageType.QUESTION,
            image = icon_MsgDialog,
            buttons= Gtk.ButtonsType.YES_NO,
            text=(_('dialogwarning1')))
        
        dialog.format_secondary_text((_('dialogwarning2')) +' \"'+ facename + '\" '+ (_('dialogwarning3')))
        response = dialog.run()
        
        #En caso afirmativo se le pide la contraseña al usuario y se envian 2 variables, una indicando la operación a realizar y otra con el id del rostro para poder eliminarlo
        if response == Gtk.ResponseType.YES:
            #if os.system('pkexec slimbookface-howdy-pkexec delete '+ str(faceid)) == 0:
            cmd = 'pkexec slimbookface-howdy-pkexec delete '+ str(faceid)
            
            try:
                subprocess.Popen(
                    ["x-terminal-emulator --new-tab -e $SHELL -c '"+
                    cmd+"; "+
                    "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

            except:
                print("Command Failed")

            #subprocess.Popen(["gnome-terminal", "--command="+cmd]) # Funciona a medias ok

            model.remove(tree_iter) # ---> esto borra directamente de la lista la cara en la interfaz
            

        elif response == Gtk.ResponseType.NO:
            print('Operation canceled')

        dialog.destroy()

    def on_buttonCopyEmail_clicked(self, buttonCopyEmail):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard.set_text('dev@slimbook.es', -1)
        os.system("notify-send 'Slimbook Face' '"+ (_("stremailcopiednotify")) +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")

    def button_change(self, eventbox, icon, label):
        
        box = eventbox.get_property("name")
        state = icon.get_name()
        img = ""
        #print(box+" ----- "+state)

        if box == "howdy_download":
            if state == "clicked":
                img = '/images/img01-white.png'
                label.set_label(_("drivercamreinstall"))
            else:
                img = '/images/img01.png'
                label.set_label(_("drivercaminstall"))

        elif box == "howdy_activate":
            if state == "clicked":
                img = '/images/img02-white.png'
                label.set_label(_("disablefacerecognition"))
            else:
                img = '/images/img02.png'
                label.set_label(_("enablefacerecognition"))

        elif box == "howdy_login":
            
            if state == "clicked":
                img = '/images/img03-white.png'
                label.set_label(_("strdisablewithlogin"))
            else:
                img = '/images/img03.png'
                label.set_label(_("strenablewithlogin"))

        elif box == "howdy_addface":
            if state == "clicked":
                img = '/images/img04-white.png'
                label.set_label(_("straddnewfacemodel"))
            else:
                img = '/images/img04.png'
                label.set_label(_("straddnewfacemodel"))
        
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+img,
            width=100,
            height=100,
            preserve_aspect_ratio=True)
        
        icon.set_from_pixbuf(pixbuf)

    def on_radio_button_toggled(self, radiobutton):
        
        if radiobutton.get_active():
            cert = ""

            if  radiobutton.get_name() == "fast":
                cert = 4.2
            elif radiobutton.get_name() == "balanced":
                cert = 2.8
            elif radiobutton.get_name() == "secure":
                cert = 2 
            else:
                print("Mode not found")

            if not cert == "":
                if self.update_config_file("certainty", str(cert)) == 0:
                    print("Updated to "+radiobutton.get_name())

            config_file = '/lib/security/howdy/config.ini'
            call = subprocess.getstatusoutput("cat "+config_file)[1]
            patron = "certainty.*=[ ](.*)"
            patron_res = re.compile(patron)
            value = patron_res.search(call).group(1)
            print("Actual value: "+value+"\n")

    def update_config_file(self, variable, value):
        print("\nUpdating file...")

        update = variable+"=="+value
        #print(str(update))
        #print("/dev/v4l/by-path/pci-0000:04:00.3-usb-0:3:1.2-video-index0")

        cmd = "pkexec slimbookface-howdy-pkexec update_config "+str(update)
        print(cmd) 

        try:
            subprocess.Popen(
                ["x-terminal-emulator --new-tab -e $SHELL -c '"+
                cmd+"; "+
                "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

        except:
            print("Command Failed")

        #p = subprocess.Popen(["gnome-terminal", "--command="+cmd]) 
  

    def get_value(self, variable):
        config_file = '/lib/security/howdy/config.ini'
        call = subprocess.getstatusoutput("cat "+config_file)[1]
        patron = variable+".*=[ ](.*)"
        patron_res = re.compile(patron)
        value = patron_res.search(call).group(1)
        return value

    def deviceList(self):
        salida = subprocess.getstatusoutput("ls /dev/v4l/by-path")
        #print(salida[1])

        listStoreDevices = Gtk.ListStore(str, str)
        self.devicesTreeView = Gtk.TreeView(model=listStoreDevices)

        if not salida[0] == 0:
                print("0 faces added")
        else:
            
            devices = salida[1].split("\n")
            #print(str(devices))
            cont = 0
            for device in devices:
                dev = device
                #print(i)
                #print (dev)
                device = (cont, str(dev))
                if dev[-1:] == "0":
                    listStoreDevices.append((str(cont), str(dev)))
                    cont = cont+1

        # TreView que almacena el listado de los dispositivos disponibles del usuario
        # Adding column text
        for i, column_title in enumerate(["ID", "Device"]):
            rendererText = Gtk.CellRendererText()
            column_text = Gtk.TreeViewColumn(column_title, rendererText, text=i)
            self.devicesTreeView.append_column(column_text)
        
        self.devices = ""
        self.devices = Gtk.VBox(spacing=5)
        self.devices.pack_start(self.devicesTreeView, False, False, 1)  

    def faceList(self):
        try:
            encodings = json.load(open(models_path))
        except FileNotFoundError:
            print("No face model known for the user " + user)
            encodings = ""

        listStoreFaces = Gtk.ListStore(int, str, str)
        facesTreeView = Gtk.TreeView(model=listStoreFaces)

        if encodings == "":
            print("0 faces added")
        else:
            listStoreFaces = Gtk.ListStore(int, str, str)
            for enc in encodings:
                strface = enc["label"]
                date = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(enc["time"]))
                idface = enc["id"]

                face = (int(idface), str(strface), str(date))
                listStoreFaces.append(face)
            
            #TreView whit added face models
            
            facesTreeView = Gtk.TreeView(model=listStoreFaces)

            for i, column_title in enumerate(["ID", (_("facemodelname")), (_("createddateface"))]):
                rendererText = Gtk.CellRendererText()
                column_text = Gtk.TreeViewColumn(column_title, rendererText, text=i)
                facesTreeView.append_column(column_text)
        

        return facesTreeView

    def shoutDriverWarning(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookface/images/icono.png',
            width=90,
            height=90,
            preserve_aspect_ratio=True)
        icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
        icon_MsgDialog.show()

        dialog = Gtk.MessageDialog(message_type= Gtk.MessageType.QUESTION,
            image = icon_MsgDialog,
            buttons= Gtk.ButtonsType.YES_NO,
            text=(_('dialogwarning1')))
        
        dialog.format_secondary_text(_("str_installWarn"))
        response = dialog.run()
        
        
        if response == Gtk.ResponseType.YES:
            print("Install driver")
            self.installDriver()
            self.hide()
            win = SlimbookFace()
            win.show_all()
            win.connect("destroy", Gtk.main_quit)

        elif response == Gtk.ResponseType.NO:
            print('Operation canceled')

        dialog.destroy()
        
class AddFaceDialog(Gtk.Dialog):

    def __init__(self):
        Gtk.Dialog.__init__(self,
            (_('straddfacetitle')),
            parent=None,
            modal=True,
            destroy_with_parent=True)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(400, 250)
        self.set_icon_from_file(currpath+"/images/iconoface.png")
        self.set_resizable(False)
        self.connect("close", self.close_ok)
        vbox = Gtk.VBox(spacing=5)
        self.get_content_area().add(vbox)
        table = Gtk.Table(n_rows=3, n_columns=3, homogeneous=False)
        vbox.add(table)
        # (0, 0)
        label = Gtk.Label(label=(_('strsteps1')))
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 0, 1, xpadding=5, ypadding=5)
        # (1, 0)
        label = Gtk.Label(label='')
        label.set_markup('<b>'+ (_('strsteps2')) +' </b>'+ (_('strsteps3')))
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 1, 2, xpadding=5, ypadding=5)

        # (2, 0)
        self.entryFaceModelName = Gtk.Entry()
        table.attach(self.entryFaceModelName, 0, 2, 2, 3,
            xpadding=5,
            ypadding=5,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        # (3, 0)
        label = Gtk.Label(label='')
        label.set_markup('<b>'+ (_('strsteps4')) +' </b> '+ (_('strsteps5')))
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 3, 4, xpadding=5, ypadding=5)
        # (4, 0)
        self.buttonShowCam = Gtk.Button(label=(_('strbuttonwebcam')))
        self.buttonShowCam.connect("clicked", self.show_cam)
        table.attach(self.buttonShowCam, 0, 2, 4, 5,
            xpadding=5,
            ypadding=5,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        # (5, 0)
        label = Gtk.Label(label='')
        label.set_markup('<b>'+ (_('strsteps6')) +' </b> '+ (_('strsteps7')) +'\n')
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 5, 6, xpadding=5, ypadding=5)

        self.show_all()

    def show_cam(self, buttonShowCam):

        #if os.system('pkexec slimbookface-howdy-pkexec test none') == 0:	
        #   print("Howdy test")

        cmd = "pkexec slimbookface-howdy-pkexec test none"    
        print(cmd) 


        subprocess.Popen(
            ["x-terminal-emulator -e $SHELL -c '"+
            cmd+"; "+
            "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)



        #subprocess.Popen(["gnome-terminal", "--command=pkexec slimbookface-howdy-pkexec test none & disown"]) # Funciona a medias ok 
        #subprocess.call(["gnome-terminal", "--command=pkexec slimbookface-howdy-pkexec test none "]) # Funciona a medias ok 

        #os.popen("pkexec slimbookface-howdy-pkexec test none ") # No funciona

        #subprocess.Popen("pkexec slimbookface-howdy-pkexec test none ",shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT) #No funciona a medias
 
        #subprocess.run(['pkexec slimbookface-howdy-pkexec test none'], shell=True) # No funciona a medias

        #subprocess.Popen(["gnome-terminal","pkexec slimbookface-howdy-pkexec test none "]) # No funciona en ninguno

        #subprocess.call("pkexec slimbookface-howdy-pkexec test none ", shell = True) # No funciona


        #subprocess.call(['pkexec','slimbookface-howdy-pkexec','test','none'], shell = True) # No funciona porque pkexec no detecta el programa
     
        #subprocess.Popen(['pkexec','slimbookface-howdy-pkexec test none'], shell=True) # No funciona porque pkexec no detecta el programa

    def close_ok(self):
        FaceModelName = self.entryFaceModelName.get_text()
        FaceModelName = '\"'+ FaceModelName + '\"'
        
        cmd = "pkexec slimbookface-howdy-pkexec add "+ FaceModelName + " | grep -i added"    
        print(cmd) 

        try:
            subprocess.Popen(
                ["x-terminal-emulator --new-tab -e $SHELL -c '"+
                cmd+"; "+
                "exit 0'"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

        except:
            print("Command Failed")

        #p = subprocess.Popen(["gnome-terminal", "--command="+cmd]) 


        
        #if os.system('pkexec slimbookface-howdy-pkexec add '+ FaceModelName + ' | grep -i "added a new model"') == 0:
        #    os.system("notify-send 'Slimbook Face' '"+ (_("stralertaddface")) +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")
        #else:
        #    os.system("notify-send 'Slimbook Face' '"+ (_("stralertaddface2")) +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")


if __name__ == "__main__":
	if __file__.startswith('/usr') or os.getcwd().startswith('/usr'):
		sys.path.insert(1, '/usr/share/slimbookface')
	else:
		sys.path.insert(1, os.path.normpath(
			os.path.join(os.getcwd(), '../src')))
	

    #Style provider ------------------------------------------------
	style_provider = Gtk.CssProvider()
	style_provider.load_from_path(currpath+'/css/style.css')

	Gtk.StyleContext.add_provider_for_screen (
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
	win = SlimbookFace()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()
	Gtk.main()
