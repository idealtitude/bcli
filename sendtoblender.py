#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade HG on Sat Oct 19 21:20:46 2013

import sys
import os
import time
from subprocess import Popen, PIPE, STDOUT
import shlex
import threading

import wx

# begin wxGlade: extracode
# end wxGlade


class ExecCmd:
	def __init__(self, prnt, strcmd):
		self.strcmd = strcmd
		self.prnt = prnt
		self.progr = True
		
	def progressbar(self):
		x = 1
		y = 0
		u = u"\u25AE"
		def showprogress(x, y):
			z = u * x
			strsb = "%ss" % y
			self.prnt.frame_1_statusbar.SetStatusText("%ss" % y, 0)
			self.prnt.frame_1_statusbar.SetStatusText(z, 1)
			if x == 0:
				self.prnt.frame_1_statusbar.SetStatusText('%ss' % y, 0)
			
		while self.progr:       
			if x > 4:
				x = 0
			showprogress(x, y)
			x = x + 1
			y = y + 0.25
			time.sleep(0.25)
			
	def __output_stdoe(self, i):
		#tco = self.prnt.output_textctrl
		tcs = self.prnt.text_ctrl_2
		e = tcs.GetLastPosition()
		l = len(i)
		s = e - l
		tcs.SetStyle(s, e, wx.TextAttr('#FF3232', wx.NullColour))
	
	def startrender(self):
		
		progbar = threading.Thread(target=self.progressbar)
		progbar.start()
		
		try:
			start_time = time.time()
			cmd = Popen(shlex.split(self.strcmd), stdout=PIPE, stderr=PIPE)
			oe = cmd.communicate()
			chknberr = 0
			
			while True:
				ot = oe[0]
				er = oe[1]
				if len(str(ot)) > 0:
					self.prnt.text_ctrl_2.AppendText(str(ot))
				if len(str(er)) > 0:
					self.prnt.text_ctrl_2.AppendText("\n%s" % str(er))
					self.__output_stdoe(str(er))
					#chknberr += 1
					
				if cmd.poll() != None:
					self.progr = False
					elapsed_time = time.time() - start_time
					self.prnt.frame_1_statusbar.SetStatusText("%ss" % str(elapsed_time), 0)
					break
		except IOError as e:
			m = "I/O error({0}): {1}".format(e.errno, e.strerror)
			self.prnt.text_ctrl_2.SetText(m)


class BCliRender(wx.Frame):
	def __init__(self, parent, datas):
		# begin wxGlade: BcliFileBrowser.__init__
		#kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, parent)
		
		self.datas = datas
		self.strcmd = None
		
		self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
		self.sizer_3_staticbox = wx.StaticBox(self, -1, "Commande finale")
		self.button_1 = wx.Button(self, -1, "Render it")
		self.button_2 = wx.Button(self, -1, "Annuler")
		self.label_1 = wx.StaticText(self, -1, "Mémoriser l'exécutable")
		self.checkbox_1 = wx.CheckBox(self, -1, "")
		self.sizer_4_staticbox = wx.StaticBox(self, -1, "Validation")
		self.text_ctrl_2 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
		self.sizer_5_staticbox = wx.StaticBox(self, -1, "Output")
		self.frame_1_statusbar = self.CreateStatusBar(2, 0)

		self.__set_properties()
		self.__do_layout()
		self.__fill_cmd_input()
		
		self.Show()
		
		self.Bind(wx.EVT_TEXT_ENTER, self.editcmd, self.text_ctrl_1)
		
		self.Bind(wx.EVT_BUTTON, self.mkproc, self.button_1)
		self.Bind(wx.EVT_BUTTON, self.quitwin, self.button_2)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: BCliRender.__set_properties
		self.SetTitle("BCli Render")
		self.SetSize((800, 600))
		self.frame_1_statusbar.SetStatusWidths([-1])
		# statusbar fields
		frame_1_statusbar_fields = ["frame_1_statusbar"]
		for i in range(len(frame_1_statusbar_fields)):
			self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: BCliRender.__do_layout
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_2 = wx.BoxSizer(wx.VERTICAL)
		self.sizer_5_staticbox.Lower()
		sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
		self.sizer_4_staticbox.Lower()
		sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
		self.sizer_3_staticbox.Lower()
		sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
		sizer_3.Add(self.text_ctrl_1, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
		sizer_2.Add(sizer_3, 0, wx.BOTTOM|wx.EXPAND, 5)
		sizer_4.Add(self.button_1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
		sizer_4.Add(self.button_2, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
		sizer_4.Add(self.label_1, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
		sizer_4.Add(self.checkbox_1, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
		sizer_2.Add(sizer_4, 0, wx.BOTTOM|wx.EXPAND, 5)
		sizer_5.Add(self.text_ctrl_2, 1, wx.ALL|wx.EXPAND, 5)
		sizer_2.Add(sizer_5, 1, wx.EXPAND, 5)
		sizer_1.Add(sizer_2, 1, wx.ALL|wx.EXPAND, 5)
		self.SetSizer(sizer_1)
		self.Layout()
		self.Centre()
		# end wxGlade
		
	def __fill_cmd_input(self):
		addext = 0
		if self.datas["addext"] is True:
			addext = 1
			
		if self.datas["end"] == "":
			self.strcmd = "%s -b %s -o %s -F %s -x %s -f %s" % (str(self.datas["bin"]), str(self.datas["src"]), str(self.datas["out"]), str(self.datas["type"]), addext, str(self.datas["start"]))
			self.text_ctrl_1.SetValue(self.strcmd)
		else:
			#video render
			pass
			
	def editcmd(self, e):
		dlg = wx.MessageDialog(self, 'Souhaites-tu utiliser cette modification de la la commande?', 'Message', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
		if dlg.ShowModal() == wx.ID_OK:
			self.strcmd = self.text_ctrl_1.GetValue()
		dlg.Destroy()
	
	def mkproc(self, e):
		if self.checkbox_1.GetValue() is True:
			f = open('executables.txt', 'r')
			x = False
			for l in f:
				if l.strip('\n') == str(self.datas["bin"]):
					x = True
					break
			f.close()
			if x is True:
				dlg = wx.MessageDialog(self, 'Cet exécutable est déjà dans la liste', 'Message', wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
			else:
				nf = open('executables.txt', 'a')
				nf.write(str(self.datas["bin"]))
				nf.close()
				
		newrender = ExecCmd(self, self.strcmd)
		newrender.startrender()
		
	def quitwin(self, e):
		self.Close()

