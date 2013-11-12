#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

import wx

class checkBin:
    def __init__(self, parent, blenderbin):
        self.prnt = parent
        self.bbin = blenderbin

        self._checkBin()

    def _checkBin(self):
        cmd = ['which', self.bbin]
        try:
            chk = subprocess.call(cmd)
            print(str(chk))
            #wx.MessageDialog(self.prnt, 'Le test a réussi!', 'Succès', wx.OK|wx.ICON_INFORMATION)
        except OSError as err:
            #wx.MessageDialog(self.prnt, "Le test a échoué! Infos erreur:\n\nNuméro: %s\nFichier: %s\nMessage %s" % (err.errno, err.filename, err.strerror), 'Erreur', wx.OK|wx.ICON_ERROR)
            print("nok")

