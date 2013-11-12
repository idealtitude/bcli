#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
#import re

import wx
import wx.combo

from bclilib import fileshandle as fh
from bclilib import filesbrowser as fb
from bclilib import sendtoblender as s2b


class BCli(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        ### Quelques variables ###

        ###############################
        ### Eléments de l'interface ###
        ###############################

        # Choix de l'exécutable blender
        binlist = []
        f = open(fh.getPath('/datas/executables.txt'))
        for l in f:
            binlist.append(str(l.strip()))
        f.close()

        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (24,24))
        bintest_bmp = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, (24,24))
        self.executable_combobox = wx.ComboBox(self, -1, choices=binlist, style=wx.CB_DROPDOWN)
        self.browse_exec_button = wx.BitmapButton(self, -1, open_bmp)
        self.bintest_button = wx.BitmapButton(self, -1, bintest_bmp)
        self.sizer_exec_staticbox = wx.StaticBox(self, -1, "Exécutable")

        # Choix du fichier source
        self.source_textctrl = wx.TextCtrl(self, -1, "")
        self.browse_source_button = wx.BitmapButton(self, -1, open_bmp)
        self.sizer_source_staticbox = wx.StaticBox(self, -1, "Fichier source")

        # Choix du fichier de destination
        self.destination_textctrl = wx.TextCtrl(self, -1, "")
        self.browse_destination_button = wx.BitmapButton(self, -1, open_bmp)
        self.sizer_destination_staticbox = wx.StaticBox(self, -1, "Fichier de destination")

        # Choix des frames
        self.start_frames_label = wx.StaticText(self, -1, "Début")
        self.start_frames_textctrl = wx.TextCtrl(self, -1, "1")
        self.start_frames_spinctrl = wx.SpinCtrl(self, -1, "1", min=0, max=10000)
        self.end_frames_label = wx.StaticText(self, -1, "Fin")
        self.end_frames_textctrl = wx.TextCtrl(self, -1, "")
        self.sizer_frames_staticbox = wx.StaticBox(self, -1, "Frames")
        self.end_frames_spinctrl = wx.SpinCtrl(self, -1, "", min=0, max=10000)

        # Choix du format
        self.format_combobox = wx.ComboBox(self, -1, choices=["PNG", "TGA", "IRIS", "JPEG", "MOVIE", "IRIZ", "RAWTGA", "AVIRAW", "AVIJPEG", "BMP", "FRAMESERVE"], style=wx.CB_DROPDOWN)
        self.format_checkbox = wx.CheckBox(self, -1, "Extension")
        self.sizer_format_staticbox = wx.StaticBox(self, -1, "Format")

        # Validation du formulaire
        self.validation_hr = wx.StaticLine(self, -1)
        self.exit_button = wx.Button(self, -1, "Quitter")
        self.reset_button = wx.Button(self, -1, "Réinitialiser")
        self.valid_button = wx.Button(self, -1, "Valider")
        self.statusbar = self.CreateStatusBar(1, 0)

        ### Fin éléments interface ###

        ##########################################
        ### Bindings des éléments aux méthodes ###
        ##########################################

        # Boutons de navigation fichiers
        self.Bind(wx.EVT_BUTTON, lambda evt, name=self.browse_exec_button, field=self.executable_combobox, ref=0:self.openFileBrowser(evt, name, field, ref), self.browse_exec_button)
        self.Bind(wx.EVT_BUTTON, lambda evt, name=self.browse_source_button, field=self.source_textctrl, ref=1: self.openFileBrowser(evt, name, field, ref), self.browse_source_button)
        self.Bind(wx.EVT_BUTTON, lambda evt, name=self.browse_destination_button, field=self.destination_textctrl, ref=2: self.openFileBrowser(evt, name, field, ref), self.browse_destination_button)

        #self.browse_exec_button
        self.Bind(wx.EVT_BUTTON, self.testBin, self.bintest_button)

        # Spin controls pour les frames
        self.Bind(wx.EVT_SPINCTRL, self.spinStartFrame, self.start_frames_spinctrl)
        self.Bind(wx.EVT_SPINCTRL, self.spinEndFrame, self.end_frames_spinctrl)

        # Boutons de validation
        self.Bind(wx.EVT_BUTTON, self.closeApp, self.exit_button)
        self.Bind(wx.EVT_BUTTON, self.resetApp, self.reset_button)
        self.Bind(wx.EVT_BUTTON, self.executeRender, self.valid_button)

        ### Fin bindings ###

        self.__set_properties()
        self.__do_layout()

    ### Properties et layout ###
    def __set_properties(self):
        self.SetTitle("BCli")
        self.statusbar.SetStatusWidths([-1])
        # statusbar fields
        statusbar_fields = ["bcli_main_statusbar"]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        self.executable_combobox.SetMinSize((500, 33))
        self.executable_combobox.SetToolTipString("Défintion de l'exécutable blender")
        self.bintest_button.SetToolTipString("Tester l'exécutable sélctionné")
        self.source_textctrl.SetToolTipString("Définition du fichier source blender")
        self.destination_textctrl.SetToolTipString("Définition du fichier source de blender")
        self.start_frames_textctrl.SetMinSize((100, 31))
        self.end_frames_textctrl.SetMinSize((100, 31))
        self.start_frames_spinctrl.SetMinSize((50, 31))
        self.end_frames_spinctrl.SetMinSize((50, 31))
        self.executable_combobox.SetSelection(0)
        self.format_combobox.SetSelection(0)
        self.format_checkbox.SetValue(1)
        self.valid_button.SetDefault()

    def __do_layout(self):
        ### Layout de l'interface ###

        # Conteneur principal
        sizer_main = wx.BoxSizer(wx.VERTICAL)

        sizer_validation = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_format_staticbox.Lower()
        sizer_format = wx.StaticBoxSizer(self.sizer_format_staticbox, wx.HORIZONTAL)
        self.sizer_frames_staticbox.Lower()
        sizer_frames = wx.StaticBoxSizer(self.sizer_frames_staticbox, wx.HORIZONTAL)
        self.sizer_destination_staticbox.Lower()
        sizer_destination = wx.StaticBoxSizer(self.sizer_destination_staticbox, wx.HORIZONTAL)
        self.sizer_source_staticbox.Lower()
        sizer_source = wx.StaticBoxSizer(self.sizer_source_staticbox, wx.HORIZONTAL)
        self.sizer_exec_staticbox.Lower()
        sizer_exec = wx.StaticBoxSizer(self.sizer_exec_staticbox, wx.HORIZONTAL)
        sizer_exec.Add(self.executable_combobox, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_exec.Add(self.browse_exec_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_exec.Add(self.bintest_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_exec, 0, wx.ALL|wx.EXPAND, 5)
        sizer_source.Add(self.source_textctrl, 1, wx.RIGHT|wx.EXPAND|wx.ADJUST_MINSIZE, 4)
        sizer_source.Add(self.browse_source_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_source, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer_destination.Add(self.destination_textctrl, 1, wx.RIGHT|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_destination.Add(self.browse_destination_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_destination, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer_frames.Add(self.start_frames_label, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_frames.Add(self.start_frames_textctrl, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_frames.Add(self.start_frames_spinctrl, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 20)
        sizer_frames.Add(self.end_frames_label, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_frames.Add(self.end_frames_textctrl, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_frames.Add(self.end_frames_spinctrl, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_frames, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer_format.Add(self.format_combobox, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 20)
        sizer_format.Add(self.format_checkbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_format, 0, wx.ALL|wx.EXPAND, 5)
        sizer_main.Add(self.validation_hr, 0, wx.ALL|wx.EXPAND, 10)
        sizer_validation.Add(self.exit_button, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_validation.Add(self.reset_button, 1, wx.LEFT|wx.RIGHT|wx.EXPAND|wx.ADJUST_MINSIZE, 10)
        sizer_validation.Add(self.valid_button, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_validation, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        self.SetSizer(sizer_main)
        sizer_main.Fit(self)
        self.Layout()
        self.Centre()

    ### Fin properties and layout

    ############################
    ### Méthodes de la class ###
    ############################

    # Ouverture du navigateur de fichiers
    def openFileBrowser(self, e, name, field, ref):
        fd = fb.BrowseFiles(self, name, field, ref)

    # Test de l'exécutable renseigné dans le formulaire
    def testBin(self, e):
        self.bintest_button.Enable(False)
        binpath = self.executable_combobox.GetValue()

        dlg = wx.MessageDialog(self, 'Pas encore implémenté...', 'Succès', wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        self.bintest_button.Enable(True)

    # Spin controls pour les frames
    def spinStartFrame(self, e):
        value = self.start_frames_spinctrl.GetValue()
        self.start_frames_textctrl.SetValue(str(value))
    def spinEndFrame(self, event):
        value = self.end_frames_spinctrl.GetValue()
        self.end_frames_textctrl.SetValue(str(value))

    # Fermeture de l'application
    def closeApp(self, e):
        self.Close()

    def resetApp(self, e):
        #self.Close()
        print("Pas encore implémenté...")
        pass

    # Valider le formulaire et exécuter la commande
    def executeRender(self, e):
        dataCollect = {"bin": self.executable_combobox.GetValue(),
                         "src": self.source_textctrl.GetValue(),
                         "out": self.destination_textctrl.GetValue(),
                         "start": self.start_frames_textctrl.GetValue(),
                         "end": self.end_frames_textctrl.GetValue(),
                         "type": self.format_combobox.GetValue(),
                         "addext": self.format_checkbox.GetValue()}

        gorender = s2b.BCliRender(self, dataCollect)


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    bcli_main = BCli(None, -1, "")
    app.SetTopWindow(bcli_main)
    bcli_main.Show()
    app.MainLoop()
