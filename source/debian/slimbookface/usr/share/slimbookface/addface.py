#!/usr/bin/env python3

import sys, os
import gi
try:
	import cv2
except:
	print('')
import gettext, locale
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, GdkPixbuf

entorno_usu = locale.getlocale()[0]
if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0:
	idiomas = [entorno_usu]
else:
	idiomas = ['en']

print('Language: ', entorno_usu)

t = gettext.translation('addface',
						'/usr/share/slimbookface/locale',
						languages=idiomas,
						fallback=True,)

_ = t.gettext

class AddFaceDialog(Gtk.Dialog):
	def __init__(self):
		Gtk.Dialog.__init__(self,
			(_('straddfacetitle')),
			None,
			Gtk.DialogFlags.MODAL |
			Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_default_size(400, 250)
		self.set_resizable(False)
		self.connect("close", self.close_ok)
		vbox = Gtk.VBox(spacing=5)
		self.get_content_area().add(vbox)
		table = Gtk.Table(3, 3, False)
		vbox.add(table)
		# (0, 0)
		label = Gtk.Label((_('strsteps1')))
		label.set_alignment(0, 0.5)
		table.attach(label, 0, 2, 0, 1, xpadding=5, ypadding=5)
		# (1, 0)
		label = Gtk.Label('')
		label.set_markup('<b>'+ (_('strsteps2')) +' </b>'+ (_('strsteps3')))
		label.set_alignment(0, 0.5)
		table.attach(label, 0, 2, 1, 2, xpadding=5, ypadding=5)
		'''# (0, 0)
		label = Gtk.Label(_('strfacemodelname'))
		label.set_justify(Gtk.Justification.CENTER)
		table.attach(label, 0, 1, 1, 2, xpadding=5, ypadding=5)'''
		# (2, 0)
		self.entryFaceModelName = Gtk.Entry()
		table.attach(self.entryFaceModelName, 0, 2, 2, 3,
			xpadding=5,
			ypadding=5,
			xoptions=Gtk.AttachOptions.FILL,
			yoptions=Gtk.AttachOptions.SHRINK)
		# (3, 0)
		label = Gtk.Label('')
		label.set_markup('<b>'+ (_('strsteps4')) +' </b> '+ (_('strsteps5')))
		label.set_alignment(0, 0.5)
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
		label = Gtk.Label('')
		label.set_markup('<b>'+ (_('strsteps6')) +' </b> '+ (_('strsteps7')) +'\n')
		label.set_alignment(0, 0.5)
		table.attach(label, 0, 2, 5, 6, xpadding=5, ypadding=5)

		self.show_all()

	def show_cam(self, buttonShowCam):
		'''cam = cv2.VideoCapture(0)
		cv2.namedWindow('Slimbook Face: Webcam', cv2.WINDOW_NORMAL)
		mirror = True

		while True:
			ret_val, img = cam.read()
			if mirror:
				img = cv2.flip(img, 1)
			cv2.imshow('Slimbook Face: Webcam', img)
			if cv2.waitKey(1) == 27:
				break
			if cv2.getWindowProperty('Slimbook Face: Webcam',cv2.WND_PROP_VISIBLE) < 1:
				break
		cv2.destroyAllWindows()'''
		cam = cv2.VideoCapture(0)
		leido, frame = cam.read()


		if leido == True:
			path = '/tmp/'
			cv2.imwrite(os.path.join(path, 'image.jpeg'), frame)
		cam.release()

		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename='/tmp/image.jpeg',
			width=400,
			height=400,
			preserve_aspect_ratio=True)
		captura = Gtk.Image.new_from_pixbuf(pixbuf)
		captura.set_alignment(0.5, 0)
		dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK)
		dialog.move(0, 0)
		dialog.get_content_area().add(captura)
		dialog.set_image(captura)
		dialog.show_all()
		dialog.run()
		dialog.destroy()

	def close_ok(self):
		FaceModelName = self.entryFaceModelName.get_text()
		FaceModelName = '\"'+ FaceModelName + '\"'
		if os.system('pkexec python3 /usr/share/slimbookface/slimbookface-howdy.py add '+ FaceModelName + ' | grep -i "added a new model"') == 0:
			os.system("notify-send 'Slimbook Face' '"+ (_("stralertaddface")) +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")
		else:
			os.system("notify-send 'Slimbook Face' '"+ (_("stralertaddface2")) +"' -i '" + '/usr/share/slimbookface/images/icono.png' + "'")

if __name__ == "__main__":
	cm = AddFaceDialog()
	if cm.run() == Gtk.ResponseType.ACCEPT:
		cm.close_ok()
	cm.hide()
	cm.destroy()
	exit(0)