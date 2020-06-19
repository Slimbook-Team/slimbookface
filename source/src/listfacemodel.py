#!/usr/bin/env python3

import sys, os
import gi
import json
import gettext, locale
import subprocess
import getpass
import time
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, GdkPixbuf
from os.path import expanduser

user = getpass.getuser()

class ListFaceModel(Gtk.Dialog):
	def __init__(self):
		Gtk.Dialog.__init__(self,
			'List of face models',
			None,
			Gtk.DialogFlags.MODAL |
			Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_default_size(400, 250)
		self.set_resizable(False)
		vbox = Gtk.VBox(spacing=5)
		self.get_content_area().add(vbox)
		table = Gtk.Table(3, 3, False)
		vbox.add(table)
		# (0, 0)
		label = Gtk.Label('')
		label.set_alignment(0, 0.5)
		table.attach(label, 0, 1, 0, 1, xpadding=5, ypadding=5)
        # (1, 0)
		label = Gtk.Label('')
		label.set_markup('<b>Face model profile</b>')
		label.set_alignment(0, 0.5)
		table.attach(label, 0, 1, 1, 2, xpadding=5, ypadding=5)
		# (1, 1)
		label = Gtk.Label('')
		label.set_markup('<b>Registration date</b>')
		label.set_alignment(0, 0.5)
		table.attach(label, 1, 2, 1, 2, xpadding=5, ypadding=5)
		# (1, 2)
		label = Gtk.Label('')
		label.set_markup('<b>Actions</b>')
		label.set_alignment(0, 0.5)
		table.attach(label, 2, 3, 1, 2, xpadding=5, ypadding=5)

		models_path = '/lib/security/howdy/models/'+ user +'.dat'
		try:
			encodings = json.load(open(models_path))
		except FileNotFoundError:
			print("No face model known for the user " + user + ", please run:")
		
		pos1 = 2
		pos2 = 3

		for enc in encodings:
			date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(enc["time"]))
			strface = enc["label"]
			print(strface +' '+ date)
			pos1 = pos1 + 1
			pos2 = pos2 + 1

		self.show_all()

	def close_ok(self):
		os.system('echo kk')

if __name__ == "__main__":
	cm = ListFaceModel()
	if cm.run() == Gtk.ResponseType.ACCEPT:
		cm.close_ok()
	cm.hide()
	cm.destroy()
	exit(0)