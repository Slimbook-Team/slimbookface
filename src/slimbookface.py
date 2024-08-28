#!/usr/bin/python3
# -*- coding: utf-8 -*-

import v4l2

import cv2
import numpy
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
import configparser
import glob
from datetime import datetime
from os.path import expanduser

sys.path.insert(1, str('../src'))

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, GdkPixbuf, GObject
import cairo

currpath = os.path.dirname(os.path.realpath(__file__))
user = getpass.getuser()
models_path = '/usr/share/dlib/'+ user +'.dat'

_ = gettext.gettext

HOWDY_CONFIG = "/etc/howdy/config.ini"
V4L_PATH = "/dev/v4l/by-path/"

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

       
        self.facesTreeView = Gtk.TreeView()
        for i, column_title in enumerate(["ID", (_("Face name")), (_("Creation date"))]):
            rendererText = Gtk.CellRendererText()
            column_text = Gtk.TreeViewColumn(column_title, rendererText, text=i)
            self.facesTreeView.append_column(column_text)

        self.facesTreeView.set_model(self.get_face_list())
        
        
        # Creating page grids
        grid_main = Gtk.Grid(column_homogeneous=True,
                              column_spacing=15,
                              row_spacing=20)
        grid_info = Gtk.Grid(column_homogeneous=True,
                              column_spacing=0,
                              row_spacing=20)

        notebook.append_page(grid_main, Gtk.Label.new(_('Main')))
        notebook.append_page(grid_info, Gtk.Label.new(_('Information')))

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
        evnt_download.set_sensitive(False)
        #evnt_download.connect("button_press_event", self._btnDownload_clicked, iconDownload, lbl_download)

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
        evnt_activate.connect("button_press_event", self.on_button_activate_clicked, iconActivate, lbl_activate)

        # Loading state
        config = self.get_config()
        if config["core"]["disabled"] == "false":
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
        evnt_login.set_sensitive(False)
        #evnt_login.connect("button_press_event", self._btnLogin_clicked, iconLogin, lbl_login )      

        # Loading state
        if os.path.isfile(HOWDY_CONFIG):

            f = open("/etc/pam.d/common-auth","r")
            lines = f.readlines()
            f.close()
            
            iconLogin.set_name("released")
            for line in lines:
                line = line.strip()
                if line.find("pam_howdy.so") != -1:
                    if line[0] != '#':
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
        evnt_face.connect("button_press_event", self.on_button_face_clicked, iconFace, lbl_face)

        lbl_faces = Gtk.Label(halign=Gtk.Align.CENTER, 
                                 justify=Gtk.Justification.CENTER,
                                 wrap=True, 
                                 name = "faces")

        lbl_faces.set_markup("<span><b>"+(_("Faces"))+"</b></span>")

        self.button_change(evnt_face, iconFace, lbl_face)

        # Scroll window 1

        self.faces = Gtk.VBox(spacing=5)
        self.faces.add(self.facesTreeView)

        scrolled_window1 = Gtk.ScrolledWindow()
        scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window1.set_min_content_height(125)
        scrolled_window1.set_min_content_width(300)
        scrolled_window1.add(self.faces)
        
        self.buttonDeleteFace = Gtk.Button(label=(_('Delete selected face')))
        #self.buttonDeleteFace.set_sensitive(False)
        self.buttonDeleteFace.set_name("detele_face")
        self.buttonDeleteFace.connect("clicked", self.on_button_delete_face_clicked, self.facesTreeView.get_selection(), self.facesTreeView)
        
        self.tree_selection = self.facesTreeView.get_selection()
        #self.tree_selection.connect("changed", self.onSelectionChanged, self.buttonDeleteFace)

        # Scroll window 2

        self.get_device_list()

        scrolled_window2 = Gtk.ScrolledWindow()
        scrolled_window2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window2.set_min_content_height(125)
        scrolled_window2.set_min_content_width(300)
        scrolled_window2.add(self.devices)

        self.tree_selection2 = self.devicesTreeView.get_selection()
        self.tree_selection2.connect("changed", self.on_device_changed, None)

        lbl_devices = Gtk.Label()
        lbl_devices.set_markup("<span><b>"+_("Devices")+"</b></span>")

        # Radiobuttons

        rb_box = Gtk.Box()
        
        # Etiqueta reconocimiento
        mode_lbl =Gtk.Label()
        mode_lbl.set_markup("<span><b>"+_("Recognition level")+"</b></span>")
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
            config = self.get_config()
            value = config["video"]["certainty"]
            
            value = float(value) # check for locale decimal point?
            
            if value >= 4.2:
                rb_fast.set_active(True)
            elif value > 2.0 and value < 4.2:
                rb_balanced.set_active(True)
            elif value <= 2.0:
                rb_secure.set_active(True)
        except:
            print("Failed to read config.ini")  

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
        web_link.set_markup("<span><b><a href='https://slimbook.es/'>"+_('Visit SLIMBOOK website')+"</a></b></span>")
        web_link.set_halign(Gtk.Align.CENTER)


        tutorial_link = Gtk.Label()
        tutorial_link.set_markup("<span><b><a href='https://slimbook.es/en/tutoriales/aplicaciones-slimbook/400-slimbook-face-biometric-recognition-and-dont-enter-more-passwords'>"+_('User manual of Slimbook Face')+"</a></b></span>")
        tutorial_link.set_halign(Gtk.Align.CENTER)

        github_link = Gtk.Label()
        github_link.set_markup("<span><b><a href='https://github.com/slimbook/slimbookface'>"+_('GitHub')+"</a></b></span>")
        github_link.set_halign(Gtk.Align.CENTER)

        translations_link = Gtk.Label()
        translations_link.set_markup("<span><b><a href='https://github.com/slimbook/slimbookface/tree/master/source/src/locale'>"+_('Help us with translations')+"</a></b></span>")
        translations_link.set_halign(Gtk.Align.CENTER)

        link_box1 = Gtk.VBox(spacing = 10)
        link_box1.add(web_link)
        link_box1.pack_start(tutorial_link, True, True, 0)

        link_box2 = Gtk.VBox(spacing = 10)
        link_box2.add(translations_link)
        link_box2.pack_start(github_link, True, True, 0)
        
        tutorial_link = Gtk.Label()
        tutorial_link.set_markup("<span><b><a href='"+_('strusermanual')+"'>"+_('strlabelusermanual')+"</a></b>    </span>")
        tutorial_link.set_halign(Gtk.Align.CENTER)

        social_media = Gtk.Label()
        social_media.set_markup('<span>'+(_('If you want to support the Slimbook team with the development of this app and several more to come, you can do so by joining our')) + "<a href='https://www.patreon.com/slimbook'> patreon </a>" +(_('or buying a brand new Slimbook.'))+'</span>')
        social_media.set_line_wrap(True)
        social_media.set_justify(Gtk.Justification.CENTER)

        thanks_lbl = Gtk.Label()
        thanks_lbl.set_markup('<span><b>'+_("Thanks to boltgolt. The software is provided \"as is\", without") +'\n'+_("warranty of any kind.")+'</b></span>')
        thanks_lbl.set_justify(Gtk.Justification.CENTER)

        info_lbl = Gtk.Label()
        info_lbl.set_markup("\n<span><b>"+ (_("Info:")) +" </b>"+ (_("Contact with us if you find something wrong.")) +"</span>")
        info_lbl.set_justify(Gtk.Justification.CENTER)


        hbox2 = Gtk.HBox(spacing=5)

        label = Gtk.Label(label=' ')
        label.set_markup("<span><b>"+ (_("Contact with us if you find something wrong."))+ "</b></span>")
        label.set_justify(Gtk.Justification.CENTER)
        hbox2.pack_start(label, False, False, 0)
        
        icon = Gtk.Image()
        icon_path = currpath+'/images/copy.png'
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Copy e-mail'))
        
        buttonCopyEmail = Gtk.Button()
        buttonCopyEmail.add(icon)
        #buttonCopyEmail.connect("clicked", self.on_buttonCopyEmail_clicked)
        buttonCopyEmail.set_halign(Gtk.Align.CENTER)
        hbox2.pack_start(buttonCopyEmail, False, False, 0)
        hbox2.set_halign(Gtk.Align.CENTER)

        license = Gtk.Label(label='')
        license.set_markup('<b>'+ (_('You are free to:')) +'</b>\n<span size="smaller"><b>'+ (_('Share:')) +'</b> '+ (_('--copy and redistribute the material in any medium')) +' '+ (_('or format'))+ '\n'+ (_('Slimbook Copyright - License Creative Commons BY-NC-ND 4.0')) +'</span>')
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
        grid_info.attach(link_box1, 1, 0, 2, 2)
        grid_info.attach(link_box2, 3, 0, 2, 2)
        grid_info.attach(thanks_lbl, 0, 2, 6, 1)
        grid_info.attach(hbox2, 0, 3, 6, 1)

        grid_info.attach(social_media, 0, 4, 6, 1)
        grid_info.attach(social_box, 0, 5, 6, 1)
        grid_info.attach(license, 0, 6, 6, 1)
        grid_info.attach(CCIcon, 0, 7, 6, 1)

    def get_config(self):
        
        if os.path.exists(HOWDY_CONFIG):
            config = configparser.ConfigParser()
            config.read(HOWDY_CONFIG)
            return config
        else:
            return configparser.ConfigParser()
        
    def get_device_list(self):
    
        listStoreDevices = Gtk.ListStore(str, str, str)
        self.devicesTreeView = Gtk.TreeView(model=listStoreDevices)
        
        devices = glob.glob("/dev/video*")
        cont = 0
        for dev in devices:
            info = v4l2.query_capabilities(dev)
            if ((info.device_caps & v4l2.CAP_VIDEO_CAPTURE) != 0 ):
                name = info.card
                node = dev
                for lnk in os.listdir(V4L_PATH):
                    target = os.path.realpath(V4L_PATH + os.readlink(V4L_PATH + lnk))

                    if (target == dev):
                        node = lnk
                        break
                
                listStoreDevices.append((str(cont), name, node))
                cont = cont + 1
        

        # TreView que almacena el listado de los dispositivos disponibles del usuario
        # Adding column text
        for i, column_title in enumerate(["ID", "Device"]):
            rendererText = Gtk.CellRendererText()
            column_text = Gtk.TreeViewColumn(column_title, rendererText, text=i)
            self.devicesTreeView.append_column(column_text)
        
        self.devices = ""
        self.devices = Gtk.VBox(spacing=5)
        self.devices.pack_start(self.devicesTreeView, False, False, 1)
        
        try:
            config = self.get_config()
            
            cfg_device = config["video"]["device_path"]
            
            for dev in listStoreDevices:
                if (cfg_device.find(dev[2]) != -1):
                    self.devicesTreeView.set_cursor(dev.path)
        except:
            pass

    def get_face_list(self):
        try:
            encodings = json.load(open(models_path))
        except FileNotFoundError:
            print("No face model known for the user " + user)
            encodings = ""

        model = Gtk.ListStore(int, str, str)

        if encodings == "":
            print("0 faces added")
        else:
            for enc in encodings:
                strface = enc["label"]
                date = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(enc["time"]))
                idface = enc["id"]

                face = (int(idface), str(strface), str(date))
                model.append(face)
            
        
        return model

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

            os.system("pkexec slimbookface-helper update-config video.certainty={0}".format(cert))
            
    def button_change(self, eventbox, icon, label):
        
        box = eventbox.get_property("name")
        state = icon.get_name()
        img = ""
        #print(box+" ----- "+state)

        if box == "howdy_download":
            if state == "clicked":
                img = '/images/img01-white.png'
                label.set_label(_("Howdy is installed"))
            else:
                img = '/images/img01.png'
                label.set_label(_("Howdy is not installed"))

        elif box == "howdy_activate":
            if state == "clicked":
                img = '/images/img02-white.png'
                label.set_label(_("Disable face recognition"))
            else:
                img = '/images/img02.png'
                label.set_label(_("Enable face recognition"))

        elif box == "howdy_login":
            
            if state == "clicked":
                img = '/images/img03-white.png'
                label.set_label(_("Howdy is enabled at login"))
            else:
                img = '/images/img03.png'
                label.set_label(_("Howdy is disabled at login"))

        elif box == "howdy_addface":
            if state == "clicked":
                img = '/images/img04-white.png'
                label.set_label(_("Add new face model"))
            else:
                img = '/images/img04.png'
                label.set_label(_("Add new face model"))
        
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+img,
            width=100,
            height=100,
            preserve_aspect_ratio=True)
        
        icon.set_from_pixbuf(pixbuf)

    def on_button_face_clicked(self, EventBox, EventButton, icon_face, label_face):
        icon_face.set_name("clicked") 
        self.button_change(EventBox, icon_face, label_face)
        
        try:
            config = self.get_config()
            
            cfg_device = config["video"]["device_path"]
            addFace_dialog = AddFaceDialog(cfg_device)
            addFace_dialog.set_modal(True)
            response = addFace_dialog.run()
        
            if response == Gtk.ResponseType.ACCEPT:
                addFace_dialog.close_ok()
                #reload face list
                self.facesTreeView.set_model(self.get_face_list())
                
            addFace_dialog.destroy()
        except:
            print("Cannot read config.ini")
        
        icon_face.set_name("released") 
        self.button_change(EventBox, icon_face, label_face)

    def on_button_activate_clicked(self, EventBox, EventButton, icon_activate, label_activate):
        
        config = self.get_config()
        if config["core"]["disabled"] == "false":
            os.system("pkexec slimbookface-helper disable")
            label_activate.set_label(_('Enable face recognition'))
            icon_activate.set_name("released")
            self.button_change(EventBox, icon_activate, label_activate)
        
        else:
            os.system("pkexec slimbookface-helper enable")
            label_activate.set_label(_('Disable face recognition'))
            icon_activate.set_name("clicked")
            self.button_change(EventBox, icon_activate, label_activate)    

    def on_button_delete_face_clicked(self, button, tree_selection, treeview) :
        
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            faceid = model.get_value(tree_iter,0)
            facename = model.get_value(tree_iter, 1)
    
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/icono.png',
            width=90,
            height=90,
            preserve_aspect_ratio=True)
        icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
        icon_MsgDialog.show()

        dialog = Gtk.MessageDialog(message_type= Gtk.MessageType.QUESTION,
            image = icon_MsgDialog,
            buttons= Gtk.ButtonsType.YES_NO,
            text=(_('Alert!')))
        
        dialog.format_secondary_text((_('Are you sure that you want delete')) +' \"'+ facename + '\" '+ (_('\'s face?')))
        response = dialog.run()
        
        if response == Gtk.ResponseType.YES:
            print("destroying face {0}".format(faceid))
            os.system("pkexec slimbookface-helper remove {0}".format(faceid))
            model.remove(tree_iter)
        
        dialog.destroy()
    
    def on_device_changed(self, tree_selection, data):
        (model, path) = tree_selection.get_selected_rows()

        tree_iter = model.get_iter(path)
        camid = model.get_value(tree_iter, 0)
        device = model.get_value(tree_iter, 2)
        
        os.system("pkexec slimbookface-helper update-config video.device_path={0}{1}".format(V4L_PATH,device))
        
    
class AddFaceDialog(Gtk.Dialog):

    def __init__(self, device):
        Gtk.Dialog.__init__(self,
            (_('Slimbook Face: Add new face model for current user')),
            parent=None,
            modal=True,
            destroy_with_parent=True)
        self.device = device
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
        label = Gtk.Label(label=(_('Follow these steps to add new face model to Slimbook Face:')))
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 0, 1, xpadding=5, ypadding=5)
        # (1, 0)
        label = Gtk.Label(label='')
        label.set_markup('<b>'+ (_('Step 1:')) +' </b>'+ (_('Enter a name')))
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
        label.set_markup('<b>'+ (_('Step 2:')) +' </b> '+ (_('Preview your selected cam image')))
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 3, 4, xpadding=5, ypadding=5)
        # (4, 0)
        self.buttonShowCam = Gtk.Button(label=(_('Show webcam')))
        self.buttonShowCam.connect("clicked", self.show_cam)
        table.attach(self.buttonShowCam, 0, 2, 4, 5,
            xpadding=5,
            ypadding=5,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        # (5, 0)
        label = Gtk.Label(label='')
        label.set_markup('<b>'+ (_('Step 3:')) +' </b> '+ (_('Accept to capture your face (this can take 5-10 seconds')) +'\n')
        label.set_halign(Gtk.Align.START)
        table.attach(label, 0, 2, 5, 6, xpadding=5, ypadding=5)

        self.show_all()

    def show_cam(self, buttonShowCam):
        webcam_dialog = WebcamDialog(self.device)
        webcam_dialog.set_modal(True)
        response = webcam_dialog.run()
        
    def close_ok(self):
        face_name = self.entryFaceModelName.get_text()
        os.system("pkexec slimbookface-helper add {0}".format(face_name))

class WebcamDialog(Gtk.Dialog):

    def __init__(self,device):
        Gtk.Dialog.__init__(self,
            (_('Preview')),
            parent=None,
            modal=True,
            destroy_with_parent=True)
        
        self.device = device
        #self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.CLOSE)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(648, 488)
        box = Gtk.VBox()
        self.da = Gtk.DrawingArea()
        self.da.set_size_request(320,240)
        box.pack_start(self.da, True, True,0)
        self.da.connect("draw",self.expose)
        self.get_content_area().add(box)
        
        self.connect("destroy",self.on_destroy)
        self.show_all()
        
        GObject.timeout_add(60,self.update)
        
        self.vid = cv2.VideoCapture(device)

    def on_destroy(self,data):
        self.vid.release()
        
    def update(self):
        self.da.queue_draw()
        return True
    
    def expose(self,area,context):
        #context.scale(area.get_allocated_width(), area.get_allocated_height())
        ret, frame = self.vid.read()
        if ret:
            #print(frame.shape)
            h,w,bpp = frame.shape
            self.da.set_size_request(w,h)
            #frame = numpy.expand_dims(frame,axis=-1)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
            data = bytearray(frame.tobytes())
            
            #print(len(data))
            #data = numpy.ndarray(frame.shape, dtype=numpy.uint32)
            #numpy.copyto(data,raw,"unsafe")
            surface = cairo.ImageSurface.create_for_data (data,cairo.FORMAT_ARGB32 ,w,h)
            context.set_source_surface(surface)
            context.paint()


if __name__ == "__main__":
    if __file__.startswith('/usr') or os.getcwd().startswith('/usr'):
        sys.path.insert(1, '/usr/share/slimbookface')
    else:
        sys.path.insert(1, os.path.normpath(
            os.path.join(os.getcwd(), '../src')))

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
