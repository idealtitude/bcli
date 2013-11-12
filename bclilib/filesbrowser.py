#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import basename, dirname
import wx


class BrowseFiles(wx.Frame):
    def __init__(self, parent, name, field, ref):
        wx.Frame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.prnt = parent
        self.name = name
        self.name.Enable(False)
        self.field = field

        self.ref = ref
        title = ""
        if self.ref == 0:
            title = "BcliFileBrowser ~ sélection de l'exécutable"
        elif self.ref == 1:
            title = "BcliFileBrowser ~ sélection de la source"
        elif self.ref == 2:
            title = "BcliFileBrowser ~ sélection de la destination"

        self.title = title

        #self.prnt.exit_but.Enable(False)

        self.path = ""

        self.path_dirctrl = None
        if self.ref == 0:
            self.path_dirctrl = wx.GenericDirCtrl(self, -1, size=(500,300), style=0)
        elif self.ref == 1:
            self.path_dirctrl = wx.GenericDirCtrl(self, -1, size=(500,300), style=wx.DIRCTRL_SHOW_FILTERS,filter="Blend files (*.blend)|*.blend")
        elif self.ref == 2:
            self.path_dirctrl = wx.GenericDirCtrl(self, -1, size=(500,300), style=wx.DIRCTRL_DIR_ONLY)

        self.static_line_1 = wx.StaticLine(self, -1)
        self.exit_but = wx.Button(self, -1, "Quitter")
        self.open_but = wx.Button(self, -1, "Ouvrir")
        self.browser_statusbar = self.CreateStatusBar(1, 0)

        self.__set_properties()
        self.__do_layout()

        self.path_dirctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSel)
        self.Bind(wx.EVT_BUTTON, self.closeBrowser, self.exit_but)
        self.Bind(wx.EVT_BUTTON, self.openFile, self.open_but)

    def __set_properties(self):
        self.SetTitle(self.title)
        #self.path_dirctrl.SetMinSize((380, 190))
        self.open_but.Enable(False)
        self.browser_statusbar.SetStatusWidths([-1])
        # statusbar fields
        browser_statusbar_fields = ["Navigateur de fichier"]
        for i in range(len(browser_statusbar_fields)):
            self.browser_statusbar.SetStatusText(browser_statusbar_fields[i], i)

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.path_dirctrl, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(self.static_line_1, 0, wx.ALL|wx.EXPAND, 5)
        sizer_3.Add(self.exit_but, 1, wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 5)
        sizer_3.Add(self.open_but, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(sizer_3, 0, wx.ALL|wx.EXPAND, 5)
        sizer_1.Add(sizer_2, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()

        self.Show()

    def closeBrowser(self, e):
        self.Close()

    def OnClose(self, e):
        self.name.Enable(True)
        e.Skip()

    def OnSel(self, e):
        if self.ref == 2:
            self.path = self.path_dirctrl.GetPath()
            self.open_but.Enable(True)
        else:
            self.path = self.path_dirctrl.GetFilePath()
            if self.path != "":
                self.open_but.Enable(True)
            else:
                self.open_but.Enable(False)

        self.browser_statusbar.SetStatusText(self.path)

    def openFile(self, e):
        if self.path != "":
            if self.ref == 2:
                dlg = wx.TextEntryDialog(self, 'Saisis un nom pour ce fichier', 'Nom du fichier', 'BCli')
                dlg.SetValue("")
                imagename = ""
                if dlg.ShowModal() == wx.ID_OK:
                    imagename = dlg.GetValue()
                dlg.Destroy()
                if imagename != "":
                    self.path = self.path + "/" + imagename
                else:
                    self.path = self.path + "/rendu"

            if self.ref == 1:
                dn = dirname(self.path)
                bn = basename(self.path)
                bn = bn.replace('.blend', '')
                self.prnt.destination_textctrl.SetValue("%s/%s" % (dn, bn))

            self.field.SetValue(self.path)
            self.Close()
        else:
            dlg = wx.MessageDialog(self, 'Aucun exécutable n\'a été sélectionné...', 'Message', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

