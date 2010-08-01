#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyReinforcement - calulation of reinforced concrete bar's area
# Copyright (C) 2010  P. Mavrogiorgos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Βιβλιοθήκες
from __future__ import division
import wx
from math import pi
from wx.lib.wordwrap import wordwrap

try:
    from agw import floatspin as FS
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.floatspin as FS

ROW = 6         # Από αυτή της σειρα και κάτω αρχίζουν τα δεδομένα των πλεγμάτων
ROW2 = 9        # Από αυτή τη σειρά και κάτω αρχίζουν τα δεδομένα των τυποποιημένων πλεγμάτων B500A
ROW3 = 12       # Σε αυτή τη σειρά είναι το άθροισμά των πλεγμάτων
BORDER = 5      # Το περιθώριο που θα αφήνουν οι sizers

# Σε περίπτωση που θέλουμε να αλλάξουμε τις default τιμές του προγράμματος απλά άλλαζουμε τις τιμές στο dictionary DATA
DATA = { u"bw" : "25", u"c" : "30", u"Fw":"10", u"Dmax": "16", u"Ανοχή":"0.2" }

# To όνομα και το εμβαδό των τυποποιημένων πλεγμάτων
TYPOPOIHMENA = {u"T131" : "1.31", u"T188" : "1.88", u"T196" : "1.96", u"T377" : "3.77", u"T92" : "0.92", u"T139" : "1.39", u"O92" : "0.92"}

# H μεταβλτήτη STYLES περιέχει τα styles του κεντρικού παράθυρου της εφαρμογής - μπαίνει στο self.frame.__init__
# H wx.DEFAULT_FRAME_STYLE = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX | wx.RESIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.SYSTEM_CAPTION
STYLES = wx.STAY_ON_TOP | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.RESIZE_BORDER

class MyFrame(wx.Frame):
    u""" Η κλάση αυτή δημιουργεί το κεντρικό παράθυρο της εφαρμογής"""
    def __init__(self):
        # Δημιουργία του κεντρικού Frame και του panel που συνδέεται μαζί του
        self.frame = wx.Frame.__init__(self, None, -1, u"pyReinforcement",style = STYLES)
        self.panel = wx.Panel(self)

        self.BOLD_FONT = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
        self.DEFAULT_FONT = wx.Font(8 ,wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        self.panel.SetFont(self.DEFAULT_FONT)           # Δεν είναι απαραίτητο

        # Δήλωση μεταβλητών. δηλώνονται και μεταβλητές που δε χρειάζονται αλλά έτσι είναι πιο εύκολος ο προγραμματισμός στη συνέχεια.
        self.spinner = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.D_Lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.As = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.cm2 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.AsCtrlText = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.As_string = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.checkbox = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.fi = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.ana = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.sum = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.sumCtrl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        self.bw = float(DATA[u"bw"])
        self.Dmax = float(DATA[u"Dmax"])
        self.c = float(DATA[u"c"])
        self.Fw = float(DATA[u"Fw"])
        self.Tol = float(DATA[u"Ανοχή"])

        # Κλήση λοιπών συναρτήσεων

        self.create_widgets_rabdoi()
        self.create_widgets_plegmata()
        self.create_widgets_typopoiimena()
        self.create_widgets_sum_plegmata()
        self.create_sizers()
        self.place_widgets_in_sizers()
        self.bind_events()
        self.renew(1)         # Το τρέχω για να γίνουν οι πράξεις στα πλέγματα
        self.create_menu()

    def bind_events(self):
        u""" Η συνάρτηση αυτή κάνει bind τα events "Ενεργοποίηση checkbox", "Γύρισμα του spinbutton" και "Aλλαγή του TextCtrl"."""
        for i in range(0,ROW - 1):
            self.spinner[i].Bind(wx.EVT_SPINCTRL, self.renew)
            self.checkbox[i].Bind(wx.EVT_CHECKBOX, self.renew)
            self.D_Lbl[i].Bind(wx.EVT_TEXT, self.renew)
        for i in range(ROW,ROW2):
            self.spinner[i].Bind(wx.EVT_SPINCTRL, self.renew)
            self.checkbox[i].Bind(wx.EVT_CHECKBOX, self.renew)
            self.D_Lbl[i].Bind(wx.EVT_TEXT, self.renew)
        for i in range(ROW2,ROW3):
            self.spinner[i].Bind(wx.EVT_SPINCTRL, self.renew)
            self.checkbox[i].Bind(wx.EVT_CHECKBOX, self.renew)
            self.fi[i].Bind(wx.EVT_COMBOBOX, self.renew)

    def create_widgets_rabdoi(self):
        # Δημιουργία των widgets των ράβδων. Εδώ δημιουργούνται τα widgets με τα μεταβλητά Φ (TextCtrl)
        for i in range(0,ROW - 1):
            self.checkbox[i] = wx.CheckBox(self.panel, -1, "", )
            self.spinner[i] = wx.SpinCtrl(self.panel, -1, "", size = (45, -1))
            self.spinner[i].SetRange(0, 100)
            self.spinner[i].SetValue(0)
            self.fi[i] = wx.StaticText(self.panel, -1, u"Φ")
            self.D_Lbl[i] = wx.TextCtrl(self.panel, -1, str(2*i+12), size = (30, -1))
            self.As[i] = 0
            self.AsCtrlText[i] = wx.TextCtrl(self.panel, -1, "%.2f" % self.As[i],  size = (40, -1))
            self.cm2[i] = wx.StaticText(self.panel, -1, u"cm2")

        # Δημιουργία του widget του αθροίσματος των ράβδων
        for i in range(ROW - 1,ROW):
            self.sum[i] = wx.StaticText(self.panel, -1, u"Άθροισμα :")
            self.sumCtrl[i] = wx.TextCtrl(self.panel, -1, "0.00",size = (40, -1))
            self.cm2[i] = wx.StaticText(self.panel, -1, u"cm2")
            self.sum[i].SetFont(self.BOLD_FONT)
            self.sumCtrl[i].SetFont(self.BOLD_FONT)

    def create_widgets_plegmata(self):
        # Δημιουργία των widgets των πλεγμάτων.
        for i in range (ROW,ROW2):
            self.checkbox[i] = wx.CheckBox(self.panel, -1, "", )
            self.fi[i] = wx.StaticText(self.panel, -1, u"Φ")
            self.D_Lbl[i] = wx.TextCtrl(self.panel, -1, unicode(str((i-ROW)*2 + 8)), size = (30, -1))
            self.ana[i] = wx.StaticText(self.panel, -1, u"/", size = (5,-1))
            self.spinner[i] = FS.FloatSpin(self.panel, -1, min_val=1, max_val=100,
                                increment=0.5, value=20,size = (55, -1), extrastyle=FS.FS_LEFT)
            self.spinner[i].SetFormat("%f")
            self.spinner[i].SetDigits(1)
            self.As[i] = 0
            self.AsCtrlText[i] = wx.TextCtrl(self.panel, -1, "%.2f" % self.As[i],  size = (40, -1))
            self.cm2[i] = wx.StaticText(self.panel, -1, u"cm2/m")

    def create_widgets_typopoiimena(self):
        # Δημιουργία του widget του αθροίσματος των τυποποιημένων πλεγμάτων

        self.typopoihmena_keys = TYPOPOIHMENA.keys()
        self.typopoihmena_values = TYPOPOIHMENA.values()

        for i in range (ROW2, ROW3):
            self.checkbox[i] = wx.CheckBox(self.panel, -1, "", )
            self.spinner[i] = wx.SpinCtrl(self.panel, -1, "", size = (45, -1))
            self.spinner[i].SetRange(0, 100)
            self.spinner[i].SetValue(0)
            self.fi[i] = wx.ComboBox(  self.panel, -1, size = (55,20), choices = TYPOPOIHMENA.keys())
            self.fi[i].SetFont(self.DEFAULT_FONT)
            self.As[i] = 0
            self.AsCtrlText[i] = wx.TextCtrl(self.panel, -1, "%.2f" % self.As[i],  size = (40, -1))
            self.cm2[i] = wx.StaticText(self.panel, -1, u"cm2/m")

        self.fi[ROW2].SetValue  ( self.typopoihmena_keys[0])
        self.fi[ROW2+1].SetValue( self.typopoihmena_keys[3])
        self.fi[ROW2+2].SetValue( self.typopoihmena_keys[6])

    def create_widgets_sum_plegmata(self):
        # Δημιουργία του widget του αθροίσματος των πλεγμάτων
        for i in range(ROW3, ROW3 + 1):
            self.sum[i] = wx.StaticText(self.panel, -1, u"Άθροισμα :")
            self.sumCtrl[i] = wx.TextCtrl(self.panel, -1, "0.00",size = (40, -1))
            self.cm2[i] = wx.StaticText(self.panel, -1, u"cm2/m")
            self.sum[i].SetFont(self.BOLD_FONT)
            self.sumCtrl[i].SetFont(self.BOLD_FONT)

    def MakeStaticBoxSizer(self, boxlabel):
        u""" Η συνάρτηση αυτή δημιουργεί StaticBoxSizers με το όνομα boxlabel"""
        # Στο συγκεκριμένο πρόγραμμα δεν είναι και πολύ χρήσιμη καθώς δημιουργούνται μόνο 2 staticboxsizers...
        box = wx.StaticBox(self.panel, -1, boxlabel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        return sizer

    def create_sizers(self):
        u""" Η συνάρτηση αυτή δημιουργεί τα απαιτούεμενα sizers"""
        # Δημιοργούνται 2 bagSizers. Ένα για τις ράβδους και ένα για τα πλέγματα. Μέσα σε αυτά τα δύο μπαίνουν όλα τα widgets
        # Κάθε bagSizer τοποθετείται μέσα σε ένα StaticboxSizer
        # Τα staticboxSizers μπαίνουν μέσα σε ένα VERTICAL BoxSizer.
        self.bagSizerRabdoi= wx.GridBagSizer(vgap = BORDER, hgap = BORDER)
        self.bagSizerPlegmata = wx.GridBagSizer(vgap = BORDER, hgap = BORDER)
        self.StaticBoxSizerRabdoi = self.MakeStaticBoxSizer(u"Ράβδοι")
        self.StaticBoxSizerPlegmata = self.MakeStaticBoxSizer(u"Πλέγματα")
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

    def place_widgets_in_sizers(self):
        u""" Η συνάρτηση αυτή αρχικά τοποθετεί τα widgets μέσα στα BagSizers (ράβδοι - πλέγματα)
        Στη συνέχεια τοποθετεί τα sizers μέσα στο κεντρικό Sizer"""

        # self.mainSizer.Add(wx.StaticLine(self.panel,1), 0, wx.EXPAND)

        # Τοποθέτηση των widgets των ράβδων μέσα στο δικό τους BagSizer
        for i in range(0,ROW - 1):
            self.bagSizerRabdoi.Add(self.checkbox[i], (i,0), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.spinner[i], (i,1), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.fi[i], (i,2), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.D_Lbl[i], (i,3), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.AsCtrlText[i], (i,4), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.cm2[i], (i,5), (1,1), wx.ALIGN_CENTER | wx.EXPAND)

        for i in range(ROW - 1,ROW):
            self.bagSizerRabdoi.Add(self.sum[i], (i,1), (1,3), wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
            self.bagSizerRabdoi.Add(self.sumCtrl[i], (i,4), (1,1), wx.ALIGN_CENTER)
            self.bagSizerRabdoi.Add(self.cm2[i], (i,5), (1,1), wx.ALIGN_CENTER | wx.EXPAND)

        # Τοποθέτηση των widgets των πλεγμάτων μέσα στο δικό τους BagSizer
        for i in range(ROW,ROW2):
            self.bagSizerPlegmata.Add(self.checkbox[i], (i-ROW,0), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.fi[i], (i-ROW,1), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.D_Lbl[i], (i-ROW,2), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.ana[i], (i-ROW,3), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.spinner[i], (i-ROW,4), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.AsCtrlText[i], (i-ROW,5), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.cm2[i], (i-ROW,6), (1,1), wx.ALIGN_CENTER | wx.EXPAND)

        for i in range(ROW2, ROW3):
            self.bagSizerPlegmata.Add(self.checkbox[i], (i-ROW,0), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.spinner[i], (i-ROW,2), (1,2), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.fi[i], (i-ROW,4), (1,1), wx.ALIGN_LEFT)
            self.bagSizerPlegmata.Add(self.AsCtrlText[i], (i-ROW,5), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.cm2[i], (i-ROW,6), (1,1), wx.ALIGN_CENTER | wx.EXPAND)

        for i in range(ROW3, ROW3+1):
            self.bagSizerPlegmata.Add(self.sum[i], (i-ROW,2), (1,3), wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
            self.bagSizerPlegmata.Add(self.sumCtrl[i], (i-ROW,5), (1,1), wx.ALIGN_CENTER)
            self.bagSizerPlegmata.Add(self.cm2[i], (i-ROW,6), (1,1), wx.ALIGN_CENTER | wx.EXPAND)

        # Τοποθέτηση των bagSizers μέσα στα StaticBoxSizers
        self.StaticBoxSizerRabdoi.Add(self.bagSizerRabdoi)
        self.StaticBoxSizerPlegmata.Add(self.bagSizerPlegmata)

        # Τοποθέτηση των StaticBoxSizers μέσα στo κεντρικό BoxSizer
        self.mainSizer.Add(self.StaticBoxSizerRabdoi, 0, wx.ALL| wx.EXPAND, BORDER)
        self.mainSizer.Add(self.StaticBoxSizerPlegmata, 0, wx.ALL| wx.EXPAND, BORDER)
        
        # Ηλίθιο bug που δεν το βρίσκω με ανάγκασε να ορίσω το ελάχιστο μέγεθος του παραθύρου
        # Ίσως κάποια στιγμή να πρέπει όλα τα μεγέθη (widgets-παραθύρων) να τα ορίσω βάσει πλατφόρμας (unix-win).
        self.mainSizer.SetMinSize((200,450))
        
        # Σωστή εμφάνιση του μεγέθους του sizer
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.mainSizer.SetSizeHints(self)
        
    def renew(self,event):
        u""" Η συνάρτηση αυτή προσπαθεί να ανανεώσει τις τιμές στο panel. Κοινώς να κάνει τις πράξεις."""
        ############################################################################################
        ########################################## Ράβδοι ##########################################
        # Αρχικά ελέγχεται πόσο είναι το εμβαδό για κάθε διάμετρο ράβδων
        # Στη συνέχεια ελέγεχεται αν ο αριθμός των ράβδων της κάθε διαμέτρου χωράνε σε μία στρώση
        # Αν δεν χωράνε καλείται η συνάρτηση change_color() και αλλάζει το χρώμα του widget
        # Μετά υπολογίζεται το άθροισμα του εμβαδού των ράβδων των διάμέτρων που έχουν επιλογεί στο checkbox
        # Τέλος υπολογίζεται αν οι ράβδοι που έχουν επιλέγεί (από διάφορες διαμέτρους), χωράνε σε μία στρώση
        sum = 0
        for i in range (0, ROW - 1):
            # Υπολογισμός του εμβαδού της κάθε διαμέτρου των ράβδων
            self.spinner[i].value = float(self.spinner[i].GetValue())
            self.As[i] = pi * float(self.D_Lbl[i].GetValue())**2 * self.spinner[i].value/4/100
            self.As_string[i] = u"%.2f" % self.As[i]
            self.AsCtrlText[i].SetValue(self.As_string[i])
            # Αλλαγή του χρώματος του As αν τα σίδερα δε χωράνε σε μία στρώση.
            self.change_color(i)

            # Υπολογισμός του αθροίσματος των ράβδων
            sum += int(self.checkbox[i].IsChecked()) * float(self.AsCtrlText[i].GetValue())

        # έλεγχος αν οι ράβδοι που έχουν επιλεγεί (Checkbutton) χωράνε σε μία στρώση.
        # ΔΕ γίνεται χρήση της μεταβλητής Tolerance.
        number_of_checked_bars = 0              # Αριθμός των ράβδων που έχουν επιλεγεί
        length_of_checked_bars = 0              # Αναφέρεται στο συνολικό μήκος των ράβδων (σε τομή) που έχουν επιλεγεί (παράλληλα με το bw).
        max_Fl = 0                              # Η μέγιστη διάμέτρος των ράβδων που έχουν επιλεγεί.

        for i in range(0,ROW - 1):
            number_of_checked_bars += float(self.checkbox[i].IsChecked()) * self.spinner[i].value
            length_of_checked_bars += float(self.checkbox[i].IsChecked()) * self.spinner[i].value * float(self.D_Lbl[i].GetValue())
            if max_Fl < float(self.D_Lbl[i].GetValue()) * float(self.checkbox[i].IsChecked()):
                max_Fl = float(self.D_Lbl[i].GetValue())

        number_of_spaces = (number_of_checked_bars - 1)
        min_dist = max(20, max_Fl, self.Dmax + 5)
        min_bw = (2 * self.c + 2 * self.Fw + min_dist * number_of_spaces + length_of_checked_bars) / 10

        # Τοποθέτηση του υπολογισθέντος αθροίσματος στο widget και ανάλογη αλλαγή του χρώματος της γραμματοσειράς
        for i in range(ROW - 1,ROW):
            self.sumCtrl[i].SetValue(unicode(sum))
            if min_bw > self.bw:
                self.sumCtrl[i].SetForegroundColour("red")
            else:
                self.sumCtrl[i].SetForegroundColour("black")
                

        ############################################################################################
        ######################################## Πλέγματα ##########################################
        # Αρχικά υπολογίζεται το εμβαδό του κάθε πλέγματος για κάθε διάμετρο ή τύπο πλέγματος,
        # ανάλογα με την απόσταση ή το πλήθος που έχει υπολογιστεί.
        # Μετά υπολογίζεται το άθροισμα των εργοταξιακών πλεγμάτων και στη συνέχεια το άθροισμμα
        # των τυποποιημένων πλεγμάτων
        sum = 0
        # Για τα εργοταξιακά πλέγματα
        for i in range (ROW,ROW2):
            self.spinner[i].value = float(self.spinner[i].GetValue())
            self.As[i] = (pi * float(self.D_Lbl[i].GetValue())**2 / 4)  * (100 / self.spinner[i].value) / 100
            self.As_string[i] = u"%.2f" % self.As[i]
            self.AsCtrlText[i].SetValue(self.As_string[i])
            # Υπολογισμός του αθροίσματος των πλεγμάτων
            sum += int(self.checkbox[i].IsChecked()) * float(self.AsCtrlText[i].GetValue())
        # Για τα τυποποιημένα πλέγματα
        for i in range (ROW2,ROW3):
            self.spinner[i].value = float(self.spinner[i].GetValue())
            self.As[i] = float(TYPOPOIHMENA[self.fi[i].GetValue()]) * self.spinner[i].value
            self.As_string[i] = u"%.2f" % self.As[i]
            self.AsCtrlText[i].SetValue(self.As_string[i])
            # Υπολογισμός του αθροίσματος των τυποποιημένων πλεγμάτων
            sum += int(self.checkbox[i].IsChecked()) * float(self.AsCtrlText[i].GetValue())
        # Τοποθέτηση του υπολογισθέντος αθροίσματος στο widget
        for i in range(ROW3, ROW3 + 1):
            self.sumCtrl[i].SetValue(unicode(sum))

        # Ανανέωση του panel για να αλλάξουν τα χρώματα όταν γινονται αλλαγες στις σταθερες
        self.Refresh()
    
    def create_menu(self):
        """ Η συνάρτηση αυτή δημιουργεί το μενού"""
        # Create StatusBar
        self.CreateStatusBar()
        # Set menu
        filemenu = wx.Menu()
        filemenu.Append(wx.ID_EXIT, u"&Έξοδος", u"Βγείτε από το πρόγραμμα")
        optionsmenu = wx.Menu()
        optionsmenu.Append(wx.ID_PREFERENCES, u"Σταθερές", u"Δώστε τις σταθερές του προγράμματος")
        helpmenu = wx.Menu()
        helpmenu.Append(wx.ID_HELP, u"&Βοήθεια", u"Βοήθεια σχετικά με το πρόγραμμα")
        helpmenu.AppendSeparator()
        helpmenu.Append(wx.ID_ABOUT, u"&Πληροφορίες", u"Πληροφορίες σχετικά με το πρόγραμμα")

        menubar = wx.MenuBar()
        menubar.Append(filemenu, u"&Αρχείο")
        menubar.Append(optionsmenu, u"&Επιλογές")
        menubar.Append(helpmenu, u"&Βοήθεια")
        # Create menubar
        self.SetMenuBar(menubar)

        # binding events
        wx.EVT_MENU(self, wx.ID_ABOUT, self.on_about)
        wx.EVT_MENU(self, wx.ID_HELP, self.on_help)
        wx.EVT_MENU(self, wx.ID_EXIT, self.on_exit)
        wx.EVT_MENU(self, wx.ID_PREFERENCES, self.on_preferences)

    def on_preferences(self,event):
        u""" Η συνάρτηση αυτή τρέχει όταν επιλέγονται τα "Δεδομένα" από το μενού "Επιλογές"""
        # Δημιουργία του παράθυρου από το οποίο ο χρήστης θα εισάγει τα δεδομένα
        dlg = DialogStatheres(self, -1, title = u"Σταθερές", style=wx.DEFAULT_DIALOG_STYLE)
        val = dlg.ShowModal()

        # Σε περίπτωση που πατήσουμε ΟΚ επιστρέφονται οι τιμές διαφορετικά μένουν οι παλιές
        if val == wx.ID_OK:
            self.bw = float(dlg.bw_t.GetValue())
            self.c = float(dlg.c_t.GetValue())
            self.Fw = float(dlg.Fw_t.GetValue())
            self.Dmax = float(dlg.Dmax_t.GetValue())
            self.Tol = float(dlg.Tol_t.GetValue())
        self.renew(self)
        dlg.Destroy()

        # όταν κλείνει το παράθυρο διαλόγου με τα δεδομένα, ξανατρέχει η συνάρτηση on_spin για να ανανεωθούν τα χρώματα του Αs
        self.renew(self)


    def on_about(self, evt):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = u"Εμβαδόν Οπλισμών"
        info.Version = u"1.0"
        #info.Copyright = u"Παναγιώτης Μαυρογιώργος\nΠολιτικός Μηχανικός\nΑ.Μ. ΤΕΕ 122585"
        info.Description = wordwrap(
            u"Το πρόγραμμα αυτό υπολογίζει το εμβαδόν ράβδων και πλεγμάτων οπλισμού.\n\n"
            u"Για οποιαδήποτε σχόλια ή παρατηρήσεις παρακαλώ, "
            u"επικοινωνήστε μαζί μου στην ηλεκτρονική διεύθυνση\n"
            u"pmav99@gmail.com",400, wx.ClientDC(self))
        info.WebSite = (u"http://code.google.com/p/py-reinforcement/", u"url")
        info.Developers = [ u"Παναγιώτης Μαυρογιώργος, Πολιτικός Μηχανικός Δ.Π.Θ."]
        info.License = wordwrap(
                       u"Επιτρέπεται η ελεύθερη χρήση και διανομή του προγράμματος.\n\n"
                       u"Ο δημιουργός του προγράμματος, ουδεμία ευθύνη αναλαμβάνει\n"
                       u"για τυχον βλάβες που θα προκύψουν από τη χρήση του.",400, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def on_help(self,event):
        msg = wordwrap(
            u"Στα συνολικά αθροίσματα εμφανίζονται μόνο όσες σειρές έχουν επιλεγεί στην πρώτη στήλη.\n\n"
            u"Από το menu Επιλογές διαλέγοντας 'Σταθερές' δίνετε στοιχεία της διατομής που σας ενδιαφέρει. "
            u"Με τα στοιχεία αυτά ελέγχεται αν τα σίδερα που έχουν εκλεγεί χωράνε σε μία στρώση.\n\n"
            u"Αν οι ράβδοι που έχουν επιλεγεί είναι ο μέγιστος αριθμός ράβδων της αυτής διαμέτρου που χωράνε σε μία στρώση,"
            u" τότε το As εμφανίζεται με ΜΠΛΕ γραμματοσειρά.\n\n"
            u"Αν οι ράβδοι που έχουν επιλεγεί ΔΕ χωράνε σε μία στρώση τότε το As εμφανίζεται με ΚΟΚΚΙΝΗ γραμματοσειρά.\n\n"
            u"Αν οι ράβδοι που έχουν επιλεγεί ΔΕ χωράνε σε μία στρώση μεν, αλλά για τιμή μικρότερη από τη μεταβλήτη Ανοχή,"
            u" τότε εμφανίζονται με ΜΩΒ γραμματοσειρά. Π.χ. αν η Ανοχή είναι ίση με 0.1 και χωράνε 4.93 ράβδοι ανά στρώση,"
            u" τότε το πρόγραμμα όταν βάλουμε 5 ράβδους θα δείξει το αποτέλεσμα με MΩΒ χρώμα.\n\n"
            u"Στη σειρά του αθροίσματος αν τα σίδερα δε χωράνε σε μία στρώση τότε το αποτέλεσμα εμφανίζεται με ΚΟΚΚΙΝΟ χρώμα."
            u" Η τιμή της Ανοχής ΔΕΝ επηρρεάζει τη χρωματική απεικόνιση του αθροίσματος.",400, wx.ClientDC(self))
        msg_box = wx.MessageBox(msg)

    def on_exit(self, event):
        self.Close(True)

    def change_color(self,i):
        """ Η συνάρτηση αυτή αλλάζει το χρώμα του As ανάλογα με το αν τα σίδερα χωρανε σε μία στρώση"""
        # Με μπλε χρώμα εμφανίζεται το Αs όταν τα σίδερα χωράνε ακριβώς σε μία στρώση
        # Με κόκκινο χρώμα εμφανίζεται το As όταν τα σίδερα ΔΕ χωράνε σε μία στρώση.
        # Η μεταβλητή tol_used παίρνει την τιμή Τrue αν έχει ληφθεί υπόψη η ανοχή (Tolerance) και False αν δεν έχει ληφθεί υπόψη

        # Σε περίπτωση που έχει την τιμή True τότε το Αs εμφανίζεται με μωβ αντί για μπλε χρώμα

        number, tol_used = self.number_of_bars(self.bw, self.Dmax, self.c, self.Fw, int(self.D_Lbl[i].GetValue()), self.Tol)

        if number == self.spinner[i].value and tol_used:
            self.AsCtrlText[i].SetForegroundColour("purple")
        elif number == self.spinner[i].value and not(tol_used):
            self.AsCtrlText[i].SetForegroundColour("blue")
        elif number < self.spinner[i].value:
            self.AsCtrlText[i].SetForegroundColour("red")
        else:
            self.AsCtrlText[i].SetForegroundColour("black")

    def number_of_bars(self, bw, Dmax, c, Fw, Fl, Tol):
        """ Η συνάρτηση αυτή επιστρέφει τον μέγιστο αριθμό των ράβδων που χωράνε σε μια στρώση σε μια δεδομένη διατομή"""
        # Επιστρέφει 2 τιμές. Η πρώτη είναι ο αριθμός των ράβδων που χωράνε σε μία στρώση. Η δεύτερη είναι Τrue/Fasle ανάλογα με το αν
        # χρησιμοποιήθηκε η ανοχή ή όχι.
        min_dist = max(20, Fl, Dmax + 5)
        num_bars = (bw*10 - 2 * c - 2 * Fw + min_dist)/(Fl + min_dist)

        # Αν ο αριθμός των ράβδων (αστρογγυλοποίητος) απέχει από το αμέσως μεγαλύτερο ακέραιο τιμή μικρότερη από την ανοχή (tol)
        # τότε θεωρείται ότι τα σίδερα χωράνε σε μία στρώση αλλά τα αποτελέσματα θα εμφανίζονται με μωβ χρώμα αντί για μπλε (function change_colors)
        if (1 + int(num_bars)) - num_bars <= Tol:
            return int(num_bars)+1, True
        else:
            return int(num_bars), False


class DialogStatheres(wx.Dialog):
    """ Η κλάση αυτή δημιουργεί το παράθυρο διαλόγου από το οποίο δίνονται τα δεδομένα για τον έλεγχο αν χωράνε τα σίδερα σε μία στρώση"""
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE, useMetal=False):

        wx.Dialog.__init__(self,parent, -1, title)

        # create sizer
        sizer = wx.FlexGridSizer(cols = 2, vgap = 5, hgap = 5)
        btnSizer = wx.StdDialogButtonSizer()
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # create wigdets
        self.bw_l = wx.StaticText(self, -1, u" Πλάτος δοκού bw (cm) :")
        self.bw_t = wx.TextCtrl(self, -1, "", size=(60,-1),validator=DataXforValidator(DATA, u"bw"))
        self.c_l = wx.StaticText(self, -1, u"Επικάλυψη c (mm) :")
        self.c_t = wx.TextCtrl(self, -1, "", size=(60,-1),validator=DataXforValidator(DATA, u"c"))
        self.Fw_l = wx.StaticText(self, -1, u"Φ Συνδετήρα (mm) :")
        self.Fw_t = wx.TextCtrl(self, -1, "", size=(60,-1),validator=DataXforValidator(DATA, u"Fw"))
        self.Dmax_l = wx.StaticText(self, -1, u" Dmax Αδρανών (mm) :")
        self.Dmax_t = wx.TextCtrl(self, -1, "", size=(60,-1),validator=DataXforValidator(DATA, u"Dmax"))
        self.Tol_l = wx.StaticText(self, -1, u"Ανοχή :")
        self.Tol_t = wx.TextCtrl(self, -1, "", size=(60,-1),validator=DataXforValidator(DATA, u"Ανοχή"))
        self.text = wx.StaticText(self, -1, u"Η ελάχιστη απόσταση μεταξύ των \nράβδων είναι ίση με:\n\nmax {20mm ; Φmax ; Dαδρ + 5mm}")

        # create buttons
        self.btn_OK = wx.Button(self, wx.ID_OK)
        self.btn_OK.SetDefault()
        self.btn_Cancel = wx.Button(self, wx.ID_CANCEL)

        # place widgets in sizer
        sizer.Add(self.bw_l, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.bw_t, 0,  wx.ALIGN_CENTER)
        sizer.Add(self.c_l, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.c_t, 0,  wx.ALIGN_CENTER)
        sizer.Add(self.Fw_l, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Fw_t, 0,  wx.ALIGN_CENTER)
        sizer.Add(self.Dmax_l, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Dmax_t, 0,  wx.ALIGN_CENTER)
        sizer.Add(self.Tol_l, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Tol_t, 0,  wx.ALIGN_CENTER)

        # place buttons in btnsizer
        btnSizer.Add(self.btn_OK, 0)
        btnSizer.Add(self.btn_Cancel, 0)

        # place sizers and various widgets in mainSizer
        mainSizer.Add(sizer,0, wx.ALL | wx.ALIGN_CENTER, BORDER)
        mainSizer.Add(wx.StaticLine(self,-1), 0, wx.ALL |wx.EXPAND, BORDER/2)
        mainSizer.Add(self.text,0, wx.ALIGN_CENTER, BORDER)
        mainSizer.Add(wx.StaticLine(self,-1), 0, wx.ALL |wx.EXPAND, BORDER/2)
        mainSizer.Add(btnSizer,0, wx.ALL | wx.ALIGN_CENTER, BORDER)

        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

class DataXforValidator(wx.PyValidator):
    """ Ο validator αυτός χρησιμοποιείται για να μεταφέρει τιμές προς και από ένα παράθυρο"""
    def __init__(self, data, key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key

    def Clone(self):
        """Note that every validator must implement the Clone() method."""
        return DataXforValidator(self.data, self.key)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        textCtrl.SetValue(self.data.get(self.key, ""))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = textCtrl.GetValue()
        return True

class MyApp(wx.App):
    """This is my application"""
    def __init__(self, redirect=False, filename=None):
        """ Overiding the OnInit() to create our frame"""
        wx.App.__init__(self, redirect, filename)
        frame1 = MyFrame()
        frame1.Show(True)
        return None


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
