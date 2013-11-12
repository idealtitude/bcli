#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re
import subprocess

import wx
import wx.lib.imagebrowser as ib

from fileshandle import getPath as gpth


class BCliRender(wx.Frame):
    def __init__(self, parent, datas):
        wx.Frame.__init__(self, parent)

        # Quelques variables
        self.datas = datas
        self.strcmd = None
        self.pid = None

        self.rendernberrors = 0
        self.rendererrors = []
        self.ptnframes = re.compile(r'^[1-9]+$')

        self.starttime = 0

        ### INTERFACE ###

        stopprocess_bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (20,20))
        copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, (20,20))
        reset_bmp = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (20,20))
        self.final_cmd = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.finalcmd_sizer = wx.StaticBox(self, -1, "Commande finale")
        self.copycmd_button = wx.BitmapButton(self, -1, copy_bmp)
        self.resetcmd_button = wx.BitmapButton(self, -1, reset_bmp)
        self.renderit_button = wx.Button(self, -1, "Render it")
        self.stopprocess_button = wx.BitmapButton(self, -1, stopprocess_bmp)
        self.cancel_button = wx.Button(self, -1, "Annuler")
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (20,20))
        self.openfolder = wx.BitmapButton(self, -1, open_bmp)
        self.saveexec_label = wx.StaticText(self, -1, "Mémoriser l'exécutable")
        self.saveexec_checkbox = wx.CheckBox(self, -1, "")
        self.validation_staticbox = wx.StaticBox(self, -1, "Validation")
        self.output_textctrl = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.output_staticbox = wx.StaticBox(self, -1, "Output")
        self.sendtoblender_statusbar = self.CreateStatusBar(2, 0)

        self.__set_properties()
        self.__do_layout()
        self.__fill_cmd_input()

        self.Show()

        self.process = None
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

        self.Bind(wx.EVT_TEXT_ENTER, self.editCmd, self.final_cmd)
        self.editcmdcheck = False
        self.Bind(wx.EVT_TEXT, self.editCmdCheck, self.final_cmd)

        self.Bind(wx.EVT_BUTTON, self.resetCmd, self.resetcmd_button)
        self.Bind(wx.EVT_BUTTON, self.copyCmd, self.copycmd_button)

        self.Bind(wx.EVT_BUTTON, self.renderIt, self.renderit_button)
        self.Bind(wx.EVT_BUTTON, self.stopProc, self.stopprocess_button)
        self.Bind(wx.EVT_BUTTON, self.quitWin, self.cancel_button)
        self.Bind(wx.EVT_BUTTON, self.openImgDir, self.openfolder)

        ### FIN INTERFACE ###

    def __set_properties(self):
        self.SetTitle("BCli Render")
        self.SetSize((800, 600))
        self.renderit_button.Enable(False)
        self.stopprocess_button.Enable(False)
        self.resetcmd_button.Enable(False)
        self.openfolder.Enable(False)
        self.sendtoblender_statusbar.SetStatusWidths([-1, 300])
        self.openfolder.SetToolTipString("Ouvrir le dossier de l'image")
        self.copycmd_button.SetToolTipString("Copier la commande")
        self.resetcmd_button.SetToolTipString("Réinitialiser à la dernière sauvegarde de la commande")
        self.stopprocess_button.SetToolTipString("Arrêter le rendu")

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        self.output_staticbox.Lower()
        sizer_5 = wx.StaticBoxSizer(self.output_staticbox, wx.HORIZONTAL)
        self.validation_staticbox.Lower()
        sizer_4 = wx.StaticBoxSizer(self.validation_staticbox, wx.HORIZONTAL)
        self.finalcmd_sizer.Lower()
        sizer_3 = wx.StaticBoxSizer(self.finalcmd_sizer, wx.HORIZONTAL)
        sizer_3.Add(self.final_cmd, 1, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_3.Add(self.resetcmd_button, 0, wx.TOP|wx.BOTTOM|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_3.Add(self.copycmd_button, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(sizer_3, 0, wx.BOTTOM|wx.EXPAND, 5)
        sizer_4.Add(self.renderit_button, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.stopprocess_button, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.cancel_button, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.saveexec_label, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.saveexec_checkbox, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.openfolder, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(sizer_4, 0, wx.BOTTOM|wx.EXPAND, 5)
        sizer_5.Add(self.output_textctrl, 1, wx.ALL|wx.EXPAND, 5)
        sizer_2.Add(sizer_5, 1, wx.EXPAND, 5)
        sizer_1.Add(sizer_2, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()

    def __output_stdoe(self, errorstring):
        # Cette méthode sert à colorier en rouge les messages d'erreur renvoyer par le subprocess
        tcs = self.output_textctrl
        e = tcs.GetLastPosition()
        l = len(errorstring)
        s = e - l
        tcs.SetStyle(s, e, wx.TextAttr('#FF3232', wx.NullColour))

    def __del__(self):
        # Nettoyage lors de la fermeture
        if self.process is not None:
            self.process.Detach()
            self.process.CloseOutput()
            self.process = None

    def resetCmd(self, e):
        self.final_cmd.SetValue(self.strcmd)
        self.editcmdcheck = False
        self.resetcmd_button.Enable(False)

    def clearstatusbaraftercopy(self):
        time.sleep(2)
        self.sendtoblender_statusbar.SetStatusText(self.strcmd, 0)

    def copyCmd(self, e):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.strcmd))
            wx.TheClipboard.Close()
            self.sendtoblender_statusbar.SetStatusText("Presse-papier: %s" % self.strcmd, 0)
            wx.CallAfter(self.clearstatusbaraftercopy)

    def runRendering(self):
        # On lance l'exécution de la commande finale
        self.starttime = time.time()
        self.renderit_button.Enable(False)
        self.stopprocess_button.Enable(True)
        self.process = wx.Process(self)
        self.process.Redirect();
        self.pid = wx.Execute(self.strcmd, wx.EXEC_ASYNC, self.process)

    def OnIdle(self, e):
        # l'exécution de la commande finale a été lancé, le wxprocess est en cours
        # On récupère au fur et à mesure la sortie et on l'affiche dans le champ output_textctrl de l'interface
        # On colorie en rouge si c'est un message d'erreur
        if self.process is not None:
            stream = self.process.GetInputStream()

            if stream.CanRead():
                text = stream.read()
                self.output_textctrl.AppendText(text)

            estream = self.process.GetErrorStream()

            if estream.CanRead():
                self.rendernberrors += 1
                etext = estream.read()
                self.output_textctrl.AppendText(etext)
                self.__output_stdoe(str(etext))

                self.rendererrors.append(etext)

    def OnProcessEnded(self, e):
        # L'exécution de la commande finale s'est terminée
        endtime = time.time()
        stream = self.process.GetInputStream()

        if stream.CanRead():
            text = stream.read()
            self.output_textctrl.AppendText(text)

        estream = self.process.GetErrorStream()

        if estream.CanRead():
            #self.rendernberrors += 1
            etext = estream.read()
            self.output_textctrl.AppendText(etext)
            self.__output_stdoe(str(etext))

            self.rendererrors.append(etext)

        self.process.Destroy()
        self.process = None
        self.renderit_button.Enable(True)
        self.stopprocess_button.Enable(False)
        elapsedtime = endtime - self.starttime
        self.sendtoblender_statusbar.SetStatusText("Durée: %s, Erreur(s): %s" % (elapsedtime, self.rendernberrors), 1)

        for i in self.rendererrors:
            self.output_textctrl.AppendText(i)

    def __fill_cmd_input(self):
        # On remplie le champ commande finale avec les variables déclarées lors du __init__ (reçues lors de l'instanciation de l'objet dans bcli.py)

        # L'utilisateur a-t-il renseigné le champ extensions
        addext = 0
        if self.datas["addext"] is True:
            addext = 1

        # On vérifie ce que contiennent les variables start et end des frames
        # On teste d'abord si c'est des nombres
        checkstartframes = re.match(self.ptnframes, self.datas['start'])
        if checkstartframes > 0:
            # La variable end est-elle renseigné, si non -> image, si oui -> anim
            if self.datas['end'] == "" or self.datas['end'] == "0":
                # formatage de la commande rendu image
                self.strcmd = "%s -b %s -o %s -F %s -x %s -f %s" % (str(self.datas["bin"]), str(self.datas["src"]), str(self.datas["out"]), str(self.datas["type"]), addext, str(self.datas["start"]))
            else:
                checkendframes = re.match(self.ptnframes, self.datas['end'])
                if checkstartframes > 0:
                    # formatage de la commande rendu animation
                    self.strcmd = "%s -b %s -o %s -F %s -x %s -s %s -e %s -a" % (str(self.datas["bin"]), str(self.datas["src"]), str(self.datas["out"]), str(self.datas["type"]), addext, str(self.datas["start"]), str(self.datas["end"]))

            # On remplie le champ final_cmd (commande finale) avec la chaine de la commande
            self.final_cmd.SetValue(self.strcmd)
            self.sendtoblender_statusbar.SetStatusText(self.strcmd, 0)
            self.renderit_button.Enable(True)
        else:
            # Quelque chose n'est pas normal avec les frames... On en informe l'utilisateur et on ne remplie pas le champ commande finale
            dlg = wx.MessageDialog(self, 'La définition des frames ne semble pas valide!', 'Error', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.sendtoblender_statusbar.SetStatusText("Impossible de formater la commande...", 0)

        if self.datas["out"] != "":
            self.openfolder.Enable(True)

    def editCmd(self, e):
        # L'utilsateur a appuyé sur Entrée alors qu'il était dans le champ commande finale
        # Au cas où il amodifié la commande on lui demande s'il veut utiliser cette nouvelle version...
        # Sinon on ne touche pas à la variable command finale
        dlg = wx.MessageDialog(self, 'Souhaites-tu utiliser cette modification de la commande?', 'Message', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            self.strcmd = self.final_cmd.GetValue()
            self.sendtoblender_statusbar.SetStatusText(self.strcmd, 0)
            self.resetcmd_button.Enable(False)

            # On regarde si la chaine de la commande contient quelque chose entre les caractères -o et -F (on cherche un dossier)
            x = re.search(r'(?<=-o\s).*(?=\s-F)', self.final_cmd.GetValue())
            if x > 0:
                y = x.group(0)
                y = y.strip()
                if os.path.isdir(y):
                    self.datas["out"] = y
                    self.openfolder.Enable(True)
                else:
                    z = os.path.dirname(y)
                    if os.path.isdir(z):
                        self.datas["out"] = "%s/" % z
                        self.openfolder.Enable(True)
            else:
                self.datas["out"] = ""
                self.openfolder.Enable(False)
        dlg.Destroy()

    def editCmdCheck(self, e):
        # L'utilisateur saisis du texte dans le champ commande finale
        # on pass la variable editcmdcheck à True
        # elle sera utilisée pour un test lorsque il voudra lancer le rendu
        self.editcmdcheck = True
        self.resetcmd_button.Enable(True)

    def renderIt(self, e):
        # le champ commande finale a-t-il été modifié et non enregistré?
        # La variable editcmdcheck nous indique si oui ou non
        if self.editcmdcheck:
            dlg = wx.MessageDialog(self, 'la commande a été modifiée. Utiliser cette nouvelle commande (clickez sur OK pour confirmer)?', 'Message', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_OK:
                self.strcmd = self.final_cmd.GetValue()
                self.editcmdcheck = False
                self.resetcmd_button.Enable(False)
                self.sendtoblender_statusbar.SetStatusText(self.strcmd, 0)
            else:
                self.sendtoblender_statusbar.SetStatusText("/!\ Commande utilisée: %s" % self.strcmd, 0)
            dlg.Destroy()

        # La checkbox mémoriser l'exécutable est-elle cochée
        # Si oui on ajoute au fichier executables.txt l'exécutable renseigné, s'il n'est pas déjà dans le fichier
        if self.saveexec_checkbox.GetValue() is True:
            f = open(gpth('/datas/executables.txt'), 'r')
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
                nf = open(gpth('/datas/executables.txt'), 'a')
                nf.write(str(self.datas["bin"]))
                nf.close()

        # On envoie la commande finale a blender (aller à la fonction runRendering)
        wx.CallAfter(self.runRendering)

    def stopProc(self, e):
        # Méthode pour arrêter le processus, accessible par le bouton stopprocess_button
        pid = self.pid
        self.process.CloseOutput()
        self.renderit_button.Enable(True)
        self.stopprocess_button.Enable(False)
        self.sendtoblender_statusbar.SetStatusText("Processus %s interrompu!" % pid, 0)

    def openImgDir(self, e):
        # Ouvrir le dossier contenant l'image
        # TODO: rendre cross plateforme...
        if self.datas["out"] != "":
            imgdir = os.path.dirname(self.datas["out"])
            dlg = ib.ImageDialog(self, imgdir)
            if dlg.ShowModal() == wx.ID_OK:
                subprocess.call(['gvfs-open', dlg.GetFile()])
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, 'Aucun dossier n\'a été sélectionné! Veuillez retourner au formulaire pour en définir un.', 'Message', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def quitWin(self, e):
        # Fermer la fenêtre
        self.Close()

