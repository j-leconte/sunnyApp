#  -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import re
import sqlite3
import unicodedata
import random
from operator import itemgetter

# Notes of random things to implement:
# Disobey and identified to add later
# Add dmg from vitesse/poids/niveau/ohko
# Weather
# Mettre en balise modo les infos non gérables sur un tour type lance soleil se lance direct si soleil
# Changer ordre proc statuts
# Prendre en compte le nombre de tours pour sommeil/conf/piege

# import GUI and database
Ui_MainWindow, QtBaseClass = uic.loadUiType("Interface.ui")
conn = sqlite3.connect('sunrise_dex.sqlite')
c = conn.cursor()
conn2 = sqlite3.connect('buildsunny.sqlite')
c2 = conn2.cursor()

# create main class
class MainWindow(QMainWindow):

    # base def
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.applycustom.clicked.connect(self.SplitCustom) # effect of first buttun apply in pokemon1
        self.ui.applycustom_2.clicked.connect(self.SplitCustom2) # effect of first buttun apply in pokemon1
        self.ui.applycustom_3.clicked.connect(self.SplitCustom3)
        self.ui.applycustom_4.clicked.connect(self.SplitCustom4)
        self.ui.applycustom_5.clicked.connect(self.SplitCustom5)
        self.ui.applycustom_6.clicked.connect(self.SplitCustom6)

        # get pokemon or attacks
        self.ui.pokedex.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokedex_2.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokedex_3.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokedex_4.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokedex_5.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokedex_6.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])
        self.ui.pokecapture.addItems([nom[0] for nom in c.execute("SELECT nom FROM pokemons")][0:1042])

        self.ui.checkattaque.clicked.connect(self.generatePokemon) # fill attack box & fill pokemon stats
        self.ui.checkattaque_2.clicked.connect(self.generatePokemon2) # fill attack box & fill pokemon stats
        self.ui.checkattaque_3.clicked.connect(self.generatePokemon3)
        self.ui.checkattaque_4.clicked.connect(self.generatePokemon4)
        self.ui.checkattaque_5.clicked.connect(self.generatePokemon5)
        self.ui.checkattaque_6.clicked.connect(self.generatePokemon6)

        self.ui.applygenerator.clicked.connect(self.generateattack) # apply button 2 to generate attack
        self.ui.applygenerator_2.clicked.connect(self.generateattack2) # apply button 2 to generate attack
        self.ui.applygenerator_3.clicked.connect(self.generateattack3)
        self.ui.applygenerator_4.clicked.connect(self.generateattack4)
        self.ui.applygenerator_5.clicked.connect(self.generateattack5)
        self.ui.applygenerator_6.clicked.connect(self.generateattack6)

        self.ui.fightbutton.clicked.connect(self.fightInit) # generate the fight
        self.ui.clearall.clicked.connect(self.clearFunAll) # clear first page
        self.ui.clear_1.clicked.connect(self.clearFun1) # clear poke 1
        self.ui.clear_2.clicked.connect(self.clearFun2) # clear poke 2
        self.ui.clear_3.clicked.connect(self.clearFun3) # clear poke 3
        self.ui.clear_4.clicked.connect(self.clearFun4) # clear poke a
        self.ui.clear_5.clicked.connect(self.clearFun5) # clear poke b
        self.ui.clear_6.clicked.connect(self.clearFun6) # clear poke c

        self.ui.codestatutbox.clicked.connect(self.putstat) # Add all statuts and modif

        #Second page : outils
        self.ui.genbutton.clicked.connect(self.pokegen)
        self.ui.continentok.clicked.connect(self.checkregion)
        self.ui.regionok.clicked.connect(self.checkzone)
        self.ui.zoneok.clicked.connect(self.checkmethode)
        self.ui.capturebutton.clicked.connect(self.pokecatch)
        self.ui.diceroll.clicked.connect(self.rolldice)


    def normalise_string_attaques(self,s):
        # pour l'index des attaques mal orthographiée. opérations de simplifications devant être appliquées à l'index et aux attaques raw à march
        s=s.lower()
        s=unicodedata.normalize('NFKD',s)
        s= u''.join(c for c in s if not unicodedata.combining(c))
        s=re.sub("\W","",s,flags=re.UNICODE)
        return s

    def init_index_attaques(self):
    	# cette partie doit tourner une seule fois à l'init. mets-la où ça t'arrange.
        # la variable all_attaques_out doit être accessible par attaque_match() sois mets-la en variable globale, soit mets-la dans les arguments de attaque_match()
    	all_attaques_out={}
    	c.execute("select nom from attaques")
    	for row in c.fetchall():
    		propre=row[0]
    		sale=self.normalise_string_attaques(propre)
    		all_attaques_out[sale]=propre
    	return all_attaques_out

    def init_index_pkmon(self):
    	# cette partie doit tourner une seule fois à l'init. mets-la où ça t'arrange.
        # la variable all_attaques_out doit être accessible par attaque_match() sois mets-la en variable globale, soit mets-la dans les arguments de attaque_match()
    	all_pokemon_out={}
    	c.execute("select nom from pokemons")
    	for row in c.fetchall():
    		propre=row[0]
    		sale=self.normalise_string_attaques(propre)
    		all_pokemon_out[sale]=propre
    	return all_pokemon_out

    def levenshtein(self,s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)

        #  len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 #  j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       #  than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def attaque_match(self,att,all_attaques):
    	# pour calculateur sunrise. permet de retrouver le nom d'une attaque à partir d'un nom possiblement mal orthographié. le premier argument est le nom d'attaque mal orthographié à traiter. Les deux autres sont des listes fixes. Tu peux me les passer là en argument ou les mettre en variable globale, c'est comme ça t'arrange
    	att=self.normalise_string_attaques(att) # normalise casse, diacritiques, et supprime tous les caractères non alphabétiques
    	if att in all_attaques:
    		return all_attaques[att]

    	# on attaque les distances, cette partie peut prendre du temps
    	distance_max=3
    	bon_candidat=None
    	for candidat in all_attaques:
    		distance=self.levenshtein(att,candidat)
    		if distance<distance_max:
    			bon_candidat=candidat
    			distance_max=distance

    	if bon_candidat:
    		return all_attaques[bon_candidat]

    	raise KeyError("erreur")
    	return

    def pvToColor(self,pvcurrent,pvmax):
        if pvcurrent > pvmax*2/3:
            pvcolor="[color=#669900]"
        elif pvcurrent <= pvmax*2/3 and pvcurrent >= pvmax/3:
            pvcolor="[color=#ffcc00]"
        else:
            pvcolor="[color=#ff6600]"
        return pvcolor

    def build_dict(self,seq, key):
        return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

    def typeMatrix(self,typeAtt,typeDef):
        # defending types inpkmon1["side"] of attacking types
        if typeDef=='':
            return 1
        else:
            typeChart = {'normal': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 0.5, 'insecte': 1, 'spectre': 0, 'acier': 0.5, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 1, 'ténèbres': 1, 'fée': 1},
            'combat': {'normal': 2, 'combat': 1, 'vol': 0.5, 'poison': 0.5, 'sol': 1, 'roche': 2, 'insecte': 0.5, 'spectre': 0, 'acier': 2, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 0.5, 'glace': 2, 'dragon': 1, 'ténèbres': 2, 'fée': 0.5},
            'vol': {'normal': 1, 'combat': 2, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 0.5, 'insecte': 2, 'spectre': 1, 'acier': 0.5, 'feu': 1, 'eau': 1, 'plante': 2, 'électrique': 0.5, 'psy': 1, 'glace': 1, 'dragon': 1, 'ténèbres': 1, 'fée': 1},
            'poison': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 0.5, 'sol': 0.5, 'roche': 0.5, 'insecte': 1, 'spectre': 0.5, 'acier': 0, 'feu': 1, 'eau': 1, 'plante': 2, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 1, 'ténèbres': 1, 'fée': 2},
            'sol': {'normal': 1, 'combat': 1, 'vol': 0, 'poison': 2, 'sol': 1, 'roche': 2, 'insecte': 0.5, 'spectre': 1, 'acier': 2, 'feu': 2, 'eau': 1, 'plante': 0.5, 'électrique': 2, 'psy': 1, 'glace': 1, 'dragon': 1, 'ténèbres': 1, 'fée': 1},
            'roche': {'normal': 1, 'combat': 0.5, 'vol': 2, 'poison': 1, 'sol': 0.5, 'roche': 1, 'insecte': 2, 'spectre': 1, 'acier': 0.5, 'feu': 2, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 1, 'glace': 2, 'dragon': 1, 'ténèbres': 1, 'fée': 1},
            'insecte': {'normal': 1, 'combat': 0.5, 'vol': 0.5, 'poison': 0.5, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 0.5, 'acier': 0.5, 'feu': 0.5, 'eau': 1, 'plante': 2, 'électrique': 1, 'psy': 2, 'glace': 1, 'dragon': 1, 'ténèbres': 2, 'fée': 0.5},
            'spectre': {'normal': 0, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 2, 'acier': 1, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 2, 'glace': 1, 'dragon': 1, 'ténèbres': 0.5, 'fée': 1},
            'acier': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 2, 'insecte': 1, 'spectre': 1, 'acier': 0.5, 'feu': 0.5, 'eau': 0.5, 'plante': 1, 'électrique': 0.5, 'psy': 1, 'glace': 2, 'dragon': 1, 'ténèbres': 1, 'fée': 2},
            'feu': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 0.5, 'insecte': 2, 'spectre': 1, 'acier': 2, 'feu': 0.5, 'eau': 0.5, 'plante': 2, 'électrique': 1, 'psy': 1, 'glace': 2, 'dragon': 0.5, 'ténèbres': 1, 'fée': 1},
            'eau': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 2, 'roche': 2, 'insecte': 1, 'spectre': 1, 'acier': 1, 'feu': 2, 'eau': 0.5, 'plante': 0.5, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 0.5, 'ténèbres': 1, 'fée': 1},
            'plante': {'normal': 1, 'combat': 1, 'vol': 0.5, 'poison': 0.5, 'sol': 2, 'roche': 2, 'insecte': 0.5, 'spectre': 1, 'acier': 0.5, 'feu': 0.5, 'eau': 2, 'plante': 0.5, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 0.5, 'ténèbres': 1, 'fée': 1},
            'électrique': {'normal': 1, 'combat': 1, 'vol': 2, 'poison': 1, 'sol': 0, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 1, 'feu': 1, 'eau': 2, 'plante': 0.5, 'électrique': 0.5, 'psy': 1, 'glace': 1, 'dragon': 0.5, 'ténèbres': 1, 'fée': 1},
            'psy': {'normal': 1, 'combat': 2, 'vol': 1, 'poison': 2, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 0.5, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 0.5, 'glace': 1, 'dragon': 1, 'ténèbres': 0, 'fée': 1},
            'glace': {'normal': 1, 'combat': 1, 'vol': 2, 'poison': 1, 'sol': 2, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 0.5, 'feu': 0.5, 'eau': 0.5, 'plante': 2, 'électrique': 1, 'psy': 1, 'glace': 0.5, 'dragon': 2, 'ténèbres': 1, 'fée': 1},
            'dragon': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 0.5, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 2, 'ténèbres': 1, 'fée': 0},
            'ténèbres': {'normal': 1, 'combat': 0.5, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 2, 'acier': 1, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 2, 'glace': 1, 'dragon': 1, 'ténèbres': 0.5, 'fée': 0.5},
            'fée': {'normal': 1, 'combat': 2, 'vol': 1, 'poison': 0.5, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 0.5, 'feu': 0.5, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 2, 'ténèbres': 2, 'fée': 1},
            'objet': {'normal': 1, 'combat': 1, 'vol': 1, 'poison': 1, 'sol': 1, 'roche': 1, 'insecte': 1, 'spectre': 1, 'acier': 1, 'feu': 1, 'eau': 1, 'plante': 1, 'électrique': 1, 'psy': 1, 'glace': 1, 'dragon': 1, 'ténèbres': 1, 'fée': 1}}
            i=typeChart[typeAtt][typeDef]
            return i

    def translateModifPrec(self,stat):
        if stat<=-6:
            return 0.33
        elif stat==-5:
            return 0.37
        elif stat==-4:
            return 0.43
        elif stat==-3:
            return 0.5
        elif stat==-2:
            return 0.6
        elif stat==-1:
            return 0.75
        elif stat==0:
            return 1
        elif stat==1:
            return 1.33
        elif stat==2:
            return 1.66
        elif stat==3:
            return 2
        elif stat==4:
            return 2.33
        elif stat==5:
            return 2.66
        elif stat>=6:
            return 3

    def translateModifStat(self,stat):
        if stat==-6:
            return 0.25
        elif stat==-5:
            return 0.28
        elif stat==-4:
            return 0.33
        elif stat==-3:
            return 0.4
        elif stat==-2:
            return 0.5
        elif stat==-1:
            return 0.66
        elif stat==0:
            return 1
        elif stat==1:
            return 1.5
        elif stat==2:
            return 2
        elif stat==3:
            return 2.5
        elif stat==4:
            return 3
        elif stat==5:
            return 3.5
        elif stat==6:
            return 4
    def translateCrit(self,crit):
        if crit=='normal':
            return 4
        elif crit=='eleve':
            return 12
        elif crit=='tres eleve':
            return 50
        elif crit=='toujours critique':
            return 100

    # Put all stats and statuts
    def putstat(self):
        code = self.ui.codestatut.toPlainText()
        codeSplit = re.split('-',code)
        if len(codeSplit) == 6:
            if(codeSplit[0]!="NA"):
                if(bool(re.search("BRL", codeSplit[0]))):
                    self.ui.effetbrule.setChecked(True)
                if(bool(re.search("PSN", codeSplit[0]))):
                    self.ui.effetpoison.setChecked(True)
                if(bool(re.search("CNF", codeSplit[0]))):
                    self.ui.effetconfus.setChecked(True)
                if(bool(re.search("GEL", codeSplit[0]))):
                    self.ui.effetgel.setChecked(True)
                if(bool(re.search("SLP", codeSplit[0]))):
                    self.ui.effetsommeil.setChecked(True)
                if(bool(re.search("MAL", codeSplit[0]))):
                    self.ui.effetmaledi.setChecked(True)
                if(bool(re.search("PAR", codeSplit[0]))):
                    self.ui.effetpara.setChecked(True)
                if(bool(re.search("ACN", codeSplit[0]))):
                    self.ui.effetattrac.setChecked(True)
                if(bool(re.search("DBS", codeSplit[0]))):
                    self.ui.effetdeso.setChecked(True)
                if(bool(re.search("PIG", codeSplit[0]))):
                    self.ui.effetpiege.setChecked(True)
                if(bool(re.search("IDT", codeSplit[0]))):
                    self.ui.effetident.setChecked(True)
                if(bool(re.search("VA", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(1)
                if(bool(re.search("VB", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(2)
                if(bool(re.search("VC", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(3)
                if(bool(re.search("V1", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(4)
                if(bool(re.search("V2", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(5)
                if(bool(re.search("V3", codeSplit[0]))):
                    self.ui.vampicible.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[0]))):
                    self.ui.modifatt.setValue(1)
                if(bool(re.search("A02", codeSplit[0]))):
                    self.ui.modifatt.setValue(2)
                if(bool(re.search("A03", codeSplit[0]))):
                    self.ui.modifatt.setValue(3)
                if(bool(re.search("A04", codeSplit[0]))):
                    self.ui.modifatt.setValue(4)
                if(bool(re.search("A05", codeSplit[0]))):
                    self.ui.modifatt.setValue(5)
                if(bool(re.search("A06", codeSplit[0]))):
                    self.ui.modifatt.setValue(6)
                if(bool(re.search("A07", codeSplit[0]))):
                    self.ui.modifatt.setValue(-1)
                if(bool(re.search("A08", codeSplit[0]))):
                    self.ui.modifatt.setValue(-2)
                if(bool(re.search("A09", codeSplit[0]))):
                    self.ui.modifatt.setValue(-3)
                if(bool(re.search("A10", codeSplit[0]))):
                    self.ui.modifatt.setValue(-4)
                if(bool(re.search("A11", codeSplit[0]))):
                    self.ui.modifatt.setValue(-5)
                if(bool(re.search("A12", codeSplit[0]))):
                    self.ui.modifatt.setValue(-6)
                if(bool(re.search("D01", codeSplit[0]))):
                    self.ui.modifdefen.setValue(1)
                if(bool(re.search("D02", codeSplit[0]))):
                    self.ui.modifdefen.setValue(2)
                if(bool(re.search("D03", codeSplit[0]))):
                    self.ui.modifdefen.setValue(3)
                if(bool(re.search("D04", codeSplit[0]))):
                    self.ui.modifdefen.setValue(4)
                if(bool(re.search("D05", codeSplit[0]))):
                    self.ui.modifdefen.setValue(5)
                if(bool(re.search("D06", codeSplit[0]))):
                    self.ui.modifdefen.setValue(6)
                if(bool(re.search("D07", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-1)
                if(bool(re.search("D08", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-2)
                if(bool(re.search("D09", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-3)
                if(bool(re.search("D10", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-4)
                if(bool(re.search("D11", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-5)
                if(bool(re.search("D12", codeSplit[0]))):
                    self.ui.modifdefen.setValue(-6)
                if(bool(re.search("S01", codeSplit[0]))):
                    self.ui.modifatts.setValue(1)
                if(bool(re.search("S02", codeSplit[0]))):
                    self.ui.modifatts.setValue(2)
                if(bool(re.search("S03", codeSplit[0]))):
                    self.ui.modifatts.setValue(3)
                if(bool(re.search("S04", codeSplit[0]))):
                    self.ui.modifatts.setValue(4)
                if(bool(re.search("S05", codeSplit[0]))):
                    self.ui.modifatts.setValue(5)
                if(bool(re.search("S06", codeSplit[0]))):
                    self.ui.modifatts.setValue(6)
                if(bool(re.search("S07", codeSplit[0]))):
                    self.ui.modifatts.setValue(-1)
                if(bool(re.search("S08", codeSplit[0]))):
                    self.ui.modifatts.setValue(-2)
                if(bool(re.search("S09", codeSplit[0]))):
                    self.ui.modifatts.setValue(-3)
                if(bool(re.search("S10", codeSplit[0]))):
                    self.ui.modifatts.setValue(-4)
                if(bool(re.search("S11", codeSplit[0]))):
                    self.ui.modifatts.setValue(-5)
                if(bool(re.search("S12", codeSplit[0]))):
                    self.ui.modifatts.setValue(-6)
                if(bool(re.search("F01", codeSplit[0]))):
                    self.ui.modifdefs.setValue(1)
                if(bool(re.search("F02", codeSplit[0]))):
                    self.ui.modifdefs.setValue(2)
                if(bool(re.search("F03", codeSplit[0]))):
                    self.ui.modifdefs.setValue(3)
                if(bool(re.search("F04", codeSplit[0]))):
                    self.ui.modifdefs.setValue(4)
                if(bool(re.search("F05", codeSplit[0]))):
                    self.ui.modifdefs.setValue(5)
                if(bool(re.search("F06", codeSplit[0]))):
                    self.ui.modifdefs.setValue(6)
                if(bool(re.search("F07", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-1)
                if(bool(re.search("F08", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-2)
                if(bool(re.search("F09", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-3)
                if(bool(re.search("F10", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-4)
                if(bool(re.search("F11", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-5)
                if(bool(re.search("F12", codeSplit[0]))):
                    self.ui.modifdefs.setValue(-6)
                if(bool(re.search("T01", codeSplit[0]))):
                    self.ui.modifvit.setValue(1)
                if(bool(re.search("T02", codeSplit[0]))):
                    self.ui.modifvit.setValue(2)
                if(bool(re.search("T03", codeSplit[0]))):
                    self.ui.modifvit.setValue(3)
                if(bool(re.search("T04", codeSplit[0]))):
                    self.ui.modifvit.setValue(4)
                if(bool(re.search("T05", codeSplit[0]))):
                    self.ui.modifvit.setValue(5)
                if(bool(re.search("T06", codeSplit[0]))):
                    self.ui.modifvit.setValue(6)
                if(bool(re.search("T07", codeSplit[0]))):
                    self.ui.modifvit.setValue(-1)
                if(bool(re.search("T08", codeSplit[0]))):
                    self.ui.modifvit.setValue(-2)
                if(bool(re.search("T09", codeSplit[0]))):
                    self.ui.modifvit.setValue(-3)
                if(bool(re.search("T10", codeSplit[0]))):
                    self.ui.modifvit.setValue(-4)
                if(bool(re.search("T11", codeSplit[0]))):
                    self.ui.modifvit.setValue(-5)
                if(bool(re.search("T12", codeSplit[0]))):
                    self.ui.modifvit.setValue(-6)
                if(bool(re.search("E01", codeSplit[0]))):
                    self.ui.modifesquive.setValue(1)
                if(bool(re.search("E02", codeSplit[0]))):
                    self.ui.modifesquive.setValue(2)
                if(bool(re.search("E03", codeSplit[0]))):
                    self.ui.modifesquive.setValue(3)
                if(bool(re.search("E04", codeSplit[0]))):
                    self.ui.modifesquive.setValue(4)
                if(bool(re.search("E05", codeSplit[0]))):
                    self.ui.modifesquive.setValue(5)
                if(bool(re.search("E06", codeSplit[0]))):
                    self.ui.modifesquive.setValue(6)
                if(bool(re.search("E07", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-1)
                if(bool(re.search("E08", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-2)
                if(bool(re.search("E09", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-3)
                if(bool(re.search("E10", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-4)
                if(bool(re.search("E11", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-5)
                if(bool(re.search("E12", codeSplit[0]))):
                    self.ui.modifesquive.setValue(-6)
                if(bool(re.search("P01", codeSplit[0]))):
                    self.ui.modifprec.setValue(1)
                if(bool(re.search("P02", codeSplit[0]))):
                    self.ui.modifprec.setValue(2)
                if(bool(re.search("P03", codeSplit[0]))):
                    self.ui.modifprec.setValue(3)
                if(bool(re.search("P04", codeSplit[0]))):
                    self.ui.modifprec.setValue(4)
                if(bool(re.search("P05", codeSplit[0]))):
                    self.ui.modifprec.setValue(5)
                if(bool(re.search("P06", codeSplit[0]))):
                    self.ui.modifprec.setValue(6)
                if(bool(re.search("P07", codeSplit[0]))):
                    self.ui.modifprec.setValue(-1)
                if(bool(re.search("P08", codeSplit[0]))):
                    self.ui.modifprec.setValue(-2)
                if(bool(re.search("P09", codeSplit[0]))):
                    self.ui.modifprec.setValue(-3)
                if(bool(re.search("P10", codeSplit[0]))):
                    self.ui.modifprec.setValue(-4)
                if(bool(re.search("P11", codeSplit[0]))):
                    self.ui.modifprec.setValue(-5)
                if(bool(re.search("P12", codeSplit[0]))):
                    self.ui.modifprec.setValue(-6)

            if(codeSplit[1]!="NA"):
                if(bool(re.search("BRL", codeSplit[1]))):
                    self.ui.effetbrule_3.setChecked(True)
                if(bool(re.search("PSN", codeSplit[1]))):
                    self.ui.effetpoison_3.setChecked(True)
                if(bool(re.search("CNF", codeSplit[1]))):
                    self.ui.effetconfus_3.setChecked(True)
                if(bool(re.search("GEL", codeSplit[1]))):
                    self.ui.effetgel_3.setChecked(True)
                if(bool(re.search("SLP", codeSplit[1]))):
                    self.ui.effetsommeil_3.setChecked(True)
                if(bool(re.search("MAL", codeSplit[1]))):
                    self.ui.effetmaledi_3.setChecked(True)
                if(bool(re.search("PAR", codeSplit[1]))):
                    self.ui.effetpara_3.setChecked(True)
                if(bool(re.search("ACN", codeSplit[1]))):
                    self.ui.effetattrac_3.setChecked(True)
                if(bool(re.search("DBS", codeSplit[1]))):
                    self.ui.effetdeso_3.setChecked(True)
                if(bool(re.search("PIG", codeSplit[1]))):
                    self.ui.effetpiege_3.setChecked(True)
                if(bool(re.search("IDT", codeSplit[1]))):
                    self.ui.effetident_3.setChecked(True)
                if(bool(re.search("V1", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(1)
                if(bool(re.search("V2", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(2)
                if(bool(re.search("V3", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(3)
                if(bool(re.search("VA", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(4)
                if(bool(re.search("VB", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(5)
                if(bool(re.search("VC", codeSplit[1]))):
                    self.ui.vampicible_3.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(1)
                if(bool(re.search("A02", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(2)
                if(bool(re.search("A03", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(3)
                if(bool(re.search("A04", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(4)
                if(bool(re.search("A05", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(5)
                if(bool(re.search("A06", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(6)
                if(bool(re.search("A07", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-1)
                if(bool(re.search("A08", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-2)
                if(bool(re.search("A09", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-3)
                if(bool(re.search("A10", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-4)
                if(bool(re.search("A11", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-5)
                if(bool(re.search("A12", codeSplit[1]))):
                    self.ui.modifatt_3.setValue(-6)
                if(bool(re.search("D01", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(1)
                if(bool(re.search("D02", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(2)
                if(bool(re.search("D03", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(3)
                if(bool(re.search("D04", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(4)
                if(bool(re.search("D05", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(5)
                if(bool(re.search("D06", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(6)
                if(bool(re.search("D07", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-1)
                if(bool(re.search("D08", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-2)
                if(bool(re.search("D09", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-3)
                if(bool(re.search("D10", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-4)
                if(bool(re.search("D11", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-5)
                if(bool(re.search("D12", codeSplit[1]))):
                    self.ui.modifdefen_3.setValue(-6)
                if(bool(re.search("S01", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(1)
                if(bool(re.search("S02", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(2)
                if(bool(re.search("S03", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(3)
                if(bool(re.search("S04", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(4)
                if(bool(re.search("S05", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(5)
                if(bool(re.search("S06", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(6)
                if(bool(re.search("S07", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-1)
                if(bool(re.search("S08", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-2)
                if(bool(re.search("S09", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-3)
                if(bool(re.search("S10", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-4)
                if(bool(re.search("S11", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-5)
                if(bool(re.search("S12", codeSplit[1]))):
                    self.ui.modifatts_3.setValue(-6)
                if(bool(re.search("F01", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(1)
                if(bool(re.search("F02", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(2)
                if(bool(re.search("F03", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(3)
                if(bool(re.search("F04", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(4)
                if(bool(re.search("F05", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(5)
                if(bool(re.search("F06", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(6)
                if(bool(re.search("F07", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-1)
                if(bool(re.search("F08", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-2)
                if(bool(re.search("F09", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-3)
                if(bool(re.search("F10", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-4)
                if(bool(re.search("F11", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-5)
                if(bool(re.search("F12", codeSplit[1]))):
                    self.ui.modifdefs_3.setValue(-6)
                if(bool(re.search("T01", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(1)
                if(bool(re.search("T02", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(2)
                if(bool(re.search("T03", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(3)
                if(bool(re.search("T04", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(4)
                if(bool(re.search("T05", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(5)
                if(bool(re.search("T06", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(6)
                if(bool(re.search("T07", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-1)
                if(bool(re.search("T08", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-2)
                if(bool(re.search("T09", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-3)
                if(bool(re.search("T10", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-4)
                if(bool(re.search("T11", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-5)
                if(bool(re.search("T12", codeSplit[1]))):
                    self.ui.modifvit_3.setValue(-6)
                if(bool(re.search("E01", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(1)
                if(bool(re.search("E02", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(2)
                if(bool(re.search("E03", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(3)
                if(bool(re.search("E04", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(4)
                if(bool(re.search("E05", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(5)
                if(bool(re.search("E06", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(6)
                if(bool(re.search("E07", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-1)
                if(bool(re.search("E08", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-2)
                if(bool(re.search("E09", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-3)
                if(bool(re.search("E10", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-4)
                if(bool(re.search("E11", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-5)
                if(bool(re.search("E12", codeSplit[1]))):
                    self.ui.modifesquive_3.setValue(-6)
                if(bool(re.search("P01", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(1)
                if(bool(re.search("P02", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(2)
                if(bool(re.search("P03", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(3)
                if(bool(re.search("P04", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(4)
                if(bool(re.search("P05", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(5)
                if(bool(re.search("P06", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(6)
                if(bool(re.search("P07", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-1)
                if(bool(re.search("P08", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-2)
                if(bool(re.search("P09", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-3)
                if(bool(re.search("P10", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-4)
                if(bool(re.search("P11", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-5)
                if(bool(re.search("P12", codeSplit[1]))):
                    self.ui.modifprec_3.setValue(-6)

            if(codeSplit[2]!="NA"):
                if(bool(re.search("BRL", codeSplit[2]))):
                    self.ui.effetbrule_5.setChecked(True)
                if(bool(re.search("PSN", codeSplit[2]))):
                    self.ui.effetpoison_5.setChecked(True)
                if(bool(re.search("CNF", codeSplit[2]))):
                    self.ui.effetconfus_5.setChecked(True)
                if(bool(re.search("GEL", codeSplit[2]))):
                    self.ui.effetgel_5.setChecked(True)
                if(bool(re.search("SLP", codeSplit[2]))):
                    self.ui.effetsommeil_5.setChecked(True)
                if(bool(re.search("MAL", codeSplit[2]))):
                    self.ui.effetmaledi_5.setChecked(True)
                if(bool(re.search("PAR", codeSplit[2]))):
                    self.ui.effetpara_5.setChecked(True)
                if(bool(re.search("ACN", codeSplit[2]))):
                    self.ui.effetattrac_5.setChecked(True)
                if(bool(re.search("DBS", codeSplit[2]))):
                    self.ui.effetdeso_5.setChecked(True)
                if(bool(re.search("PIG", codeSplit[2]))):
                    self.ui.effetpiege_5.setChecked(True)
                if(bool(re.search("IDT", codeSplit[2]))):
                    self.ui.effetident_5.setChecked(True)
                if(bool(re.search("VA", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(1)
                if(bool(re.search("VB", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(2)
                if(bool(re.search("VC", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(3)
                if(bool(re.search("V1", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(4)
                if(bool(re.search("V2", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(5)
                if(bool(re.search("V3", codeSplit[2]))):
                    self.ui.vampicible_5.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(1)
                if(bool(re.search("A02", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(2)
                if(bool(re.search("A03", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(3)
                if(bool(re.search("A04", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(4)
                if(bool(re.search("A05", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(5)
                if(bool(re.search("A06", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(6)
                if(bool(re.search("A07", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-1)
                if(bool(re.search("A08", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-2)
                if(bool(re.search("A09", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-3)
                if(bool(re.search("A10", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-4)
                if(bool(re.search("A11", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-5)
                if(bool(re.search("A12", codeSplit[2]))):
                    self.ui.modifatt_5.setValue(-6)
                if(bool(re.search("D01", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(1)
                if(bool(re.search("D02", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(2)
                if(bool(re.search("D03", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(3)
                if(bool(re.search("D04", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(4)
                if(bool(re.search("D05", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(5)
                if(bool(re.search("D06", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(6)
                if(bool(re.search("D07", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-1)
                if(bool(re.search("D08", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-2)
                if(bool(re.search("D09", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-3)
                if(bool(re.search("D10", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-4)
                if(bool(re.search("D11", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-5)
                if(bool(re.search("D12", codeSplit[2]))):
                    self.ui.modifdefen_5.setValue(-6)
                if(bool(re.search("S01", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(1)
                if(bool(re.search("S02", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(2)
                if(bool(re.search("S03", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(3)
                if(bool(re.search("S04", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(4)
                if(bool(re.search("S05", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(5)
                if(bool(re.search("S06", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(6)
                if(bool(re.search("S07", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-1)
                if(bool(re.search("S08", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-2)
                if(bool(re.search("S09", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-3)
                if(bool(re.search("S10", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-4)
                if(bool(re.search("S11", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-5)
                if(bool(re.search("S12", codeSplit[2]))):
                    self.ui.modifatts_5.setValue(-6)
                if(bool(re.search("F01", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(1)
                if(bool(re.search("F02", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(2)
                if(bool(re.search("F03", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(3)
                if(bool(re.search("F04", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(4)
                if(bool(re.search("F05", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(5)
                if(bool(re.search("F06", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(6)
                if(bool(re.search("F07", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-1)
                if(bool(re.search("F08", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-2)
                if(bool(re.search("F09", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-3)
                if(bool(re.search("F10", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-4)
                if(bool(re.search("F11", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-5)
                if(bool(re.search("F12", codeSplit[2]))):
                    self.ui.modifdefs_5.setValue(-6)
                if(bool(re.search("T01", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(1)
                if(bool(re.search("T02", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(2)
                if(bool(re.search("T03", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(3)
                if(bool(re.search("T04", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(4)
                if(bool(re.search("T05", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(5)
                if(bool(re.search("T06", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(6)
                if(bool(re.search("T07", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-1)
                if(bool(re.search("T08", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-2)
                if(bool(re.search("T09", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-3)
                if(bool(re.search("T10", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-4)
                if(bool(re.search("T11", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-5)
                if(bool(re.search("T12", codeSplit[2]))):
                    self.ui.modifvit_5.setValue(-6)
                if(bool(re.search("E01", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(1)
                if(bool(re.search("E02", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(2)
                if(bool(re.search("E03", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(3)
                if(bool(re.search("E04", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(4)
                if(bool(re.search("E05", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(5)
                if(bool(re.search("E06", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(6)
                if(bool(re.search("E07", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-1)
                if(bool(re.search("E08", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-2)
                if(bool(re.search("E09", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-3)
                if(bool(re.search("E10", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-4)
                if(bool(re.search("E11", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-5)
                if(bool(re.search("E12", codeSplit[2]))):
                    self.ui.modifesquive_5.setValue(-6)
                if(bool(re.search("P01", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(1)
                if(bool(re.search("P02", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(2)
                if(bool(re.search("P03", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(3)
                if(bool(re.search("P04", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(4)
                if(bool(re.search("P05", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(5)
                if(bool(re.search("P06", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(6)
                if(bool(re.search("P07", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-1)
                if(bool(re.search("P08", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-2)
                if(bool(re.search("P09", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-3)
                if(bool(re.search("P10", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-4)
                if(bool(re.search("P11", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-5)
                if(bool(re.search("P12", codeSplit[2]))):
                    self.ui.modifprec_5.setValue(-6)

            if(codeSplit[3]!="NA"):
                if(bool(re.search("BRL", codeSplit[3]))):
                    self.ui.effetbrule_2.setChecked(True)
                if(bool(re.search("PSN", codeSplit[3]))):
                    self.ui.effetpoison_2.setChecked(True)
                if(bool(re.search("CNF", codeSplit[3]))):
                    self.ui.effetconfus_2.setChecked(True)
                if(bool(re.search("GEL", codeSplit[3]))):
                    self.ui.effetgel_2.setChecked(True)
                if(bool(re.search("SLP", codeSplit[3]))):
                    self.ui.effetsommeil_2.setChecked(True)
                if(bool(re.search("MAL", codeSplit[3]))):
                    self.ui.effetmaledi_2.setChecked(True)
                if(bool(re.search("PAR", codeSplit[3]))):
                    self.ui.effetpara_2.setChecked(True)
                if(bool(re.search("ACN", codeSplit[3]))):
                    self.ui.effetattrac_2.setChecked(True)
                if(bool(re.search("DBS", codeSplit[3]))):
                    self.ui.effetdeso_2.setChecked(True)
                if(bool(re.search("PIG", codeSplit[3]))):
                    self.ui.effetpiege_2.setChecked(True)
                if(bool(re.search("IDT", codeSplit[3]))):
                    self.ui.effetident_2.setChecked(True)
                if(bool(re.search("V1", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(1)
                if(bool(re.search("V2", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(2)
                if(bool(re.search("V3", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(3)
                if(bool(re.search("VA", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(4)
                if(bool(re.search("VB", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(5)
                if(bool(re.search("VC", codeSplit[3]))):
                    self.ui.vampicible_2.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(1)
                if(bool(re.search("A02", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(2)
                if(bool(re.search("A03", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(3)
                if(bool(re.search("A04", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(4)
                if(bool(re.search("A05", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(5)
                if(bool(re.search("A06", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(6)
                if(bool(re.search("A07", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-1)
                if(bool(re.search("A08", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-2)
                if(bool(re.search("A09", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-3)
                if(bool(re.search("A10", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-4)
                if(bool(re.search("A11", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-5)
                if(bool(re.search("A12", codeSplit[3]))):
                    self.ui.modifatt_2.setValue(-6)
                if(bool(re.search("D01", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(1)
                if(bool(re.search("D02", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(2)
                if(bool(re.search("D03", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(3)
                if(bool(re.search("D04", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(4)
                if(bool(re.search("D05", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(5)
                if(bool(re.search("D06", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(6)
                if(bool(re.search("D07", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-1)
                if(bool(re.search("D08", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-2)
                if(bool(re.search("D09", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-3)
                if(bool(re.search("D10", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-4)
                if(bool(re.search("D11", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-5)
                if(bool(re.search("D12", codeSplit[3]))):
                    self.ui.modifdefen_2.setValue(-6)
                if(bool(re.search("S01", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(1)
                if(bool(re.search("S02", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(2)
                if(bool(re.search("S03", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(3)
                if(bool(re.search("S04", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(4)
                if(bool(re.search("S05", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(5)
                if(bool(re.search("S06", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(6)
                if(bool(re.search("S07", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-1)
                if(bool(re.search("S08", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-2)
                if(bool(re.search("S09", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-3)
                if(bool(re.search("S10", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-4)
                if(bool(re.search("S11", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-5)
                if(bool(re.search("S12", codeSplit[3]))):
                    self.ui.modifatts_2.setValue(-6)
                if(bool(re.search("F01", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(1)
                if(bool(re.search("F02", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(2)
                if(bool(re.search("F03", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(3)
                if(bool(re.search("F04", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(4)
                if(bool(re.search("F05", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(5)
                if(bool(re.search("F06", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(6)
                if(bool(re.search("F07", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-1)
                if(bool(re.search("F08", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-2)
                if(bool(re.search("F09", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-3)
                if(bool(re.search("F10", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-4)
                if(bool(re.search("F11", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-5)
                if(bool(re.search("F12", codeSplit[3]))):
                    self.ui.modifdefs_2.setValue(-6)
                if(bool(re.search("T01", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(1)
                if(bool(re.search("T02", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(2)
                if(bool(re.search("T03", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(3)
                if(bool(re.search("T04", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(4)
                if(bool(re.search("T05", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(5)
                if(bool(re.search("T06", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(6)
                if(bool(re.search("T07", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-1)
                if(bool(re.search("T08", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-2)
                if(bool(re.search("T09", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-3)
                if(bool(re.search("T10", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-4)
                if(bool(re.search("T11", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-5)
                if(bool(re.search("T12", codeSplit[3]))):
                    self.ui.modifvit_2.setValue(-6)
                if(bool(re.search("E01", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(1)
                if(bool(re.search("E02", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(2)
                if(bool(re.search("E03", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(3)
                if(bool(re.search("E04", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(4)
                if(bool(re.search("E05", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(5)
                if(bool(re.search("E06", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(6)
                if(bool(re.search("E07", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-1)
                if(bool(re.search("E08", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-2)
                if(bool(re.search("E09", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-3)
                if(bool(re.search("E10", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-4)
                if(bool(re.search("E11", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-5)
                if(bool(re.search("E12", codeSplit[3]))):
                    self.ui.modifesquive_2.setValue(-6)
                if(bool(re.search("P01", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(1)
                if(bool(re.search("P02", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(2)
                if(bool(re.search("P03", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(3)
                if(bool(re.search("P04", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(4)
                if(bool(re.search("P05", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(5)
                if(bool(re.search("P06", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(6)
                if(bool(re.search("P07", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-1)
                if(bool(re.search("P08", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-2)
                if(bool(re.search("P09", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-3)
                if(bool(re.search("P10", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-4)
                if(bool(re.search("P11", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-5)
                if(bool(re.search("P12", codeSplit[3]))):
                    self.ui.modifprec_2.setValue(-6)

            if(codeSplit[4]!="NA"):
                if(bool(re.search("BRL", codeSplit[4]))):
                    self.ui.effetbrule_4.setChecked(True)
                if(bool(re.search("PSN", codeSplit[4]))):
                    self.ui.effetpoison_4.setChecked(True)
                if(bool(re.search("CNF", codeSplit[4]))):
                    self.ui.effetconfus_4.setChecked(True)
                if(bool(re.search("GEL", codeSplit[4]))):
                    self.ui.effetgel_4.setChecked(True)
                if(bool(re.search("SLP", codeSplit[4]))):
                    self.ui.effetsommeil_4.setChecked(True)
                if(bool(re.search("MAL", codeSplit[4]))):
                    self.ui.effetmaledi_4.setChecked(True)
                if(bool(re.search("PAR", codeSplit[4]))):
                    self.ui.effetpara_4.setChecked(True)
                if(bool(re.search("ACN", codeSplit[4]))):
                    self.ui.effetattrac_4.setChecked(True)
                if(bool(re.search("DBS", codeSplit[4]))):
                    self.ui.effetdeso_4.setChecked(True)
                if(bool(re.search("PIG", codeSplit[4]))):
                    self.ui.effetpiege_4.setChecked(True)
                if(bool(re.search("IDT", codeSplit[4]))):
                    self.ui.effetident_4.setChecked(True)
                if(bool(re.search("VA", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(1)
                if(bool(re.search("VB", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(2)
                if(bool(re.search("VC", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(3)
                if(bool(re.search("V1", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(4)
                if(bool(re.search("V2", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(5)
                if(bool(re.search("V3", codeSplit[4]))):
                    self.ui.vampicible_4.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(1)
                if(bool(re.search("A02", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(2)
                if(bool(re.search("A03", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(3)
                if(bool(re.search("A04", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(4)
                if(bool(re.search("A05", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(5)
                if(bool(re.search("A06", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(6)
                if(bool(re.search("A07", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-1)
                if(bool(re.search("A08", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-2)
                if(bool(re.search("A09", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-3)
                if(bool(re.search("A10", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-4)
                if(bool(re.search("A11", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-5)
                if(bool(re.search("A12", codeSplit[4]))):
                    self.ui.modifatt_4.setValue(-6)
                if(bool(re.search("D01", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(1)
                if(bool(re.search("D02", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(2)
                if(bool(re.search("D03", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(3)
                if(bool(re.search("D04", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(4)
                if(bool(re.search("D05", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(5)
                if(bool(re.search("D06", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(6)
                if(bool(re.search("D07", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-1)
                if(bool(re.search("D08", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-2)
                if(bool(re.search("D09", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-3)
                if(bool(re.search("D10", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-4)
                if(bool(re.search("D11", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-5)
                if(bool(re.search("D12", codeSplit[4]))):
                    self.ui.modifdefen_4.setValue(-6)
                if(bool(re.search("S01", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(1)
                if(bool(re.search("S02", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(2)
                if(bool(re.search("S03", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(3)
                if(bool(re.search("S04", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(4)
                if(bool(re.search("S05", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(5)
                if(bool(re.search("S06", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(6)
                if(bool(re.search("S07", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-1)
                if(bool(re.search("S08", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-2)
                if(bool(re.search("S09", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-3)
                if(bool(re.search("S10", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-4)
                if(bool(re.search("S11", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-5)
                if(bool(re.search("S12", codeSplit[4]))):
                    self.ui.modifatts_4.setValue(-6)
                if(bool(re.search("F01", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(1)
                if(bool(re.search("F02", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(2)
                if(bool(re.search("F03", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(3)
                if(bool(re.search("F04", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(4)
                if(bool(re.search("F05", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(5)
                if(bool(re.search("F06", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(6)
                if(bool(re.search("F07", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-1)
                if(bool(re.search("F08", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-2)
                if(bool(re.search("F09", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-3)
                if(bool(re.search("F10", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-4)
                if(bool(re.search("F11", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-5)
                if(bool(re.search("F12", codeSplit[4]))):
                    self.ui.modifdefs_4.setValue(-6)
                if(bool(re.search("T01", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(1)
                if(bool(re.search("T02", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(2)
                if(bool(re.search("T03", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(3)
                if(bool(re.search("T04", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(4)
                if(bool(re.search("T05", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(5)
                if(bool(re.search("T06", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(6)
                if(bool(re.search("T07", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-1)
                if(bool(re.search("T08", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-2)
                if(bool(re.search("T09", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-3)
                if(bool(re.search("T10", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-4)
                if(bool(re.search("T11", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-5)
                if(bool(re.search("T12", codeSplit[4]))):
                    self.ui.modifvit_4.setValue(-6)
                if(bool(re.search("E01", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(1)
                if(bool(re.search("E02", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(2)
                if(bool(re.search("E03", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(3)
                if(bool(re.search("E04", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(4)
                if(bool(re.search("E05", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(5)
                if(bool(re.search("E06", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(6)
                if(bool(re.search("E07", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-1)
                if(bool(re.search("E08", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-2)
                if(bool(re.search("E09", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-3)
                if(bool(re.search("E10", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-4)
                if(bool(re.search("E11", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-5)
                if(bool(re.search("E12", codeSplit[4]))):
                    self.ui.modifesquive_4.setValue(-6)
                if(bool(re.search("P01", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(1)
                if(bool(re.search("P02", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(2)
                if(bool(re.search("P03", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(3)
                if(bool(re.search("P04", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(4)
                if(bool(re.search("P05", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(5)
                if(bool(re.search("P06", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(6)
                if(bool(re.search("P07", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-1)
                if(bool(re.search("P08", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-2)
                if(bool(re.search("P09", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-3)
                if(bool(re.search("P10", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-4)
                if(bool(re.search("P11", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-5)
                if(bool(re.search("P12", codeSplit[4]))):
                    self.ui.modifprec_4.setValue(-6)

            if(codeSplit[5]!="NA"):
                if(bool(re.search("BRL", codeSplit[5]))):
                    self.ui.effetbrule_6.setChecked(True)
                if(bool(re.search("PSN", codeSplit[5]))):
                    self.ui.effetpoison_6.setChecked(True)
                if(bool(re.search("CNF", codeSplit[5]))):
                    self.ui.effetconfus_6.setChecked(True)
                if(bool(re.search("GEL", codeSplit[5]))):
                    self.ui.effetgel_6.setChecked(True)
                if(bool(re.search("SLP", codeSplit[5]))):
                    self.ui.effetsommeil_6.setChecked(True)
                if(bool(re.search("MAL", codeSplit[5]))):
                    self.ui.effetmaledi_6.setChecked(True)
                if(bool(re.search("PAR", codeSplit[5]))):
                    self.ui.effetpara_6.setChecked(True)
                if(bool(re.search("ACN", codeSplit[5]))):
                    self.ui.effetattrac_6.setChecked(True)
                if(bool(re.search("DBS", codeSplit[5]))):
                    self.ui.effetdeso_6.setChecked(True)
                if(bool(re.search("PIG", codeSplit[5]))):
                    self.ui.effetpiege_6.setChecked(True)
                if(bool(re.search("IDT", codeSplit[5]))):
                    self.ui.effetident_6.setChecked(True)
                if(bool(re.search("V1", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(1)
                if(bool(re.search("V2", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(2)
                if(bool(re.search("V3", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(3)
                if(bool(re.search("VA", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(4)
                if(bool(re.search("VB", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(5)
                if(bool(re.search("VC", codeSplit[5]))):
                    self.ui.vampicible_6.setCurrentIndex(6)

                if(bool(re.search("A01", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(1)
                if(bool(re.search("A02", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(2)
                if(bool(re.search("A03", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(3)
                if(bool(re.search("A04", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(4)
                if(bool(re.search("A05", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(5)
                if(bool(re.search("A06", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(6)
                if(bool(re.search("A07", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-1)
                if(bool(re.search("A08", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-2)
                if(bool(re.search("A09", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-3)
                if(bool(re.search("A10", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-4)
                if(bool(re.search("A11", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-5)
                if(bool(re.search("A12", codeSplit[5]))):
                    self.ui.modifatt_6.setValue(-6)
                if(bool(re.search("D01", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(1)
                if(bool(re.search("D02", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(2)
                if(bool(re.search("D03", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(3)
                if(bool(re.search("D04", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(4)
                if(bool(re.search("D05", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(5)
                if(bool(re.search("D06", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(6)
                if(bool(re.search("D07", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-1)
                if(bool(re.search("D08", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-2)
                if(bool(re.search("D09", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-3)
                if(bool(re.search("D10", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-4)
                if(bool(re.search("D11", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-5)
                if(bool(re.search("D12", codeSplit[5]))):
                    self.ui.modifdefen_6.setValue(-6)
                if(bool(re.search("S01", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(1)
                if(bool(re.search("S02", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(2)
                if(bool(re.search("S03", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(3)
                if(bool(re.search("S04", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(4)
                if(bool(re.search("S05", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(5)
                if(bool(re.search("S06", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(6)
                if(bool(re.search("S07", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-1)
                if(bool(re.search("S08", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-2)
                if(bool(re.search("S09", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-3)
                if(bool(re.search("S10", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-4)
                if(bool(re.search("S11", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-5)
                if(bool(re.search("S12", codeSplit[5]))):
                    self.ui.modifatts_6.setValue(-6)
                if(bool(re.search("F01", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(1)
                if(bool(re.search("F02", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(2)
                if(bool(re.search("F03", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(3)
                if(bool(re.search("F04", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(4)
                if(bool(re.search("F05", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(5)
                if(bool(re.search("F06", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(6)
                if(bool(re.search("F07", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-1)
                if(bool(re.search("F08", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-2)
                if(bool(re.search("F09", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-3)
                if(bool(re.search("F10", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-4)
                if(bool(re.search("F11", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-5)
                if(bool(re.search("F12", codeSplit[5]))):
                    self.ui.modifdefs_6.setValue(-6)
                if(bool(re.search("T01", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(1)
                if(bool(re.search("T02", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(2)
                if(bool(re.search("T03", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(3)
                if(bool(re.search("T04", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(4)
                if(bool(re.search("T05", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(5)
                if(bool(re.search("T06", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(6)
                if(bool(re.search("T07", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-1)
                if(bool(re.search("T08", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-2)
                if(bool(re.search("T09", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-3)
                if(bool(re.search("T10", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-4)
                if(bool(re.search("T11", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-5)
                if(bool(re.search("T12", codeSplit[5]))):
                    self.ui.modifvit_6.setValue(-6)
                if(bool(re.search("E01", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(1)
                if(bool(re.search("E02", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(2)
                if(bool(re.search("E03", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(3)
                if(bool(re.search("E04", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(4)
                if(bool(re.search("E05", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(5)
                if(bool(re.search("E06", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(6)
                if(bool(re.search("E07", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-1)
                if(bool(re.search("E08", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-2)
                if(bool(re.search("E09", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-3)
                if(bool(re.search("E10", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-4)
                if(bool(re.search("E11", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-5)
                if(bool(re.search("E12", codeSplit[5]))):
                    self.ui.modifesquive_6.setValue(-6)
                if(bool(re.search("P01", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(1)
                if(bool(re.search("P02", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(2)
                if(bool(re.search("P03", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(3)
                if(bool(re.search("P04", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(4)
                if(bool(re.search("P05", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(5)
                if(bool(re.search("P06", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(6)
                if(bool(re.search("P07", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-1)
                if(bool(re.search("P08", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-2)
                if(bool(re.search("P09", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-3)
                if(bool(re.search("P10", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-4)
                if(bool(re.search("P11", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-5)
                if(bool(re.search("P12", codeSplit[5]))):
                    self.ui.modifprec_6.setValue(-6)

        elif len(codeSplit) < 6:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(codeSplit) > 6:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()


    # Take custom entry on pokemon 1 and put it in boxes + does query on pkmon and attack
    def SplitCustom(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : 0000 - Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer.setText(datasplit[0])
            self.ui.pokename.setText(datasplit[1])
            self.ui.pokelvl.setText(datasplit[3])
            self.ui.pvcurrent.setText(datasplit[4])
            self.ui.pvtotal.setText(datasplit[5])
            self.ui.att.setText(datasplit2[0])
            self.ui.defen.setText(datasplit2[1])
            self.ui.atts.setText(datasplit2[2])
            self.ui.defs.setText(datasplit2[3])
            self.ui.vit.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque.setText(correctname)
            else:
                self.ui.attaque.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke.setText(correctpkmon)
            else:
                self.ui.poke.setText(datasplit[2])
            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            if pokedata == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                self.ui.poketype1.setText(pokedata[2])
                self.ui.poketype2.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype.setText(attackdata[2])
                self.ui.attaqueclasse.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss.setText('-')
                else:
                    self.ui.attaquepuiss.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec.setText('-')
                else:
                    self.ui.attaqueprec.setText(str(attackdata[4]))
                self.ui.attaqueprio.setText(str(attackdata[5]))
                self.ui.cible.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible.addItem("1")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible.addItems(["A","B","C","2","3"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1.toPlainText()!="spectre" and self.ui.poketype2.toPlainText()!="spectre":
                      self.ui.cible.addItem("1")
                    else:
                      self.ui.cible.addItems(["A","B","C"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible.addItems(["2","3"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible.addItems(["1","2","3"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible.addItems(["A","B","C","1","2","3"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible.addItem("/")
            self.ui.attackdex.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    # Take custom entry on pokemon 2 and put it in boxes + does query on pkmon and attack
    def SplitCustom2(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar_2.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer_2.setText(datasplit[0])
            self.ui.pokename_2.setText(datasplit[1])
            self.ui.pokelvl_2.setText(datasplit[3])
            self.ui.pvcurrent_2.setText(datasplit[4])
            self.ui.pvtotal_2.setText(datasplit[5])
            self.ui.att_2.setText(datasplit2[0])
            self.ui.defen_2.setText(datasplit2[1])
            self.ui.atts_2.setText(datasplit2[2])
            self.ui.defs_2.setText(datasplit2[3])
            self.ui.vit_2.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque_2.setText(correctname)
            else:
                self.ui.attaque_2.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke_2.setText(correctpkmon)
            else:
                self.ui.poke_2.setText(datasplit[2])

            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            self.ui.poketype1_2.setText(pokedata[2])
            self.ui.poketype2_2.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype_2.setText(attackdata[2])
                self.ui.attaqueclasse_2.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss_2.setText('-')
                else:
                    self.ui.attaquepuiss_2.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec_2.setText('-')
                else:
                    self.ui.attaqueprec_2.setText(str(attackdata[4]))
                self.ui.attaqueprio_2.setText(str(attackdata[5]))
                self.ui.cible_2.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible_2.addItem("A")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible_2.addItems(["1","2","3","B","C"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible_2.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible_2.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible_2.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1_2.toPlainText()!="spectre" and self.ui.poketype2_2.toPlainText()!="spectre":
                      self.ui.cible_2.addItem("A")
                    else:
                      self.ui.cible_2.addItems(["1","2","3"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible_2.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible_2.addItems(["B","C"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible_2.addItems(["A","B","C"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible_2.addItems(["1","2","3","A","B","C"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible_2.addItem("/")

            self.ui.attackdex_2.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_2.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl_2.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_2.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_2.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    def SplitCustom3(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar_3.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer_3.setText(datasplit[0])
            self.ui.pokename_3.setText(datasplit[1])
            self.ui.pokelvl_3.setText(datasplit[3])
            self.ui.pvcurrent_3.setText(datasplit[4])
            self.ui.pvtotal_3.setText(datasplit[5])
            self.ui.att_3.setText(datasplit2[0])
            self.ui.defen_3.setText(datasplit2[1])
            self.ui.atts_3.setText(datasplit2[2])
            self.ui.defs_3.setText(datasplit2[3])
            self.ui.vit_3.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque_3.setText(correctname)
            else:
                self.ui.attaque_3.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke_3.setText(correctpkmon)
            else:
                self.ui.poke_3.setText(datasplit[2])

            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            self.ui.poketype1_3.setText(pokedata[2])
            self.ui.poketype2_3.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype_3.setText(attackdata[2])
                self.ui.attaqueclasse_3.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss_3.setText('-')
                else:
                    self.ui.attaquepuiss_3.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec_3.setText('-')
                else:
                    self.ui.attaqueprec_3.setText(str(attackdata[4]))
                self.ui.attaqueprio_3.setText(str(attackdata[5]))
                self.ui.cible_3.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible_3.addItem("2")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible_3.addItems(["A","B","C","1","3"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible_3.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible_3.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible_3.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1_3.toPlainText()!="spectre" and self.ui.poketype2_3.toPlainText()!="spectre":
                      self.ui.cible_3.addItem("2")
                    else:
                      self.ui.cible_3.addItems(["A","B","C"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible_3.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible_3.addItems(["1","3"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible_3.addItems(["1","2","3"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible_3.addItems(["A","B","C","1","2","3"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible_3.addItem("/")

            self.ui.attackdex_3.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_3.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl_3.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_3.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_3.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    def SplitCustom4(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar_4.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer_4.setText(datasplit[0])
            self.ui.pokename_4.setText(datasplit[1])
            self.ui.pokelvl_4.setText(datasplit[3])
            self.ui.pvcurrent_4.setText(datasplit[4])
            self.ui.pvtotal_4.setText(datasplit[5])
            self.ui.att_4.setText(datasplit2[0])
            self.ui.defen_4.setText(datasplit2[1])
            self.ui.atts_4.setText(datasplit2[2])
            self.ui.defs_4.setText(datasplit2[3])
            self.ui.vit_4.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque_4.setText(correctname)
            else:
                self.ui.attaque_4.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke_4.setText(correctpkmon)
            else:
                self.ui.poke_4.setText(datasplit[2])

            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            self.ui.poketype1_4.setText(pokedata[2])
            self.ui.poketype2_4.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype_4.setText(attackdata[2])
                self.ui.attaqueclasse_4.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss_4.setText('-')
                else:
                    self.ui.attaquepuiss_4.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec_4.setText('-')
                else:
                    self.ui.attaqueprec_4.setText(str(attackdata[4]))
                self.ui.attaqueprio_4.setText(str(attackdata[5]))
                self.ui.cible_4.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible_4.addItem("B")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible_4.addItems(["1","2","3","A","C"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible_4.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible_4.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible_4.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1_4.toPlainText()!="spectre" and self.ui.poketype2_4.toPlainText()!="spectre":
                      self.ui.cible_4.addItem("B")
                    else:
                      self.ui.cible_4.addItems(["1","2","3"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible_4.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible_4.addItems(["A","C"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible_4.addItems(["A","B","C"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible_4.addItems(["1","2","3","A","B","C"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible_4.addItem("/")

            self.ui.attackdex_4.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_4.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl_4.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_4.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_4.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    def SplitCustom5(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar_5.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer_5.setText(datasplit[0])
            self.ui.pokename_5.setText(datasplit[1])
            self.ui.pokelvl_5.setText(datasplit[3])
            self.ui.pvcurrent_5.setText(datasplit[4])
            self.ui.pvtotal_5.setText(datasplit[5])
            self.ui.att_5.setText(datasplit2[0])
            self.ui.defen_5.setText(datasplit2[1])
            self.ui.atts_5.setText(datasplit2[2])
            self.ui.defs_5.setText(datasplit2[3])
            self.ui.vit_5.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque_5.setText(correctname)
            else:
                self.ui.attaque_5.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke_5.setText(correctpkmon)
            else:
                self.ui.poke_5.setText(datasplit[2])

            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            self.ui.poketype1_5.setText(pokedata[2])
            self.ui.poketype2_5.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype_5.setText(attackdata[2])
                self.ui.attaqueclasse_5.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss_5.setText('-')
                else:
                    self.ui.attaquepuiss_5.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec_5.setText('-')
                else:
                    self.ui.attaqueprec_5.setText(str(attackdata[4]))
                self.ui.attaqueprio_5.setText(str(attackdata[5]))
                self.ui.cible_5.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible_5.addItem("3")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible_5.addItems(["A","B","C","1","2"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible_5.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible_5.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible_5.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1_5.toPlainText()!="spectre" and self.ui.poketype2_5.toPlainText()!="spectre":
                      self.ui.cible_5.addItem("3")
                    else:
                      self.ui.cible_5.addItems(["A","B","C"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible_5.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible_5.addItems(["1","2"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible_5.addItems(["1","2","3"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible_5.addItems(["A","B","C","1","2","3"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible_5.addItem("/")
            self.ui.attackdex_5.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_5.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl_5.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_5.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_5.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    def SplitCustom6(self):
        all_attaques=self.init_index_attaques() # get index of attack list to correct errors
        all_pokemon=self.init_index_pkmon()
        databar = self.ui.customdatabar_6.toPlainText()
        datasplit = re.split('/| - ',databar)
        if len(datasplit) >= 6:
            datasplit2 = re.split('x',datasplit[6])
        if len(datasplit) == 8 and len(datasplit2) == 5:
            #  ex : Patate - Salamèche - 30 - 20/40 - 10x20x10x20x8 - Charge
            try:
                correctname=self.attaque_match(datasplit[7],all_attaques)
            except KeyError:
                correctname="error"
            try:
                correctpkmon=self.attaque_match(datasplit[2],all_pokemon)
            except KeyError:
                correctpkmon="error"
            self.ui.trainer_6.setText(datasplit[0])
            self.ui.pokename_6.setText(datasplit[1])
            self.ui.pokelvl_6.setText(datasplit[3])
            self.ui.pvcurrent_6.setText(datasplit[4])
            self.ui.pvtotal_6.setText(datasplit[5])
            self.ui.att_6.setText(datasplit2[0])
            self.ui.defen_6.setText(datasplit2[1])
            self.ui.atts_6.setText(datasplit2[2])
            self.ui.defs_6.setText(datasplit2[3])
            self.ui.vit_6.setText(datasplit2[4])
            if correctname!="error":
                self.ui.attaque_6.setText(correctname)
            else:
                self.ui.attaque_6.setText(datasplit[7])
            if correctpkmon!="error":
                self.ui.poke_6.setText(correctpkmon)
            else:
                self.ui.poke_6.setText(datasplit[2])

            # query poke to get type
            c.execute('SELECT * FROM pokemons WHERE nom=?',(correctpkmon,))
            pokedata = c.fetchone()
            self.ui.poketype1_6.setText(pokedata[2])
            self.ui.poketype2_6.setText(pokedata[3])
            # querry to get stats attack
            c.execute('SELECT * FROM attaques WHERE nom=?',(correctname,))
            attackdata = c.fetchone()
            if attackdata == None:
                msgBox2 = QMessageBox()
                msgBox2.setText('Attaque inconnue')
                msgBox2.exec_()
            else:
                self.ui.attaquetype_6.setText(attackdata[2])
                self.ui.attaqueclasse_6.setText(attackdata[6])
                if attackdata[3] == None:
                    self.ui.attaquepuiss_6.setText('-')
                else:
                    self.ui.attaquepuiss_6.setText(str(attackdata[3]))
                if attackdata[4] == 'echoue jamais':
                    self.ui.attaqueprec_6.setText('-')
                else:
                    self.ui.attaqueprec_6.setText(str(attackdata[4]))
                self.ui.attaqueprio_6.setText(str(attackdata[5]))
                self.ui.cible_6.clear()
                if attackdata[15]=="lanceur":
                    self.ui.cible_6.addItem("C")
                elif attackdata[15]=="au choix sauf lanceur":
                    self.ui.cible_6.addItems(["1","2","3","A","B"])
                elif attackdata[15]=="tous les adversaires":
                    self.ui.cible_6.addItem("Adversaires")
                elif attackdata[15]=="tous sauf lanceur":
                    self.ui.cible_6.addItem("Tous")
                elif attackdata[15]=="random":
                    self.ui.cible_6.addItem("Aléatoire")
                elif attackdata[15]=="truc spécifique":
                    if attackdata[1]=="Malédiction" and self.ui.poketype1_6.toPlainText()!="spectre" and self.ui.poketype2_6.toPlainText()!="spectre":
                      self.ui.cible_6.addItem("C")
                    else:
                      self.ui.cible_6.addItems(["1","2","3"])
                elif attackdata[15]=="utilisateur et alliés":
                    self.ui.cible_6.addItem("Team") # code global heal effect directly in fight ?
                elif attackdata[15]=="allié": # not doing anything, manual handle
                    self.ui.cible_6.addItems(["A","B"])
                elif attackdata[15]=="lanceur ou allié": # not doing anything, manual handle
                    self.ui.cible_6.addItems(["A","B","C"])
                elif attackdata[15]=="au choix": # not doing anything, manual handle
                    self.ui.cible_6.addItems(["1","2","3","A","B","C"])
                elif attackdata[15]=="tous" or attackdata[15]=="tous les alliés": # not doing anything, manual handle
                    self.ui.cible_6.addItem("/")

            self.ui.attackdex_6.clear()
            c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_6.toPlainText(),))
            idpoke = c.fetchone()
            if idpoke == None:
                msgBox1 = QMessageBox()
                msgBox1.setText('Nom de pokemon inconnu')
                msgBox1.exec_()
            else:
                idpoke =  str(idpoke[0])
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.pokelvl_6.toPlainText()),'niveau','preevolution'))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_6.addItem(attaque_nom)
                c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
                for row in c.fetchall():
                    attaque_id=row[0]
                    c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                    attaque_nom=c.fetchone()[0]
                    self.ui.attackdex_6.addItem('CT- '+attaque_nom)

        elif len(datasplit) < 8 or len(datasplit2) < 5:
            msgBox1 = QMessageBox()
            msgBox1.setText("Attention, il manque des choses !")
            msgBox1.exec_()
        elif len(datasplit) > 8 or len(datasplit2) > 5:
            msgBox2 = QMessageBox()
            msgBox2.setText("Attention, il y a des choses en trop !")
            msgBox2.exec_()

    def generatePokemon(self):
        self.ui.attackdex.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke.setText(correctpkmon)
        else:
            self.ui.poke.setText(self.ui.pokedex.currentText())
        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke =  str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon inconnu')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl.value() for x in stats]
            distrib=2*self.ui.spinlvl.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer.setText("0000")
            self.ui.pokename.setText(pokestat[1])
            self.ui.poke.setText(pokestat[1])
            self.ui.pokelvl.setText(str(self.ui.spinlvl.value()))
            self.ui.pvcurrent.setText(str(updatepv))
            self.ui.pvtotal.setText(str(updatepv))
            self.ui.att.setText(str(upstats[0]))
            self.ui.defen.setText(str(upstats[1]))
            self.ui.atts.setText(str(upstats[2]))
            self.ui.defs.setText(str(upstats[3]))
            self.ui.vit.setText(str(upstats[4]))
            self.ui.poketype1.setText(pokestat[2])
            self.ui.poketype2.setText(pokestat[3])

    def generatePokemon2(self):
        self.ui.attackdex_2.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex_2.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke_2.setText(correctpkmon)
        else:
            self.ui.poke_2.setText(self.ui.pokedex_2.currentText())

        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_2.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke = str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl_2.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_2.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_2.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke_2.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon introuvable')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl_2.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl_2.value() for x in stats]
            distrib=2*self.ui.spinlvl_2.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer_2.setText("0000")
            self.ui.pokename_2.setText(pokestat[1])
            self.ui.poke_2.setText(pokestat[1])
            self.ui.pokelvl_2.setText(str(self.ui.spinlvl_2.value()))
            self.ui.pvcurrent_2.setText(str(updatepv))
            self.ui.pvtotal_2.setText(str(updatepv))
            self.ui.att_2.setText(str(upstats[0]))
            self.ui.defen_2.setText(str(upstats[1]))
            self.ui.atts_2.setText(str(upstats[2]))
            self.ui.defs_2.setText(str(upstats[3]))
            self.ui.vit_2.setText(str(upstats[4]))
            self.ui.poketype1_2.setText(pokestat[2])
            self.ui.poketype2_2.setText(pokestat[3])

    def generatePokemon3(self):
        self.ui.attackdex_3.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex_3.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke_3.setText(correctpkmon)
        else:
            self.ui.poke_3.setText(self.ui.pokedex_3.currentText())

        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_3.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke = str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl_3.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_3.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_3.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke_3.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon introuvable')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl_3.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl_3.value() for x in stats]
            distrib=2*self.ui.spinlvl_3.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer_3.setText("0000")
            self.ui.pokename_3.setText(pokestat[1])
            self.ui.poke_3.setText(pokestat[1])
            self.ui.pokelvl_3.setText(str(self.ui.spinlvl_3.value()))
            self.ui.pvcurrent_3.setText(str(updatepv))
            self.ui.pvtotal_3.setText(str(updatepv))
            self.ui.att_3.setText(str(upstats[0]))
            self.ui.defen_3.setText(str(upstats[1]))
            self.ui.atts_3.setText(str(upstats[2]))
            self.ui.defs_3.setText(str(upstats[3]))
            self.ui.vit_3.setText(str(upstats[4]))
            self.ui.poketype1_3.setText(pokestat[2])
            self.ui.poketype2_3.setText(pokestat[3])

    def generatePokemon4(self):
        self.ui.attackdex_4.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex_4.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke_4.setText(correctpkmon)
        else:
            self.ui.poke_4.setText(self.ui.pokedex_4.currentText())

        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_4.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke = str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl_4.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_4.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_4.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke_4.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon introuvable')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl_4.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl_4.value() for x in stats]
            distrib=2*self.ui.spinlvl_4.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer_4.setText("0000")
            self.ui.pokename_4.setText(pokestat[1])
            self.ui.poke_4.setText(pokestat[1])
            self.ui.pokelvl_4.setText(str(self.ui.spinlvl_4.value()))
            self.ui.pvcurrent_4.setText(str(updatepv))
            self.ui.pvtotal_4.setText(str(updatepv))
            self.ui.att_4.setText(str(upstats[0]))
            self.ui.defen_4.setText(str(upstats[1]))
            self.ui.atts_4.setText(str(upstats[2]))
            self.ui.defs_4.setText(str(upstats[3]))
            self.ui.vit_4.setText(str(upstats[4]))
            self.ui.poketype1_4.setText(pokestat[2])
            self.ui.poketype2_4.setText(pokestat[3])

    def generatePokemon5(self):
        self.ui.attackdex_5.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex_5.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke_5.setText(correctpkmon)
        else:
            self.ui.poke_5.setText(self.ui.pokedex_5.currentText())

        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_5.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke = str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl_5.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_5.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_5.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke_5.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon introuvable')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl_5.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl_5.value() for x in stats]
            distrib=2*self.ui.spinlvl_5.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer_5.setText("0000")
            self.ui.pokename_5.setText(pokestat[1])
            self.ui.poke_5.setText(pokestat[1])
            self.ui.pokelvl_5.setText(str(self.ui.spinlvl_5.value()))
            self.ui.pvcurrent_5.setText(str(updatepv))
            self.ui.pvtotal_5.setText(str(updatepv))
            self.ui.att_5.setText(str(upstats[0]))
            self.ui.defen_5.setText(str(upstats[1]))
            self.ui.atts_5.setText(str(upstats[2]))
            self.ui.defs_5.setText(str(upstats[3]))
            self.ui.vit_5.setText(str(upstats[4]))
            self.ui.poketype1_5.setText(pokestat[2])
            self.ui.poketype2_5.setText(pokestat[3])

    def generatePokemon6(self):
        self.ui.attackdex_6.clear()
        all_pokemon=self.init_index_pkmon()
        try:
            correctpkmon=self.attaque_match(self.ui.pokedex_6.currentText(),all_pokemon)
        except KeyError:
            correctpkmon="error"
        if correctpkmon!="error":
            self.ui.poke_6.setText(correctpkmon)
        else:
            self.ui.poke_6.setText(self.ui.pokedex_6.currentText())

        c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_6.toPlainText(),))
        idpoke = c.fetchone()
        if idpoke == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Nom de pokemon inconnu')
            msgBox1.exec_()
        else:
            idpoke = str(idpoke[0])
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau<=? AND (methode=? OR methode=?)',(idpoke,str(self.ui.spinlvl_6.value()),'niveau','preevolution'))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_6.addItem(attaque_nom)
            c.execute('SELECT attaque_id FROM apprentissage WHERE pokemon_id=? AND niveau=0',(idpoke,))
            for row in c.fetchall():
                attaque_id=row[0]
                c.execute('SELECT nom FROM attaques WHERE id='+str(attaque_id))
                attaque_nom=c.fetchone()[0]
                self.ui.attackdex_6.addItem('CT- '+attaque_nom)

        c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.poke_6.toPlainText(),))
        pokestat = c.fetchone()
        if pokestat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Pokemon introuvable')
            msgBox1.exec_()
        else:
            updatepv=pokestat[4]+(2*self.ui.spinlvl_6.value())
            stats=[pokestat[5],pokestat[6],pokestat[7],pokestat[8],pokestat[9]]
            upstats1=[x+self.ui.spinlvl_6.value() for x in stats]
            distrib=2*self.ui.spinlvl_6.value()
            toall=int(distrib/5)
            toadd=distrib % 5
            upstats=[x+toall for x in upstats1]
            randomstatup=random.randint(0,4)
            upstats[randomstatup]=upstats[randomstatup]+toadd
            #maxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #stats[maxindex]=0
            #secmaxindex=random.choice([i for i, j in enumerate(stats) if j == max(stats)])
            #upstats[maxindex]=upstats[maxindex]+self.ui.spinlvl.value()
            #upstats[secmaxindex]=upstats[secmaxindex]+self.ui.spinlvl.value()

            self.ui.trainer_6.setText("0000")
            self.ui.pokename_6.setText(pokestat[1])
            self.ui.poke_6.setText(pokestat[1])
            self.ui.pokelvl_6.setText(str(self.ui.spinlvl_6.value()))
            self.ui.pvcurrent_6.setText(str(updatepv))
            self.ui.pvtotal_6.setText(str(updatepv))
            self.ui.att_6.setText(str(upstats[0]))
            self.ui.defen_6.setText(str(upstats[1]))
            self.ui.atts_6.setText(str(upstats[2]))
            self.ui.defs_6.setText(str(upstats[3]))
            self.ui.vit_6.setText(str(upstats[4]))
            self.ui.poketype1_6.setText(pokestat[2])
            self.ui.poketype2_6.setText(pokestat[3])

    def generateattack(self):
        self.ui.attaque.setText(self.ui.attackdex.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat = c.fetchone()
        if attackstat == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype.setText(attackstat[2])
            self.ui.attaqueclasse.setText(attackstat[6])
            if attackstat[3] == None:
                self.ui.attaquepuiss.setText('-')
            else:
                self.ui.attaquepuiss.setText(str(attackstat[3]))
            if attackstat[4] == 'echoue jamais':
                self.ui.attaqueprec.setText('-')
            else:
                self.ui.attaqueprec.setText(str(attackstat[4]))
            self.ui.attaqueprio.setText(str(attackstat[5]))

            self.ui.cible.clear()
            if attackstat[15]=="lanceur":
                self.ui.cible.addItem("1")
            elif attackstat[15]=="au choix sauf lanceur":
                self.ui.cible.addItems(["A","B","C","2","3"])
            elif attackstat[15]=="tous les adversaires":
                self.ui.cible.addItem("Adversaires")
            elif attackstat[15]=="tous sauf lanceur":
                self.ui.cible.addItem("Tous")
            elif attackstat[15]=="random":
                self.ui.cible.addItem("Aléatoire")
            elif attackstat[15]=="truc spécifique":
                if attackstat[1]=="Malédiction" and self.ui.poketype1.toPlainText()!="spectre" and self.ui.poketype2.toPlainText()!="spectre":
                  self.ui.cible.addItem("1")
                else:
                  self.ui.cible.addItems(["A","B","C"])
            elif attackstat[15]=="utilisateur et alliés":
                self.ui.cible.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat[15]=="allié": # not doing anything, manual handle
                self.ui.cible.addItems(["2","3"])
            elif attackstat[15]=="lanceur ou allié": # not doing anything, manual handle
                self.ui.cible.addItems(["1","2","3"])
            elif attackstat[15]=="au choix": # not doing anything, manual handle
                self.ui.cible.addItems(["A","B","C","1","2","3"])
            elif attackstat[15]=="tous" or attackstat[15]=="tous les alliés": # not doing anything, manual handle
                self.ui.cible.addItem("/")

    def generateattack2(self):
        self.ui.attaque_2.setText(self.ui.attackdex_2.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex_2.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat2 = c.fetchone()
        if attackstat2 == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype_2.setText(attackstat2[2])
            self.ui.attaqueclasse_2.setText(attackstat2[6])
            if attackstat2[3] == None:
                self.ui.attaquepuiss_2.setText('-')
            else:
                self.ui.attaquepuiss_2.setText(str(attackstat2[3]))
            if attackstat2[4] == 'echoue jamais':
                self.ui.attaqueprec_2.setText('-')
            else:
                self.ui.attaqueprec_2.setText(str(attackstat2[4]))
            self.ui.attaqueprio_2.setText(str(attackstat2[5]))
            self.ui.cible_2.clear()
            if attackstat2[15]=="lanceur":
                self.ui.cible_2.addItem("A")
            elif attackstat2[15]=="au choix sauf lanceur":
                self.ui.cible_2.addItems(["1","2","3","B","C"])
            elif attackstat2[15]=="tous les adversaires":
                self.ui.cible_2.addItem("Adversaires")
            elif attackstat2[15]=="tous sauf lanceur":
                self.ui.cible_2.addItem("Tous")
            elif attackstat2[15]=="random":
                self.ui.cible_2.addItem("Aléatoire")
            elif attackstat2[15]=="truc spécifique":
                if attackstat2[1]=="Malédiction" and self.ui.poketype1_2.toPlainText()!="spectre" and self.ui.poketype2_2.toPlainText()!="spectre":
                  self.ui.cible_2.addItem("A")
                else:
                  self.ui.cible_2.addItems(["1","2","3"])
            elif attackstat2[15]=="utilisateur et alliés":
                self.ui.cible_2.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat2[15]=="allié": # not doing anything, manual handle
                self.ui.cible_2.addItems(["B","C"])
            elif attackstat2[15]=="lanceur ou allié": # not doing anything, manual handle
                self.ui.cible_2.addItems(["A","B","C"])
            elif attackstat2[15]=="au choix": # not doing anything, manual handle
                self.ui.cible_2.addItems(["1","2","3","A","B","C"])
            elif attackstat2[15]=="tous" or attackstat2[15]=="tous les alliés": # not doing anything, manual handle
                self.ui.cible_2.addItem("/")

    def generateattack3(self):
        self.ui.attaque_3.setText(self.ui.attackdex_3.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex_3.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat3 = c.fetchone()
        if attackstat3 == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype_3.setText(attackstat3[2])
            self.ui.attaqueclasse_3.setText(attackstat3[6])
            if attackstat3[3] == None:
                self.ui.attaquepuiss_3.setText('-')
            else:
                self.ui.attaquepuiss_3.setText(str(attackstat3[3]))
            if attackstat3[4] == 'echoue jamais':
                self.ui.attaqueprec_3.setText('-')
            else:
                self.ui.attaqueprec_3.setText(str(attackstat3[4]))
            self.ui.attaqueprio_3.setText(str(attackstat3[5]))
            self.ui.cible_3.clear()
            if attackstat3[15]=="lanceur":
                self.ui.cible_3.addItem("2")
            elif attackstat3[15]=="au choix sauf lanceur":
                self.ui.cible_3.addItems(["A","B","C","1","3"])
            elif attackstat3[15]=="tous les adversaires":
                self.ui.cible_3.addItem("Adversaires")
            elif attackstat3[15]=="tous sauf lanceur":
                self.ui.cible_3.addItem("Tous")
            elif attackstat3[15]=="random":
                self.ui.cible_3.addItem("Aléatoire")
            elif attackstat3[15]=="truc spécifique":
                if attackstat3[1]=="Malédiction" and self.ui.poketype1_3.toPlainText()!="spectre" and self.ui.poketype2_3.toPlainText()!="spectre":
                  self.ui.cible_3.addItem("2")
                else:
                  self.ui.cible_3.addItems(["A","B","C"])
            elif attackstat3[15]=="utilisateur et alliés":
                self.ui.cible_3.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat3[15]=="allié": # not doing anything, manual handle
                self.ui.cible_3.addItems(["1","3"])
            elif attackstat3[15]=="lanceur ou allié": # not doing anything, manual handle
                self.ui.cible_3.addItems(["1","2","3"])
            elif attackstat3[15]=="au choix": # not doing anything, manual handle
                self.ui.cible_3.addItems(["A","B","C","1","2","3"])
            elif attackstat3[15]=="tous" or attackstat3[15]=="tous les alliés": # not doing anything, manual handle
                self.ui.cible_3.addItem("/")

    def generateattack4(self):
        self.ui.attaque_4.setText(self.ui.attackdex_4.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex_4.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat4 = c.fetchone()
        if attackstat4 == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype_4.setText(attackstat4[2])
            self.ui.attaqueclasse_4.setText(attackstat4[6])
            if attackstat4[3] == None:
                self.ui.attaquepuiss_4.setText('-')
            else:
                self.ui.attaquepuiss_4.setText(str(attackstat4[3]))
            if attackstat4[4] == 'echoue jamais':
                self.ui.attaqueprec_4.setText('-')
            else:
                self.ui.attaqueprec_4.setText(str(attackstat4[4]))
            self.ui.attaqueprio_4.setText(str(attackstat4[5]))
            self.ui.cible_4.clear()
            if attackstat4[15]=="lanceur":
                self.ui.cible_4.addItem("B")
            elif attackstat4[15]=="au choix sauf lanceur":
                self.ui.cible_4.addItems(["1","2","3","A","C"])
            elif attackstat4[15]=="tous les adversaires":
                self.ui.cible_4.addItem("Adversaires")
            elif attackstat4[15]=="tous sauf lanceur":
                self.ui.cible_4.addItem("Tous")
            elif attackstat4[15]=="random":
                self.ui.cible_4.addItem("Aléatoire")
            elif attackstat4[15]=="truc spécifique":
                if attackstat4[1]=="Malédiction" and self.ui.poketype1_4.toPlainText()!="spectre" and self.ui.poketype2_4.toPlainText()!="spectre":
                  self.ui.cible_4.addItem("B")
                else:
                  self.ui.cible_4.addItems(["1","2","3"])
            elif attackstat4[15]=="utilisateur et alliés":
                self.ui.cible_4.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat4[15]=="allié": # not doing anything, manual handle
                self.ui.cible_4.addItems(["A","C"])
            elif attackstat4[15]=="lanceur ou allié": # not doing anything, manual handle
                self.ui.cible_4.addItems(["A","B","C"])
            elif attackstat4[15]=="au choix": # not doing anything, manual handle
                self.ui.cible_4.addItems(["1","2","3","A","B","C"])
            elif attackstat4[15]=="tous" or attackstat4[15]=="tous les alliés": # not doing anything, manual handle
                self.ui.cible_4.addItem("/")

    def generateattack5(self):
        self.ui.attaque_5.setText(self.ui.attackdex_5.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex_5.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat5 = c.fetchone()
        if attackstat5 == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype_5.setText(attackstat5[2])
            self.ui.attaqueclasse_5.setText(attackstat5[6])
            if attackstat5[3] == None:
                self.ui.attaquepuiss_5.setText('-')
            else:
                self.ui.attaquepuiss_5.setText(str(attackstat5[3]))
            if attackstat5[4] == 'echoue jamais':
                self.ui.attaqueprec_5.setText('-')
            else:
                self.ui.attaqueprec_5.setText(str(attackstat5[4]))
            self.ui.attaqueprio_5.setText(str(attackstat5[5]))
            self.ui.cible_5.clear()
            if attackstat5[15]=="lanceur":
                self.ui.cible_5.addItem("3")
            elif attackstat5[15]=="au choix sauf lanceur":
                self.ui.cible_5.addItems(["A","B","C","1","2"])
            elif attackstat5[15]=="tous les adversaires":
                self.ui.cible_5.addItem("Adversaires")
            elif attackstat5[15]=="tous sauf lanceur":
                self.ui.cible_5.addItem("Tous")
            elif attackstat5[15]=="random":
                self.ui.cible_5.addItem("Aléatoire")
            elif attackstat5[15]=="truc spécifique":
                if attackstat5[1]=="Malédiction" and self.ui.poketype1_5.toPlainText()!="spectre" and self.ui.poketype2_5.toPlainText()!="spectre":
                  self.ui.cible_5.addItem("3")
                else:
                  self.ui.cible_5.addItems(["A","B","C"])
            elif attackstat5[15]=="utilisateur et alliés":
                self.ui.cible_5.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat5[15]=="allié":
                self.ui.cible_5.addItems(["1","2"])
            elif attackstat5[15]=="lanceur ou allié":
                self.ui.cible_5.addItems(["1","2","3"])
            elif attackstat5[15]=="au choix":
                self.ui.cible_5.addItems(["A","B","C","1","2","3"])
            elif attackstat5[15]=="tous" or attackstat5[15]=="tous les alliés":
                self.ui.cible_5.addItem("/")

    def generateattack6(self):
        self.ui.attaque_6.setText(self.ui.attackdex_6.currentText().replace("CT- ",""))
        attaquename=self.ui.attackdex_6.currentText().replace('CT- ','')
        c.execute('SELECT * FROM attaques WHERE nom=?',(attaquename,))
        attackstat6 = c.fetchone()
        if attackstat6 == None:
            msgBox1 = QMessageBox()
            msgBox1.setText('Attaque inconnue')
            msgBox1.exec_()
        else:
            self.ui.attaquetype_6.setText(attackstat6[2])
            self.ui.attaqueclasse_6.setText(attackstat6[6])
            if attackstat6[3] == None:
                self.ui.attaquepuiss_6.setText('-')
            else:
                self.ui.attaquepuiss_6.setText(str(attackstat6[3]))
            if attackstat6[4] == 'echoue jamais':
                self.ui.attaqueprec_6.setText('-')
            else:
                self.ui.attaqueprec_6.setText(str(attackstat6[4]))
            self.ui.attaqueprio_6.setText(str(attackstat6[5]))
            self.ui.cible_6.clear()
            if attackstat6[15]=="lanceur":
                self.ui.cible_6.addItem("C")
            elif attackstat6[15]=="au choix sauf lanceur":
                self.ui.cible_6.addItems(["1","2","3","A","B"])
            elif attackstat6[15]=="tous les adversaires":
                self.ui.cible_6.addItem("Adversaires")
            elif attackstat6[15]=="tous sauf lanceur":
                self.ui.cible_6.addItem("Tous")
            elif attackstat6[15]=="random":
                self.ui.cible_6.addItem("Aléatoire")
            elif attackstat6[15]=="truc spécifique":
                if attackstat6[1]=="Malédiction" and self.ui.poketype1_6.toPlainText()!="spectre" and self.ui.poketype2_6.toPlainText()!="spectre":
                  self.ui.cible_6.addItem("C")
                else:
                  self.ui.cible_6.addItems(["1","2","3"])
            elif attackstat6[15]=="utilisateur et alliés":
                self.ui.cible_6.addItem("Team") # code global heal effect directly in fight ?
            elif attackstat6[15]=="allié": # not doing anything, manual handle
                self.ui.cible_6.addItems(["A","B"])
            elif attackstat6[15]=="lanceur ou allié": # not doing anything, manual handle
                self.ui.cible_6.addItems(["A","B","C"])
            elif attackstat6[15]=="au choix": # not doing anything, manual handle
                self.ui.cible_6.addItems(["1","2","3","A","B","C"])
            elif attackstat6[15]=="tous" or attackstat6[15]=="tous les alliés": # not doing anything, manual handle
                self.ui.cible_6.addItem("/")

    def fight(self,pkmon1,statut1,attck1,pkmon2,statut2,advnb,totaladvnb,block,nosplash):
        # pkmon1 is attacking pkmon2
        unfreeze=["Flamme Ultime", "Roue de Feu", "Boutefeu",  "Flamme Croix", "Feu Sacré", "Ébullition", "Jet de Vapeur"]
        sleepymove=["Blabla Dodo", "Ronflement"]
        if statut1["fear"]:
            if advnb==1:
                self.ui.outputrp.appendPlainText("[i]{"+str(pkmon1["name"])+" est apeuré ! Il ne peut pas attaquer !}[/i]")
        elif statut1["freeze"] and advnb==1 and attck1["type"]!="objet":
            if (random.randint(1,100) <= 80 and attck1["name"] not in unfreeze) or blocks:
                self.ui.outputrp.appendPlainText('[i]{Le gel empêche '+str(pkmon1["name"])+" d'attaquer !}[/i][/")
                block=True
            else:
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+"n'est plus gelé !}[/i][/")

        elif statut1["para"] and (random.randint(1,100) <= 25 or block):
            if advnb==1:
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+" est paralysé ! Il ne peut pas attaquer !}[/i]")
            block=True
        elif statut1["deso"] and (random.randint(1,100) <= 25 or block):
            if advnb==1:
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+random.choice([" prétend qu'il n'entend rien !"," ignore les ordres !"," n'obéit pas !"," se détourne du combat !"])+"}[/i]")
            block=True
        elif statut1["sleep"] and attck1["name"] not in sleepymove and attck1["type"]!="objet":
            if advnb==1:
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+" est endormi ! Il ne peut pas attaquer !}[/i]")
        elif statut1["attraction"] and (random.randint(1,100) <= 50 or block):
            if advnb==1:
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+" est sous le charme d'un adversaire. Il ne peut pas attaquer !}[/i]")
            block=True
        elif statut1["conf"] and (random.randint(1,100) <= 33 or block) and attck1["type"]!="objet":
            if advnb==1:
                dmg=(((((2*pkmon1["lvl"]/5)+2)*pkmon1["att"]*40)/(pkmon1["def"]*50))+2)
                if statut1["burn"]:
                    dmg=dmg/2
                newpv2=pkmon1["pvcurrent"]-round(dmg)
                if newpv2 <= 0 :
                    newpv2 = 0
                    pkmon1["ko"] = True
                self.ui.outputrp.appendPlainText('[i]{'+str(pkmon1["name"])+" se blesse dans la confusion !}[/i]")
                self.ui.outputrp.appendPlainText('{[color=#ff0000][b]-'+str(round(dmg))+'[/b][/color]} PVs [color=#777777][size=10]« Nooooon ! »[/size][/color]\n[i]PVs de [b]'+pkmon1["name"]+'[/b][/i]: '+self.pvToColor(newpv2,pkmon1["pvtotal"])+str(newpv2)+'[/color]/'+str(pkmon1["pvtotal"]))
                if pkmon1["ko"]:
                    self.ui.outputrp.appendPlainText("[center]<img src='"+str(pkmon1["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(pkmon1["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")
                pkmon1["pvcurrent"]=newpv2
            block=True

        else:
            modifAccuracy=self.translateModifPrec(pkmon1["modifprec"]-pkmon2["modifesquive"])
            if attck1["prec"]=='-':
                attckprec=1000
            else:
                attckprec=int(attck1["prec"])
            if random.randint(1,100) <= attckprec*modifAccuracy:
                pkmon1Att=pkmon1["att"]*self.translateModifStat(pkmon1["modifatt"])
                pkmon2Def=pkmon2["def"]*self.translateModifStat(pkmon2["modifdef"])
                pkmon1Atts=pkmon1["atts"]*self.translateModifStat(pkmon1["modifatts"])
                pkmon2Defs=pkmon2["defs"]*self.translateModifStat(pkmon2["modifdefs"])
                if attck1["type"]==pkmon1["type1"] or attck1["type"]==pkmon1["type2"]:
                    stab=1.5
                else:
                    stab=1

                if attck1["name"]=="Lyophilisation" and pkmon2["type1"]=="eau":
                    typeModif=2*self.typeMatrix(attck1["type"],pkmon2["type2"])
                elif attck1["name"]=="Lyophilisation" and pkmon2["type2"]=="eau":
                    typeModif=self.typeMatrix(attck1["type"],pkmon2["type1"])*2
                else:
                    typeModif=self.typeMatrix(attck1["type"],pkmon2["type1"])*self.typeMatrix(attck1["type"],pkmon2["type2"])

                if typeModif==0:
                    texttype="Cela n'affecte pas "+pkmon2["name"]+"."
                elif typeModif<1:
                    texttype="Ce n'est pas très efficace."
                elif typeModif>1:
                    texttype="C'est super efficace !"
                else:
                    texttype=""

                if random.randint(1,100) <= attck1["critchance"]:
                    crit='yes'
                    textcrit='Coup critique ! '
                else:
                    crit='no'
                    textcrit=''
                if attck1["catchiante"]=="pp":
                    attck1["puiss"]=random.choice([40,60,80])
                
                if attck1["name"]=="Boule Élek":
                    percentvit=pkmon1["vit"]/pkmon2["vit"]
                    if percentvit<=1:
                        puisselek=40
                    elif percentvit<2:
                        puisselek=60
                    elif percentvit<3:
                        puisselek=80
                    elif percentvit<4:
                        puisselek=120
                    elif percentvit>=4:
                        puisselek=150
                    attck1["puiss"]=puisselek
                    self.ui.outputattack.append("Boule Élek ("+pkmon1["name"]+") a été utilisé avec une puissance de "+str(puisselek))

                if attck1["puiss"]=='-':
                    if attck1["dmgfixe"]!="":
                        dmg=attck1["dmgfixe"]
                    elif attck1["dmgpercent"]!="":
                        dmg=int(pkmon2["pvcurrent"])*(int(attck1["dmgpercent"])/100)
                    else:
                        dmg='exception'
                elif attck1["classe"]=="spécial" and crit=='yes':
                    if pkmon1["modifatts"]<0:
                        pkmon1Atts=pkmon1["atts"]
                    if pkmon2["modifdefs"]>0:
                        pkmon2Defs=pkmon2["defs"]
                    dmg=(((((2*pkmon1["lvl"]/5)+2)*pkmon1Atts*int(attck1["puiss"]))/(pkmon2Defs*50))+2)*stab*typeModif*1.5
                elif attck1["classe"]=="physique"and crit=='yes':
                    if pkmon1["modifatt"]<0:
                        pkmon1Att=pkmon1["att"]
                    if pkmon2["modifdef"]>0:
                        pkmon2Def=pkmon2["def"]
                    dmg=(((((2*pkmon1["lvl"]/5)+2)*pkmon1Att*int(attck1["puiss"]))/(pkmon2Def*50))+2)*stab*typeModif*1.5
                elif attck1["classe"]=="spécial" and crit=='no':
                    dmg=(((((2*pkmon1["lvl"]/5)+2)*pkmon1Atts*int(attck1["puiss"]))/(pkmon2Defs*50))+2)*stab*typeModif
                elif attck1["classe"]=="physique" and crit=='no':
                    dmg= (((((2*pkmon1["lvl"]/5)+2)*pkmon1Att*int(attck1["puiss"]))/(pkmon2Def*50))+2)*stab*typeModif
            else:
                dmg='fail'
                nosplash=True

            if attck1["name"]=="Rebondifeu" and nosplash==False and advnb>1:
                dmg=round(pkmon2["pvtotal"]/16)
                texttype=''
              
            if attck1["type"]=="objet":
                if attck1["name"]=="Swap":
                    self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] arrive sur le terrain !")
                elif attck1["name"]=="Item":
                    self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] utilise [u]"+attck1["name"]+"[/u] !")
                    self.ui.outputrp.appendPlainText("[i]{L'objet fait un truc !}[/i]")
                else:
                    self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] utilise [u]"+attck1["name"]+"[/u] !")
            elif attck1["target"]==pkmon1["fightID"]:
                self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] utilise [u]"+attck1["name"]+"[/u] !")

            elif advnb==1 and totaladvnb==1:
                self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] utilise [u]"+attck1["name"]+"[/u] sur [b]"+pkmon2["name"]+"[/b] !")
            elif advnb==1:
                self.ui.outputrp.appendPlainText("[b]"+pkmon1["name"]+"[/b] utilise [u]"+attck1["name"]+"[/u] !")
            if dmg=='fail':
                if totaladvnb > 1:
                    if (attck1["name"]=="Rebondifeu" and advnb==1) or attck1["name"]!="Rebondifeu":
                        self.ui.outputrp.appendPlainText(pkmon2["name"]+" esquive !")
                else:
                    self.ui.outputrp.appendPlainText("L'attaque a échoué !")
            elif attck1["classe"]=="no damage":
                if attck1["percenthpheal"]>0:
                    heal=pkmon2["pvtotal"]*attck1["percenthpheal"]/100
                    newpv1=pkmon2["pvcurrent"]+round(heal)
                    if newpv1>pkmon2["pvtotal"]:
                        newpv1=pkmon2["pvtotal"]
                    self.ui.outputrp.appendPlainText('{[color=#669900][b]+'+str(round(heal))+'[/b][/color]} PVs [color=#777777][size=10]« '+pkmon2["name"]+' se sent mieux. »[/size][/color]\n[i]PVs de [b]'+pkmon2["name"]+'[/b][/i]: '+self.pvToColor(newpv1,pkmon2["pvtotal"])+str(newpv1)+'[/color]/'+str(pkmon2["pvtotal"]))
                    pkmon2["pvcurrent"]=newpv1
                    if attck1["name"]=="Guérison":
                        if statut1["burn"]:
                            statut1["burn"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" n'est plus brûlé !}[/i]")
                        if statut1["freeze"]:
                            statut1["freeze"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" n'est plus gelé !}[/i]")
                        if statut1["para"]:
                            statut1["para"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" n'est plus paralysé !}[/i]")
                        if statut1["conf"]:
                            statut1["conf"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" n'est plus confus !}[/i]")
                        if statut1["poison"]:
                            statut1["poison"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" n'est plus empoisonné !}[/i]")
                        if statut1["sleep"]:
                            statut1["sleep"]=False
                            self.ui.outputrp.appendPlainText("[i]{"+pkmon1["name"]+" se réveille !}[/i]")

                elif attck1["soinfixe"]>0:
                    heal=attck1["soinfixe"]
                    newpv1=pkmon2["pvcurrent"]+round(heal)
                    if newpv1>pkmon2["pvtotal"]:
                        newpv1=pkmon2["pvtotal"]
                    self.ui.outputrp.appendPlainText('{[color=#669900][b]+'+str(round(heal))+'[/b][/color]} PVs [color=#777777][size=10]« '+pkmon2["name"]+' se sent mieux. »[/size][/color]\n[i]PVs de [b]'+pkmon2["name"]+'[/b][/i]: '+self.pvToColor(newpv1,pkmon2["pvtotal"])+str(newpv1)+'[/color]/'+str(pkmon2["pvtotal"]))
                    pkmon2["pvcurrent"]=newpv1

                elif attck1["name"]=="Malédiction":
                    if attck1["target"]==pkmon1["fightID"]:
                        if pkmon1["modifdef"]==6:
                            self.ui.outputrp.appendPlainText("[i]{La défense de "+pkmon1["name"]+" ne peut plus augmenter.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{La défense de "+pkmon1["name"]+" augmente !}[/i]")
                            pkmon1["modifdef"]=pkmon1["modifdef"]+1
                        if pkmon1["modifatt"]==6:
                            self.ui.outputrp.appendPlainText("[i]{L'attaque de "+pkmon1["name"]+" ne peut plus augmenter.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{L'attaque de "+pkmon1["name"]+" augmente !}[/i]")
                            pkmon1["modifatt"]=pkmon1["modifatt"]+1
                        if pkmon1["modifvit"]==-6:
                            self.ui.outputrp.appendPlainText("[i]{La vitesse de "+pkmon1["name"]+" ne peut plus baisser.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{La vitesse de "+pkmon1["name"]+" dimine !}[/i]")
                            pkmon1["modifvit"]=pkmon1["modifvit"]-1

                    else:
                        selfdmg=round(pkmon1["pvtotal"]/2)
                        newpv3=pkmon1['pvcurrent']-selfdmg
                        if newpv3<=0:
                            newpv3=0
                            pkmon1["ko"]=True
                        pkmon1["pvcurrent"]=newpv3
                        self.ui.outputrp.appendPlainText('{[color=#ff0000][b]'+str(round(selfdmg))+'[/b][/color]} PVs [color=#777777][size=10]« '+pkmon1["name"]+' sacrifie ses PVs ! »[/size][/color]\n[i]PVs de [b]'+pkmon1["name"]+'[/b][/i]: '+self.pvToColor(newpv3,pkmon1["pvtotal"])+str(newpv3)+'[/color]/'+str(pkmon1["pvtotal"]))
                        if pkmon1["ko"]:
                            self.ui.outputrp.appendPlainText("[center]<img src='"+str(pkmon1["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(pkmon1["name"])+" est K.O !}[/i]\n\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")

                        statut2["maledi"]=True
                        self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est maudit !}[/i]")

                elif attck1["effet_txt"]!=None and attck1["effet_txt"]!="":
                    self.ui.outputrp.appendPlainText("Vérifiez les effets de l'attaque, il pourrait manquer quelque chose.")

            elif dmg=='exception':
                # exception means puissance ="-" but attack is physique or special and there is no fixed dmg or stuffs like that
                self.ui.outputrp.appendPlainText("Attaque avec des dégats particuliers à gérer à la main.")

            else:
                if attck1["classe"]=="physique" and statut1["burn"]:
                    dmg=dmg/2
                if totaladvnb > 1 and attck1["name"]!="Rebondifeu":
                    dmg=dmg*0.75
                newpv2=pkmon2["pvcurrent"]-round(dmg)
                if dmg==0:
                    textcrit=''
                if newpv2 <= 0 :
                    newpv2 = 0
                    pkmon2["ko"] = True
                if textcrit=='' and texttype=='':
                    randomuptxt=random.choice(['Bien joué '+pkmon1["name"]+' !','Encore un effort '+pkmon1["name"]+' !', 'Beau boulot '+pkmon1["name"]+' !','Pauvre '+pkmon2["name"]+' !',pkmon2["name"]+' est blessé !'])
                else:
                    randomuptxt=''

                if attck1["catchiante"]=="multihit:2" or attck1["catchiante"]=="multihit:2-5":
                    if attck1["catchiante"]=="multihit:2":
                        nbhit=2
                    if attck1["catchiante"]=="multihit:2-5":
                        nbhit=random.randint(2,5)
                    newpv2=pkmon2["pvcurrent"]
                    for hit in range(0,nbhit):
                        if random.randint(1,100) <= attck1["critchance"]:
                            if self.translateModifStat(pkmon1["modifatt"])<0:
                                pkmon1Att=pkmon1["att"]
                            if self.translateModifStat(pkmon2["modifdef"])>0:
                                pkmon2Def=pkmon2["def"]
                            dmg= (((((2*pkmon1["lvl"]/5)+2)*pkmon1Att*int(attck1["puiss"]))/(pkmon2Def*50))+2)*stab*typeModif*1.5
                        else:
                            dmg= (((((2*pkmon1["lvl"]/5)+2)*pkmon1Att*int(attck1["puiss"]))/(pkmon2Def*50))+2)*stab*typeModif
                        if statut1["burn"]:
                            dmg= dmg/2
                        newpv2=newpv2-round(dmg)
                        if hit==0:
                            self.ui.outputrp.appendPlainText('{[color=#ff0000][b]-'+str(round(dmg))+'[/b][/color]}')
                        else:
                            self.ui.outputrp.insertPlainText('{[color=#ff0000][b]-'+str(round(dmg))+'[/b][/color]}')
                    if newpv2 <= 0 :
                        newpv2 = 0
                        pkmon2["ko"] = True
                    self.ui.outputrp.insertPlainText(' PVs [color=#777777][size=10]« '+texttype+randomuptxt+' »[/size][/color]\n[i]PVs de [b]'+pkmon2["name"]+'[/b][/i]: '+self.pvToColor(newpv2,pkmon2["pvtotal"])+str(newpv2)+'[/color]/'+str(pkmon2["pvtotal"]))
                    pkmon2["pvcurrent"]=newpv2
                    if pkmon2["ko"]:
                        self.ui.outputrp.appendPlainText("[center]<img src='"+str(pkmon2["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(pkmon2["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")


                else:
                    self.ui.outputrp.appendPlainText('{[color=#ff0000][b]-'+str(round(dmg))+'[/b][/color]} PVs [color=#777777][size=10]« '+textcrit+texttype+randomuptxt+' »[/size][/color]\n[i]PVs de [b]'+pkmon2["name"]+'[/b][/i]: '+self.pvToColor(newpv2,pkmon2["pvtotal"])+str(newpv2)+'[/color]/'+str(pkmon2["pvtotal"]))
                    pkmon2["pvcurrent"]=newpv2
                    if pkmon2["ko"]:
                        self.ui.outputrp.appendPlainText("[center]<img src='"+str(pkmon2["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(pkmon2["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")

                    elif statut2["freeze"] and attck1["type"]=="feu":
                        statut2["freeze"]=False
                        self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" n'est plus gelé !}[/i]")

                if attck1["percenthpdrain"]!=0:
                    selfdmg=round(dmg*attck1["percenthpdrain"]/100)
                    newpv3=pkmon1['pvcurrent']+selfdmg
                    if newpv3>pkmon1["pvtotal"]:
                        newpv3=pkmon1["pvtotal"]
                    elif newpv3<=0:
                        newpv3=0
                        pkmon1["ko"]=True
                    if attck1["percenthpdrain"]<0:
                        self.ui.outputrp.appendPlainText('\n{[color=#ff0000][b]'+str(round(selfdmg))+'[/b][/color]} PVs [color=#777777][size=10]« '+pkmon1["name"]+' se blesse en frappant ! »[/size][/color]\n[i]PVs de [b]'+pkmon1["name"]+'[/b][/i]: '+self.pvToColor(newpv3,pkmon1["pvtotal"])+str(newpv3)+'[/color]/'+str(pkmon1["pvtotal"]))
                        if pkmon1["ko"]:
                            self.ui.outputrp.appendPlainText("[center]<img src='"+str(pkmon2["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(pkmon1["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")
                    else:
                        self.ui.outputrp.appendPlainText('\n{[color=#669900][b]+'+str(round(selfdmg))+'[/b][/color]} PVs [color=#777777][size=10]« '+pkmon1["name"]+' se sent mieux. »[/size][/color]\n[i]PVs de [b]'+pkmon1["name"]+'[/b][/i]: '+self.pvToColor(newpv3,pkmon1["pvtotal"])+str(newpv3)+'[/color]/'+str(pkmon1["pvtotal"]))
                    pkmon1["pvcurrent"]=newpv3

            c.execute('SELECT * FROM attaques_stats_lanceur WHERE nom_attaque=?',(attck1["name"],))
            statmodif1 = c.fetchone()
            c.execute('SELECT * FROM attaques_stats_adversaire WHERE nom_attaque=?',(attck1["name"],))
            statmodif2 = c.fetchone()

            if attck1["effectchance"]==None:
                effetproc='yes'
            else:
                if random.randint(1,100) <= attck1["effectchance"]:
                    effetproc='yes'
                else:
                    effetproc='no'
            txtstat = ("L'attaque","La défense","L'attaque spéciale","La défense spéciale","La vitesse","La précision","L'esquive")
            getstat = ("modifatt","modifdef","modifatts","modifdefs","modifvit","modifprec","modifesquive")
            if statmodif1 !=None and dmg!='fail' and effetproc=='yes':
                statmodif1=tuple(x if x else 0 for x in statmodif1)
                for stat in range(0,7):
                    if statmodif1[stat+2]<0 and pkmon1["ko"]==False:
                        if pkmon1[getstat[stat]]==-6:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon1["name"]+" ne peut plus baisser.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon1["name"]+" diminue !}[/i]")
                            if pkmon1[getstat[stat]]==-5:
                                pkmon1[getstat[stat]]=-6
                            else:
                                pkmon1[getstat[stat]]=pkmon1[getstat[stat]]+statmodif1[stat+2]
                    elif statmodif1[stat+2]>0 and pkmon1["ko"]==False:
                        if pkmon1[getstat[stat]]==6:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon1["name"]+" ne peut plus augmenter.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon1["name"]+" augmente !}[/i]")
                            if pkmon1[getstat[stat]]==5:
                                pkmon1[getstat[stat]]=6
                            else:
                                pkmon1[getstat[stat]]=pkmon1[getstat[stat]]+statmodif1[stat+2]

            if statmodif2 !=None and dmg!='fail' and effetproc=='yes':
                statmodif2=tuple(x if x else 0 for x in statmodif2)
                for stat in range(0,7):
                    if statmodif2[stat+2]<0 and pkmon2["ko"]==False:
                        if pkmon2[getstat[stat]]==-6:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon2["name"]+" ne peut plus baisser.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon2["name"]+" diminue !}[/i]")
                            if pkmon2[getstat[stat]]==-5:
                                pkmon2[getstat[stat]]=-6
                            else:
                                pkmon2[getstat[stat]]=pkmon2[getstat[stat]]+statmodif2[stat+2]
                    elif statmodif2[stat+2]>0 and pkmon2["ko"]==False:
                        if pkmon2[getstat[stat]]==6:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon2["name"]+" ne peut plus augmenter.}[/i]")
                        else:
                            self.ui.outputrp.appendPlainText("[i]{"+txtstat[stat]+" de "+pkmon2["name"]+" augmente !}[/i]")
                            if pkmon2[getstat[stat]]==5:
                                pkmon2[getstat[stat]]=6
                            else:
                                pkmon2[getstat[stat]]=pkmon2[getstat[stat]]+statmodif2[stat+2]

            if attck1["statutchance"]!="" and dmg!="fail":
                previousStatut=(statut2["burn"] or statut2["freeze"] or statut2["para"] or statut2["sleep"] or statut2["poison"])
                statutmain=(attck1["statut"]=="Brûlure" or attck1["statut"]=="Gel" or attck1["statut"]=="Paralysie" or attck1["statut"]=="Sommeil" or attck1["statut"]=="Empoisonnement")
                if random.randint(1,100) <= attck1["statutchance"]:
                  if previousStatut and statutmain:
                    self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est déjà sous l'effet d'un statut.}[/i]")
                  elif attck1["statut"]=="Brûlure":
                    if pkmon2["type1"]=="feu" or pkmon2["type2"]=="feu":
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est immunisé et ne peut pas être brûlé.}[/i]")
                    else:
                      statut2["burn"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est brûlé !}[/i]")
                  elif attck1["statut"]=="Gel":
                      statut2["freeze"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est gelé !}[/i]")
                  elif attck1["statut"]=="Paralysie":
                      if (pkmon2["type1"]=="sol" or pkmon2["type2"]=="sol") and attck1["type"]=="électrique":
                          self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est immunisé et ne peut pas être paralysé.}[/i]")
                      else:
                          statut2["para"]=True
                          self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est paralysé !}[/i]")
                  elif attck1["statut"]=="Empoisonnement":
                    if pkmon2["type1"]=="poison" or pkmon2["type2"]=="poison" or pkmon2["type1"]=="acier" or pkmon2["type2"]=="acier":
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est immunisé et ne peut pas être empoisonné.}[/i]")
                    else:
                      statut2["poison"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est empoisonné !}[/i]")
                  elif attck1["statut"]=="Sommeil":
                      statut2["sleep"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" s'endort !}[/i]")
                      self.ui.outputmodo.append(pkmon2["name"]+" : Sommeil pour "+str(random.randint(1,3))+" tours")
                  elif attck1["statut"]=="Attraction":
                      statut2["attraction"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est sous le charme de "+pkmon1["name"]+" !}[/i]")
                  elif attck1["statut"]=="Confusion":
                      statut2["conf"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est confus !}[/i]")
                      self.ui.outputmodo.append(pkmon2["name"]+" : Confusion pour "+str(random.randint(1,4))+" tours")
                  elif attck1["statut"]=="Piège":
                      statut2["piege"]=True
                      self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est piégé par "+attck1["name"]+" !}[/i]")
                      self.ui.outputmodo.append(pkmon2["name"]+" : Piégé pour "+str(random.randint(4,5))+" tours")
                  elif attck1["statut"]=="Vampigraine":
                      if pkmon2["type1"]=="plante" or pkmon2["type2"]=="plante":
                        self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est immunisé contre vampigraine.}[/i]")
                      else:
                        statut2["vampi"]=pkmon1["fightID"]
                        self.ui.outputrp.appendPlainText("[i]{"+pkmon2["name"]+" est infecté par vampigraine !}[/i]")

            if random.randint(1,100) <= attck1["fearchance"]:
                statut2["fear"]=True
            if attck1["effet_txt"]!="" and advnb==1:
                self.ui.outputattack.append(attck1["name"]+":\n"+attck1["effet_txt"])

        toReturn = {"pkmon1": pkmon1, "statut1": statut1,"pkmon2": pkmon2,"statut2": statut2,"block": block, "nosplash": nosplash}
        return toReturn

    def fightInit(self):
        try:
            self.ui.outputrp.setPlainText('')
            self.ui.outputmodo.setText("[modo][spoiler=Infos modération][code]")
            self.ui.outputattack.setText('')
            if (self.ui.attaqueprio.toPlainText()=='' and self.ui.attaqueprio_3.toPlainText()=='' and self.ui.attaqueprio_4.toPlainText()=='') or (self.ui.attaqueprio_2.toPlainText()=='' and self.ui.attaqueprio_4.toPlainText()=='' and self.ui.attaqueprio_6.toPlainText()==''):
                msgBox1 = QMessageBox()
                msgBox1.setText('Données manquantes')
                msgBox1.exec_()
            else:
                # get pkmon numbers for sprites
                c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke.toPlainText(),))
                idpkmon1 = c.fetchone()
                c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_2.toPlainText(),))
                idpkmon2 = c.fetchone()
                # get invisible attack data
                c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque.toPlainText(),))
                attackdata = c.fetchone()
                c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_2.toPlainText(),))
                attackdata2 = c.fetchone()
                # dic with pokemons and attacks data to pass to function
                # pokemon trainer 1
                allpkmon=[]
                allattack=[]
                allstatut=[]
                niceteam=[]
                advteam=[]

                if self.ui.poke.toPlainText()!="" and self.ui.attaque.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke.toPlainText(),))
                    idpkmon1 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque.toPlainText(),))
                    attackdata = c.fetchone()

                    vit1 = int(self.ui.vit.toPlainText())*self.translateModifStat(self.ui.modifvit.value())
                    if self.ui.effetpara.isChecked():
                        vit1=vit1/2
                    if self.ui.trainer.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon1[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character
                        species=""
                        for character in self.ui.poke.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character

                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer.toPlainText()+"/"+surnom+species+".png"

                    pkmn1 = {"sprite": sprite, "trainer": self.ui.trainer.toPlainText(),"id": idpkmon1[0], "lvl": int(self.ui.pokelvl.toPlainText()),"name": self.ui.pokename.toPlainText() ,"realname": self.ui.poke.toPlainText(),"pvcurrent": int(self.ui.pvcurrent.toPlainText()) ,"pvtotal": int(self.ui.pvtotal.toPlainText()),"att": int(self.ui.att.toPlainText()),"def": int(self.ui.defen.toPlainText()),"atts": int(self.ui.atts.toPlainText()),"defs": int(self.ui.defs.toPlainText()),"vit": vit1, "type1": self.ui.poketype1.toPlainText(),"type2": self.ui.poketype2.toPlainText(),"modifatt": self.ui.modifatt.value(),"modifdef": self.ui.modifdefen.value(), "modifatts": self.ui.modifatts.value(), "modifdefs": self.ui.modifdefs.value(),"modifvit": self.ui.modifvit.value(), "modifesquive": self.ui.modifesquive.value(), "modifprec": self.ui.modifprec.value(), "prio": int(self.ui.attaqueprio.toPlainText()),"ko": False, "fightID": "1","side": "listL", "truevit": self.ui.vit.toPlainText()}

                    attck1 = {"name": self.ui.attaque.toPlainText(),"type": self.ui.attaquetype.toPlainText(), "classe": self.ui.attaqueclasse.toPlainText(), "puiss": self.ui.attaquepuiss.toPlainText(), "prec": self.ui.attaqueprec.toPlainText(), "critchance": self.translateCrit(attackdata[14]), "fearchance": attackdata[13], "percenthpheal": attackdata[11], "percenthpdrain": attackdata[12], "statutchance": attackdata[10], "statut": attackdata[9], "effectchance": attackdata[8], "effet_txt": attackdata[7],"prio": int(self.ui.attaqueprio.toPlainText()), "vit": vit1,"target": self.ui.cible.currentText(), "dmgfixe": attackdata[16], "dmgpercent": attackdata[17], "catchiante": attackdata[18], "soinfixe": attackdata[19]}

                    statut1 = {"fear":False, "burn":self.ui.effetbrule.isChecked(), "freeze":self.ui.effetgel.isChecked(), "para":self.ui.effetpara.isChecked(), "poison":self.ui.effetpoison.isChecked(), "sleep":self.ui.effetsommeil.isChecked(), "attraction":self.ui.effetattrac.isChecked(), "conf":self.ui.effetconfus.isChecked(), "maledi":self.ui.effetmaledi.isChecked(), "vampi":self.ui.vampicible.currentText(),"prio": int(self.ui.attaqueprio.toPlainText()), "vit": vit1, "deso": self.ui.effetdeso.isChecked(), "ident": self.ui.effetident.isChecked(), "piege":self.ui.effetpiege.isChecked(), "fightID": "1"}
    
                    allpkmon.append(pkmn1)
                    allattack.append(attck1)
                    allstatut.append(statut1)
                    niceteam.append(pkmn1)

                # pokemon enemy A
                if self.ui.poke_2.toPlainText()!="" and self.ui.attaque_2.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_2.toPlainText(),))
                    idpkmon2 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_2.toPlainText(),))
                    attackdata2 = c.fetchone()

                    vit2 = int(self.ui.vit_2.toPlainText())*self.translateModifStat(self.ui.modifvit_2.value())
                    if self.ui.effetpara_2.isChecked():
                        vit2=vit2/2
                    if self.ui.trainer_2.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon2[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename_2.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character

                        species=""
                        for character in self.ui.poke_2.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character

                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer_2.toPlainText()+"/"+surnom+species+".png"

                    pkmn2 = {"sprite": sprite, "trainer": self.ui.trainer_2.toPlainText(), "id": idpkmon2[0], "lvl": int(self.ui.pokelvl_2.toPlainText()),"name": self.ui.pokename_2.toPlainText() ,"realname": self.ui.poke_2.toPlainText(),"pvcurrent": int(self.ui.pvcurrent_2.toPlainText()) ,"pvtotal": int(self.ui.pvtotal_2.toPlainText()),"att": int(self.ui.att_2.toPlainText()),"def": int(self.ui.defen_2.toPlainText()),"atts": int(self.ui.atts_2.toPlainText()),"defs": int(self.ui.defs_2.toPlainText()),"type1": self.ui.poketype1_2.toPlainText(),"type2": self.ui.poketype2_2.toPlainText(),"modifatt": self.ui.modifatt_2.value(),"modifdef": self.ui.modifdefen_2.value(), "modifatts": self.ui.modifatts_2.value(), "modifdefs": self.ui.modifdefs_2.value(),"modifvit": self.ui.modifvit_2.value(), "modifesquive": self.ui.modifesquive_2.value(), "modifprec": self.ui.modifprec_2.value(),"prio": int(self.ui.attaqueprio_2.toPlainText()), "vit": vit2,"ko": False, "fightID": "A","side": "listR", "truevit": self.ui.vit_2.toPlainText()}

                    attck2 = {"name": self.ui.attaque_2.toPlainText(),"type": self.ui.attaquetype_2.toPlainText(), "classe": self.ui.attaqueclasse_2.toPlainText(), "puiss": self.ui.attaquepuiss_2.toPlainText(), "prec": self.ui.attaqueprec_2.toPlainText(), "critchance": self.translateCrit(attackdata2[14]), "fearchance": attackdata2[13], "percenthpheal": attackdata2[11], "percenthpdrain": attackdata2[12], "statutchance": attackdata2[10], "statut": attackdata2[9], "effectchance": attackdata2[8], "effet_txt": attackdata2[7],"prio": int(self.ui.attaqueprio_2.toPlainText()), "vit": vit2,"target": self.ui.cible_2.currentText(), "dmgfixe": attackdata2[16], "dmgpercent": attackdata2[17], "catchiante": attackdata2[18], "soinfixe": attackdata2[19]}

                    statut2 = {"fear":False, "burn":self.ui.effetbrule_2.isChecked(), "freeze":self.ui.effetgel_2.isChecked(), "para":self.ui.effetpara_2.isChecked(), "poison":self.ui.effetpoison_2.isChecked(), "sleep":self.ui.effetsommeil_2.isChecked(), "attraction":self.ui.effetattrac_2.isChecked(), "conf":self.ui.effetconfus_2.isChecked(), "maledi":self.ui.effetmaledi_2.isChecked(), "vampi":self.ui.vampicible_2.currentText(),"prio": int(self.ui.attaqueprio_2.toPlainText()), "vit": vit2, "deso": self.ui.effetdeso_2.isChecked(), "ident": self.ui.effetident_2.isChecked(), "piege":self.ui.effetpiege_2.isChecked(), "fightID": "A"}

                    allpkmon.append(pkmn2)
                    allattack.append(attck2)
                    allstatut.append(statut2)
                    advteam.append(pkmn2)

                # pokemon trainer 2
                if self.ui.poke_3.toPlainText()!="" and self.ui.attaque_3.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_3.toPlainText(),))
                    idpkmon3 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_3.toPlainText(),))
                    attackdata3 = c.fetchone()

                    vit3 = int(self.ui.vit_3.toPlainText())*self.translateModifStat(self.ui.modifvit_3.value())
                    if self.ui.effetpara_3.isChecked():
                        vit3=vit3/2

                    if self.ui.trainer_3.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon3[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename_3.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character
                        species=""
                        for character in self.ui.poke_3.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character
                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer_3.toPlainText()+"/"+surnom+species+".png"

                    pkmn3 = {"sprite": sprite, "id": idpkmon3[0], "trainer": self.ui.trainer_3.toPlainText(), "lvl": int(self.ui.pokelvl_3.toPlainText()),"name": self.ui.pokename_3.toPlainText() ,"realname": self.ui.poke_3.toPlainText(),"pvcurrent": int(self.ui.pvcurrent_3.toPlainText()) ,"pvtotal": int(self.ui.pvtotal_3.toPlainText()),"att": int(self.ui.att_3.toPlainText()),"def": int(self.ui.defen_3.toPlainText()),"atts": int(self.ui.atts_3.toPlainText()),"defs": int(self.ui.defs_3.toPlainText()),"vit": vit3,"type1": self.ui.poketype1_3.toPlainText(),"type2": self.ui.poketype2_3.toPlainText(),"modifatt": self.ui.modifatt_3.value(),"modifdef": self.ui.modifdefen_3.value(), "modifatts": self.ui.modifatts_3.value(), "modifdefs": self.ui.modifdefs_3.value(),"modifvit": self.ui.modifvit_3.value(), "modifesquive": self.ui.modifesquive_3.value(), "modifprec": self.ui.modifprec_3.value(),"prio":  int(self.ui.attaqueprio_3.toPlainText()),"ko": False, "fightID": "2","side": "listL", "truevit": self.ui.vit_3.toPlainText()}

                    attck3 = {"name": self.ui.attaque_3.toPlainText(),"type": self.ui.attaquetype_3.toPlainText(), "classe": self.ui.attaqueclasse_3.toPlainText(), "puiss": self.ui.attaquepuiss_3.toPlainText(), "prec": self.ui.attaqueprec_3.toPlainText(), "critchance": self.translateCrit(attackdata3[14]), "fearchance": attackdata3[13], "percenthpheal": attackdata3[11], "percenthpdrain": attackdata3[12], "statutchance": attackdata3[10], "statut": attackdata3[9], "effectchance": attackdata3[8], "effet_txt": attackdata3[7],"prio": int(self.ui.attaqueprio_3.toPlainText()), "vit": vit3 ,"target": self.ui.cible_3.currentText(), "dmgfixe": attackdata3[16], "dmgpercent": attackdata3[17], "catchiante": attackdata3[18], "soinfixe": attackdata3[19]}

                    statut3 = {"fear":False, "burn":self.ui.effetbrule_3.isChecked(), "freeze":self.ui.effetgel_3.isChecked(), "para":self.ui.effetpara_3.isChecked(), "poison":self.ui.effetpoison_3.isChecked(), "sleep":self.ui.effetsommeil_3.isChecked(), "attraction":self.ui.effetattrac_3.isChecked(), "conf":self.ui.effetconfus_3.isChecked(), "maledi":self.ui.effetmaledi_3.isChecked(), "vampi":self.ui.vampicible_3.currentText(),"prio": int(self.ui.attaqueprio_3.toPlainText()), "vit": vit3, "deso": self.ui.effetdeso_3.isChecked(), "ident": self.ui.effetident_3.isChecked(), "piege":self.ui.effetpiege_3.isChecked(), "fightID": "2"}

                    allpkmon.append(pkmn3)
                    allattack.append(attck3)
                    allstatut.append(statut3)
                    niceteam.append(pkmn3)

                # pokemon enemy B
                if self.ui.poke_4.toPlainText()!="" and self.ui.attaque_4.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_4.toPlainText(),))
                    idpkmon4 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_4.toPlainText(),))
                    attackdata4 = c.fetchone()

                    vit4 = int(self.ui.vit_4.toPlainText())*self.translateModifStat(self.ui.modifvit_4.value())
                    if self.ui.effetpara_4.isChecked():
                        vit4=vit4/2

                    if self.ui.trainer_4.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon4[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename_4.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character
                        species=""
                        for character in self.ui.poke_4.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character

                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer_4.toPlainText()+"/"+surnom+species+".png"

                    pkmn4 = {"sprite": sprite, "id": idpkmon4[0], "trainer": self.ui.trainer_4.toPlainText(), "lvl": int(self.ui.pokelvl_4.toPlainText()),"name": self.ui.pokename_4.toPlainText() ,"realname": self.ui.poke_4.toPlainText(),"pvcurrent": int(self.ui.pvcurrent_4.toPlainText()) ,"pvtotal": int(self.ui.pvtotal_4.toPlainText()),"att": int(self.ui.att_4.toPlainText()),"def": int(self.ui.defen_4.toPlainText()),"atts": int(self.ui.atts_4.toPlainText()),"defs": int(self.ui.defs_4.toPlainText()),"vit": vit4,"type1": self.ui.poketype1_4.toPlainText(),"type2": self.ui.poketype2_4.toPlainText(),"modifatt": self.ui.modifatt_4.value(),"modifdef": self.ui.modifdefen_4.value(), "modifatts": self.ui.modifatts_4.value(), "modifdefs": self.ui.modifdefs_4.value(),"modifvit": self.ui.modifvit_4.value(), "modifesquive": self.ui.modifesquive_4.value(), "modifprec": self.ui.modifprec_4.value(),"prio": int(self.ui.attaqueprio_4.toPlainText()),"ko": False, "fightID": "B","side": "listR", "truevit": self.ui.vit_4.toPlainText()}

                    attck4 = {"name": self.ui.attaque_4.toPlainText(),"type": self.ui.attaquetype_4.toPlainText(), "classe": self.ui.attaqueclasse_4.toPlainText(), "puiss": self.ui.attaquepuiss_4.toPlainText(), "prec": self.ui.attaqueprec_4.toPlainText(), "critchance": self.translateCrit(attackdata4[14]), "fearchance": attackdata4[13], "percenthpheal": attackdata4[11], "percenthpdrain": attackdata4[12], "statutchance": attackdata4[10], "statut": attackdata4[9], "effectchance": attackdata4[8], "effet_txt": attackdata4[7], "prio": int(self.ui.attaqueprio_4.toPlainText()), "vit": vit4 ,"target": self.ui.cible_4.currentText(), "dmgfixe": attackdata4[16], "dmgpercent": attackdata4[17], "catchiante": attackdata4[18], "soinfixe": attackdata4[19]}

                    statut4 = {"fear":False, "burn":self.ui.effetbrule_4.isChecked(), "freeze":self.ui.effetgel_4.isChecked(), "para":self.ui.effetpara_4.isChecked(), "poison":self.ui.effetpoison_4.isChecked(), "sleep":self.ui.effetsommeil_4.isChecked(), "attraction":self.ui.effetattrac_4.isChecked(), "conf":self.ui.effetconfus_4.isChecked(), "maledi":self.ui.effetmaledi_4.isChecked(), "vampi":self.ui.vampicible_4.currentText(),"prio": int(self.ui.attaqueprio_4.toPlainText()), "vit": vit4, "deso": self.ui.effetdeso_4.isChecked(), "ident": self.ui.effetident_4.isChecked(), "piege":self.ui.effetpiege_4.isChecked(), "fightID": "B"}

                    allpkmon.append(pkmn4)
                    allattack.append(attck4)
                    allstatut.append(statut4)
                    advteam.append(pkmn4)


                # pokemon trainer 3
                if self.ui.poke_5.toPlainText()!="" and self.ui.attaque_5.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_5.toPlainText(),))
                    idpkmon5 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_5.toPlainText(),))
                    attackdata5 = c.fetchone()

                    vit5 = int(self.ui.vit_5.toPlainText())*self.translateModifStat(self.ui.modifvit_5.value())
                    if self.ui.effetpara_5.isChecked():
                        vit5=vit5/2

                    if self.ui.trainer_5.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon5[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename_5.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character
                        species=""
                        for character in self.ui.poke_5.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character

                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer_5.toPlainText()+"/"+surnom+species+".png"

                    pkmn5 = {"sprite": sprite, "id": idpkmon5[0], "trainer": self.ui.trainer_5.toPlainText(), "lvl": int(self.ui.pokelvl_5.toPlainText()),"name": self.ui.pokename_5.toPlainText() ,"realname": self.ui.poke_5.toPlainText(),"pvcurrent": int(self.ui.pvcurrent_5.toPlainText()) ,"pvtotal": int(self.ui.pvtotal_5.toPlainText()),"att": int(self.ui.att_5.toPlainText()),"def": int(self.ui.defen_5.toPlainText()),"atts": int(self.ui.atts_5.toPlainText()),"defs": int(self.ui.defs_5.toPlainText()),"vit": vit5,"type1": self.ui.poketype1_5.toPlainText(),"type2": self.ui.poketype2_5.toPlainText(),"modifatt": self.ui.modifatt_5.value(),"modifdef": self.ui.modifdefen_5.value(), "modifatts": self.ui.modifatts_5.value(), "modifdefs": self.ui.modifdefs_5.value(),"modifvit": self.ui.modifvit_5.value(), "modifesquive": self.ui.modifesquive_5.value(), "modifprec": self.ui.modifprec_5.value(), "prio": int(self.ui.attaqueprio_5.toPlainText()),"ko": False, "fightID": "3","side": "listL", "truevit": self.ui.vit_5.toPlainText()}

                    attck5 = {"name": self.ui.attaque_5.toPlainText(),"type": self.ui.attaquetype_5.toPlainText(), "classe": self.ui.attaqueclasse_5.toPlainText(), "puiss": self.ui.attaquepuiss_5.toPlainText(), "prec": self.ui.attaqueprec_5.toPlainText(), "critchance": self.translateCrit(attackdata5[14]), "fearchance": attackdata5[13], "percenthpheal": attackdata5[11], "percenthpdrain": attackdata5[12], "statutchance": attackdata5[10], "statut": attackdata5[9], "effectchance": attackdata5[8], "effet_txt": attackdata5[7], "prio": int(self.ui.attaqueprio_5.toPlainText()), "vit": vit5,"target": self.ui.cible_5.currentText(), "dmgfixe": attackdata5[16], "dmgpercent": attackdata5[17], "catchiante": attackdata5[18], "soinfixe": attackdata5[19]}

                    statut5 = {"fear":False, "burn":self.ui.effetbrule_5.isChecked(), "freeze":self.ui.effetgel_5.isChecked(), "para":self.ui.effetpara_5.isChecked(), "poison":self.ui.effetpoison_5.isChecked(), "sleep":self.ui.effetsommeil_5.isChecked(), "attraction":self.ui.effetattrac_5.isChecked(), "conf":self.ui.effetconfus_5.isChecked(), "maledi":self.ui.effetmaledi_5.isChecked(), "vampi":self.ui.vampicible_5.currentText(), "prio": int(self.ui.attaqueprio_5.toPlainText()), "vit": vit5, "deso": self.ui.effetdeso_5.isChecked(), "ident": self.ui.effetident_5.isChecked(), "piege":self.ui.effetpiege_5.isChecked(), "fightID": "3"}

                    allpkmon.append(pkmn5)
                    allattack.append(attck5)
                    allstatut.append(statut5)
                    niceteam.append(pkmn5)

                # pokemon enemy C
                if self.ui.poke_6.toPlainText()!="" and self.ui.attaque_6.toPlainText()!="":
                    c.execute('SELECT id FROM pokemons WHERE nom=?',(self.ui.poke_6.toPlainText(),))
                    idpkmon6 = c.fetchone()
                    c.execute('SELECT * FROM attaques WHERE nom=?',(self.ui.attaque_6.toPlainText(),))
                    attackdata6 = c.fetchone()

                    vit6 = int(self.ui.vit_6.toPlainText())*self.translateModifStat(self.ui.modifvit_6.value())
                    if self.ui.effetpara_6.isChecked():
                        vit6=vit6/2

                    if self.ui.trainer_6.toPlainText()=="0000":
                        sprite="https://sunrise-db.yo.fr/Sprites/"+str(idpkmon6[0])+".png"
                    else:
                        surnom=""
                        for character in self.ui.pokename_6.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                surnom += character
                        species=""
                        for character in self.ui.poke_6.toPlainText():
                            if character.isalnum() and ord(character) < 128:
                                species += character

                        sprite="https://sunrise-db.yo.fr/SISNetwork/sprites/"+self.ui.trainer_6.toPlainText()+"/"+surnom+species+".png"

                    pkmn6 = {"sprite": sprite, "id": idpkmon6[0], "trainer": self.ui.trainer_6.toPlainText(), "lvl": int(self.ui.pokelvl_6.toPlainText()),"name": self.ui.pokename_6.toPlainText() ,"realname": self.ui.poke_6.toPlainText(),"pvcurrent": int(self.ui.pvcurrent_6.toPlainText()) ,"pvtotal": int(self.ui.pvtotal_6.toPlainText()),"att": int(self.ui.att_6.toPlainText()),"def": int(self.ui.defen_6.toPlainText()),"atts": int(self.ui.atts_6.toPlainText()),"defs": int(self.ui.defs_6.toPlainText()),"vit": vit6,"type1": self.ui.poketype1_6.toPlainText(),"type2": self.ui.poketype2_6.toPlainText(),"modifatt": self.ui.modifatt_6.value(),"modifdef": self.ui.modifdefen_6.value(), "modifatts": self.ui.modifatts_6.value(), "modifdefs": self.ui.modifdefs_6.value(),"modifvit": self.ui.modifvit_6.value(), "modifesquive": self.ui.modifesquive_6.value(), "modifprec": self.ui.modifprec_6.value(),"prio": int(self.ui.attaqueprio_6.toPlainText()),"ko": False, "fightID": "C","side": "listR", "truevit": self.ui.vit_6.toPlainText()}

                    attck6 = {"name": self.ui.attaque_6.toPlainText(),"type": self.ui.attaquetype_6.toPlainText(), "classe": self.ui.attaqueclasse_6.toPlainText(), "puiss": self.ui.attaquepuiss_6.toPlainText(), "prec": self.ui.attaqueprec_6.toPlainText(), "critchance": self.translateCrit(attackdata6[14]), "fearchance": attackdata6[13], "percenthpheal": attackdata6[11], "percenthpdrain": attackdata6[12], "statutchance": attackdata6[10], "statut": attackdata6[9], "effectchance": attackdata6[8], "effet_txt": attackdata6[7],"prio": int(self.ui.attaqueprio_6.toPlainText()), "vit": vit6,"target": self.ui.cible_6.currentText(), "dmgfixe": attackdata6[16], "dmgpercent": attackdata6[17], "catchiante": attackdata6[18], "soinfixe": attackdata6[19]}

                    statut6 = {"fear":False, "burn":self.ui.effetbrule_6.isChecked(), "freeze":self.ui.effetgel_6.isChecked(), "para":self.ui.effetpara_6.isChecked(), "poison":self.ui.effetpoison_6.isChecked(), "sleep":self.ui.effetsommeil_6.isChecked(), "attraction":self.ui.effetattrac_6.isChecked(), "conf":self.ui.effetconfus_6.isChecked(), "maledi":self.ui.effetmaledi_6.isChecked(), "vampi":self.ui.vampicible_6.currentText(),"prio": int(self.ui.attaqueprio_6.toPlainText()), "vit": vit6, "deso": self.ui.effetdeso_6.isChecked(), "ident": self.ui.effetident_6.isChecked(), "piege":self.ui.effetpiege_6.isChecked(), "fightID": "C"}

                    allpkmon.append(pkmn6)
                    allattack.append(attck6)
                    allstatut.append(statut6)
                    advteam.append(pkmn6)

                if self.ui.init.isChecked():
                    if self.ui.fightwild.isChecked():
                        self.ui.outputrp.appendPlainText("[listL][i][color=#999999]Connexion au réseau en cours... ... ...\nSIS correctement relié au SNT - port "+str(random.randint(1000,9999))+".\nSimulation téléchargée...")
                        if self.ui.monday.isChecked():
                            self.ui.outputrp.appendPlainText("MONDAY 3.02 correctement initialisée.")
                        if self.ui.wednesday.isChecked():
                            self.ui.outputrp.appendPlainText("WEDNESDAY 2.78 correctement initialisée.")
                        if self.ui.friday.isChecked():
                            self.ui.outputrp.appendPlainText("FRIDAY 1.97 correctement initialisée.")
                        if self.ui.saturday.isChecked():
                            self.ui.outputrp.appendPlainText("SATURDAY 2.45 correctement initialisée.")
                        self.ui.outputrp.appendPlainText("\nPrésence détectée. Estimation en cours.[/color][/i][/listL]")
                        if len(advteam)==1:
                            self.ui.outputrp.appendPlainText("[center][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img]\nUn [b]"+advteam[0]["name"]+"[/b] sauvage vous attaque !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+"[/u])[/i][/size][/center]")
                        elif len(advteam)==2:
                            self.ui.outputrp.appendPlainText("[center][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[1]["id"])+".png[/img]\nUn [b]"+advteam[0]["name"]+"[/b] et un [b]"+advteam[1]["name"]+"[/b] sauvages vous attaquent !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+" et "+str(advteam[1]["lvl"])+"[/u])[/i][/size][/center]")
                        elif len(advteam)==3:
                            self.ui.outputrp.appendPlainText("[center][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[1]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[2]["id"])+".png[/img]\nUn [b]"+advteam[0]["name"]+"[/b], un [b]"+advteam[1]["name"]+"[/b] et un [b]"+advteam[2]["name"]+"[/b] sauvages vous attaquent !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+", "+str(advteam[1]["lvl"])+" et "+str(advteam[2]["lvl"])+"[/u])[/i][/size][/center]")
                        self.ui.outputrp.appendPlainText("\n[hr]")

                    if self.ui.fighttrainer.isChecked():
                        self.ui.outputrp.appendPlainText("[listL][i][color=#999999]Connexion au réseau en cours... ... ...\nSIS correctement relié au SNT - port "+str(random.randint(1000,9999))+".\nSimulation téléchargée...")
                        if self.ui.monday.isChecked():
                            self.ui.outputrp.appendPlainText("MONDAY 3.02 correctement initialisée.")
                        if self.ui.wednesday.isChecked():
                            self.ui.outputrp.appendPlainText("WEDNESDAY 2.78 correctement initialisée.")
                        if self.ui.friday.isChecked():
                            self.ui.outputrp.appendPlainText("FRIDAY 1.97 correctement initialisée.")
                        if self.ui.saturday.isChecked():
                            self.ui.outputrp.appendPlainText("SATURDAY 2.45 correctement initialisée.")
                        self.ui.outputrp.appendPlainText("\nCombat inter-dresseur détecté. Calcul en cours.[/color][/i][/listL][center][img]https://sunrise-db.yo.fr/Sprites/0.png[/img]\n[b]???[/b] veut se battre !\n[size=10]« J'vais t'casser en deux minable. Ta maman te reconnaîtra qu'à la couleur de ton p'tit cartable ! »[/size]\n")
                        if len(advteam)==1:
                            self.ui.outputrp.appendPlainText("[img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img]\n[b]???[/b] envoie au combat un [b]"+advteam[0]["name"]+"[/b] !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+"[/u])[/i][/size][/center]")
                        elif len(advteam)==2:
                            self.ui.outputrp.appendPlainText("[img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[1]["id"])+".png[/img]\n[b]???[/b] envoie au combat un [b]"+advteam[0]["name"]+"[/b] et un [b]"+advteam[1]["name"]+"[/b] !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+" et "+str(advteam[1]["lvl"])+"[/u])[/i][/size][/center]")
                        elif len(advteam)==3:
                            self.ui.outputrp.appendPlainText("[img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[0]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[1]["id"])+".png[/img][img]https://sunrise-db.yo.fr/Sprites/"+str(advteam[2]["id"])+".png[/img]\n[b]???[/b] Envoie au combat un [b]"+advteam[0]["name"]+"[/b], un [b]"+advteam[1]["name"]+"[/b] et un [b]"+advteam[2]["name"]+"[/b] !\n[size=10][i](Estimation de niveau : [u]"+str(advteam[0]["lvl"])+", "+str(advteam[1]["lvl"])+" et "+str(advteam[2]["lvl"])+"[/u])[/i][/size][/center]")
                        self.ui.outputrp.appendPlainText("\n[hr]")

                randomlist=[i for i in range(6)]
                random.shuffle(randomlist)
                for i in range(0,len(allpkmon)):
                    allpkmon[i]["randomorder"] = randomlist[i]
                    allattack[i]["randomorder"] = randomlist[i]
                    allstatut[i]["randomorder"] = randomlist[i]
                sortedpkmon = sorted(allpkmon, key=lambda d: (-d['prio'], -d['vit'], -d['randomorder']))
                sortedattack = sorted(allattack, key=lambda d: (-d['prio'], -d['vit'], -d['randomorder']))
                sortedstatut = sorted(allstatut, key=lambda d: (-d['prio'], -d['vit'], -d['randomorder']))
                indexedpkmon = self.build_dict(sortedpkmon,key="fightID")

                listid = [x["fightID"] for x in sortedpkmon]
                listidteam1 = [x for x in listid if x in ['1','2','3']]
                randomlist1 = listidteam1
                random.shuffle(randomlist1)
                listidteamA = [x for x in listid if x in ['A','B','C']]
                randomlistA = listidteamA
                random.shuffle(randomlistA)
                listtarget = [x["target"] for x in sortedattack]
                listid.extend(["Adversaires","Tous","Aléatoire","Team","/"])
                if all(x in listid for x in listtarget):
                    for index in range(0,len(sortedpkmon)):
                        if sortedpkmon[index]["ko"]==False:
                            if sortedattack[index]["catchiante"] not in ["Delete","attaque z"]:
                                if sortedattack[index]["target"]=="1":
                                    indexadv = [indexedpkmon["1"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlist1)):
                                            indexadv = [indexedpkmon[randomlist1[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="2":
                                    indexadv = [indexedpkmon["2"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlist1)):
                                            indexadv = [indexedpkmon[randomlist1[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="3":
                                    indexadv = [indexedpkmon["3"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlist1)):
                                            indexadv = [indexedpkmon[randomlist1[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="A":
                                    indexadv = [indexedpkmon["A"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlistA)):
                                            indexadv = [indexedpkmon[randomlistA[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="B":
                                    indexadv = [indexedpkmon["B"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlistA)):
                                            indexadv = [indexedpkmon[randomlistA[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="C":
                                    indexadv = [indexedpkmon["C"]["index"]]
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        for i in range(0,len(randomlistA)):
                                            indexadv = [indexedpkmon[randomlistA[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    if sortedpkmon[indexadv[0]]["ko"]:
                                        indexadv = None
                                elif sortedattack[index]["target"]=="Adversaires":
                                    if sortedpkmon[index]["fightID"] in ["1","2","3"]:
                                        indexadv = [indexedpkmon[x]["index"] for x in listidteamA]
                                    elif sortedpkmon[index]["fightID"] in ["A","B","C"]:
                                        indexadv = [indexedpkmon[x]["index"] for x in listidteam1]
                                    for i in indexadv:
                                        if sortedpkmon[i]["ko"]:
                                            indexadv.remove(i)
                                elif sortedattack[index]["target"]=="Tous":
                                    indexadv=list(range(0,len(sortedpkmon)))
                                    indexadv.remove(index)
                                elif sortedattack[index]["target"]=="Aléatoire":
                                    if sortedpkmon[index]["fightID"] in ["1","2","3"]:
                                        for i in range(0,len(randomlistA)):
                                            indexadv = [indexedpkmon[randomlistA[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                    elif sortedpkmon[index]["fightID"] in ["A","B","C"]:
                                        for i in range(0,len(randomlist1)):
                                            indexadv = [indexedpkmon[randomlist1[i]]["index"]]
                                            if sortedpkmon[indexadv[0]]["ko"]==False:
                                                break
                                elif sortedattack[index]["target"]=="Team":
                                    indexadv = None
                                    settarget = set(listid)
                                    if sortedpkmon[index]["fightID"] in ["1","2","3"]:
                                        list1=["1","2","3"]
                                    elif sortedpkmon[index]["fightID"] in ["A","B","C"]:
                                        list1=["A","B","C"]
                                    indexteam=[indexedpkmon[x]["index"] for x in [x for x in list1 if x in settarget]]
                                    self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]<img src='"+str(sortedpkmon[index]["sprite"])+"' style='max-width: 96px;max-height: 96px'>")
                                    self.ui.outputrp.appendPlainText("[b]"+sortedpkmon[index]["name"]+"[/b] utilise [u]"+sortedattack[index]["name"]+"[/u] !")
                                    for team in indexteam:
                                        if sortedstatut[team]["sleep"]:
                                            sortedstatut[team]["sleep"]=False
                                            self.ui.outputrp.appendPlainText("[i]{"+ sortedpkmon[team]["name"]+" se réveille !}[/i]")
                                        elif sortedstatut[team]["para"]:
                                            sortedstatut[team]["para"]=False
                                            self.ui.outputrp.appendPlainText("[i]{"+ sortedpkmon[team]["name"]+" n'est plus paralysé !}[/i]")
                                        elif sortedstatut[team]["poison"]:
                                            sortedstatut[team]["poison"]=False
                                            self.ui.outputrp.appendPlainText("[i]{"+ sortedpkmon[team]["name"]+" n'est plus empoisonné !}[/i]")
                                        elif sortedstatut[team]["burn"]:
                                            sortedstatut[team]["burn"]=False
                                            self.ui.outputrp.appendPlainText("[i]{"+ sortedpkmon[team]["name"]+" n'est plus brûlé !}[/i]")
                                        elif sortedstatut[team]["freeze"]:
                                            sortedstatut[team]["freeze"]=False
                                            self.ui.outputrp.appendPlainText("[i]{"+ sortedpkmon[team]["name"]+" n'est plus gelé !}[/i]")
                                        else:
                                            self.ui.outputrp.appendPlainText("[i]{Aucun effet sur "+ sortedpkmon[team]["name"]+".}[/i]")

                                elif sortedattack[index]["target"]=="/":
                                    indexadv = None
                                    self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]<img src='"+str(sortedpkmon[index]["sprite"])+"' style='max-width: 96px;max-height: 96px'>")
                                    self.ui.outputrp.appendPlainText("[b]"+sortedpkmon[index]["name"]+"[/b] utilise [u]"+sortedattack[index]["name"]+"[/u] !")
                                    self.ui.outputrp.appendPlainText("Attaque avec des effets particuliers à gérer à la main")
                                
                                if sortedattack[index]["name"]=="Rebondifeu":
                                    if sortedpkmon[index]["fightID"] in ["1","2","3"]:
                                        indexsplash = [indexedpkmon[x]["index"] for x in listidteamA]
                                    elif sortedpkmon[index]["fightID"] in ["A","B","C"]:
                                        indexsplash = [indexedpkmon[x]["index"] for x in listidteam1]
                                    for i in indexsplash:
                                        if sortedpkmon[i]["ko"]:
                                            indexsplash.remove(i)
                                    indexsplash.remove(indexadv[0])
                                else:
                                    indexsplash=[]
                                if indexadv!=None:
                                    indexadv.extend(indexsplash)

                                if indexadv==[]:
                                    indexadv=None
                                if indexadv != None:
                                    i=0
                                    self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]<img src='"+str(sortedpkmon[index]["sprite"])+"' style='max-width: 96px;max-height: 96px'>")
                                    block=False
                                    nosplash=False
                                    for adv in indexadv:
                                        if sortedpkmon[adv]["ko"]==False:
                                            i=i+1
                                            turn1=self.fight(sortedpkmon[index],sortedstatut[index],sortedattack[index],sortedpkmon[adv],sortedstatut[adv],i,len(indexadv),block,nosplash)
                                            sortedpkmon[index]=turn1["pkmon1"]
                                            sortedstatut[index]=turn1["statut1"]
                                            sortedpkmon[adv]=turn1["pkmon2"]
                                            sortedstatut[adv]=turn1["statut2"]
                                            block=turn1["block"]
                                            nosplash=turn1["nosplash"]
                                            if turn1["pkmon2"]["ko"] and turn1["pkmon2"]["fightID"] in ["A","B","C"]:
                                                    for j in range(0,len(sortedpkmon)):
                                                        if sortedpkmon[j]["fightID"] in ["1","2","3"]:
                                                            difflvl=turn1["pkmon2"]["lvl"]-sortedpkmon[j]["lvl"]
                                                            if difflvl>10:
                                                                difflvl=10
                                                            if difflvl<-10:
                                                                difflvl=-10
                                                            xp=50+(difflvl*5)
                                                            if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                                                xp=50
                                                            elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                                                xp=0
                                                            self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                                            elif turn1["pkmon2"]["ko"] and turn1["pkmon2"]["fightID"] in ["1","2","3"]:
                                                    for j in range(0,len(sortedpkmon)):
                                                        if sortedpkmon[j]["fightID"] in ["A","B","C"]:
                                                            difflvl=turn1["pkmon2"]["lvl"]-sortedpkmon[j]["lvl"]
                                                            if difflvl>10:
                                                                difflvl=10
                                                            if difflvl<-10:
                                                                difflvl=-10
                                                            xp=50+(difflvl*5)
                                                            if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                                                xp=50
                                                            elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                                                xp=0
                                                            self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                                            if turn1["pkmon1"]["ko"] and turn1["pkmon1"]["fightID"] in ["A","B","C"]:
                                                    for j in range(0,len(sortedpkmon)):
                                                        if sortedpkmon[j]["fightID"] in ["1","2","3"]:
                                                            difflvl=turn1["pkmon1"]["lvl"]-sortedpkmon[j]["lvl"]
                                                            if difflvl>10:
                                                                difflvl=10
                                                            if difflvl<-10:
                                                                difflvl=-10
                                                            xp=50+(difflvl*5)
                                                            if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                                                xp=50
                                                            elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                                                xp=0
                                                            self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                                            elif turn1["pkmon1"]["ko"] and turn1["pkmon1"]["fightID"] in ["1","2","3"]:
                                                    for j in range(0,len(sortedpkmon)):
                                                        if sortedpkmon[j]["fightID"] in ["A","B","C"]:
                                                            difflvl=turn1["pkmon1"]["lvl"]-sortedpkmon[j]["lvl"]
                                                            if difflvl>10:
                                                                difflvl=10
                                                            if difflvl<-10:
                                                                difflvl=-10
                                                            xp=50+(difflvl*5)
                                                            if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                                                xp=50
                                                            elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                                                xp=0
                                                            self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                                    self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")
                            else:
                                msgBox1 = QMessageBox()
                                msgBox1.setText("L'attaque choisie pour "+sortedpkmon[index]["name"]+" a été supprimée sur Sunrise.")
                                msgBox1.exec_()

                    for index in range(0,len(sortedpkmon)):
                        koinit=sortedpkmon[index]["ko"]
                        if sortedstatut[index]["vampi"] and sortedpkmon[index]["ko"]==False:
                            self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]")
                            vampidmg=round(sortedpkmon[index]["pvtotal"]/8)
                            newpv3=sortedpkmon[index]["pvcurrent"]-vampidmg
                            if newpv3<=0:
                                newpv3=0
                                sortedpkmon[index]["ko"]=True
                            self.ui.outputrp.appendPlainText("[i]{"+sortedpkmon[index]["name"]+" est blessé par vampigraine !}[/i]\n{[color=#ff0000][b]-"+str(vampidmg)+"[/b][/color]} PVs\n[i]PVs de [b]"+sortedpkmon[index]["name"]+"[/b][/i]: "+self.pvToColor(newpv3,sortedpkmon[index]["pvtotal"])+str(newpv3)+"[/color]/"+str(sortedpkmon[index]["pvtotal"]))
                            sortedpkmon[index]["pvcurrent"]=newpv3
                            if sortedstatut[index]["vampi"] in listid:
                                newpvcible=sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvcurrent"]+vampidmg
                                if newpvcible > sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvtotal"]:
                                    newpvcible = sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvtotal"]
                                sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvcurrent"]=newpvcible
                                self.ui.outputrp.appendPlainText('[i]PVs de [b]'+sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["name"]+'[/b][/i]: '+self.pvToColor(newpvcible,sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvtotal"])+str(newpvcible)+'[/color]/'+str(sortedpkmon[indexedpkmon[sortedstatut[index]["vampi"]]["index"]]["pvtotal"]))
                            else:
                                msgBox1 = QMessageBox()
                                msgBox1.setText('Attention, erreur de cible pour vampigraine: aucun Pokémon soigné.')
                                msgBox1.exec_()
                            self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")

                        if sortedstatut[index]["poison"] and sortedpkmon[index]["ko"]==False:
                            self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]")
                            poisondmg=round(sortedpkmon[index]["pvtotal"]/8)
                            newpv3=sortedpkmon[index]["pvcurrent"]-poisondmg
                            if newpv3<=0:
                                newpv3=0
                                sortedpkmon[index]["ko"]=True
                            self.ui.outputrp.appendPlainText("[i]{"+sortedpkmon[index]["name"]+" souffre du poison !}[/i]\n{[color=#ff0000][b]-"+str(poisondmg)+"[/b][/color]} PVs\n[i]PVs de [b]"+sortedpkmon[index]["name"]+"[/b][/i]: "+self.pvToColor(newpv3,sortedpkmon[index]["pvtotal"])+str(newpv3)+"[/color]/"+str(sortedpkmon[index]["pvtotal"]))
                            sortedpkmon[index]["pvcurrent"]=newpv3
                            self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")

                        if sortedstatut[index]["burn"] and sortedpkmon[index]["ko"]==False:
                            self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]")
                            burndmg=round(sortedpkmon[index]["pvtotal"]/16)
                            newpv3=sortedpkmon[index]["pvcurrent"]-burndmg
                            if newpv3<=0:
                                newpv3=0
                                sortedpkmon[index]["ko"]=True
                            self.ui.outputrp.appendPlainText("[i]{"+sortedpkmon[index]["name"]+" souffre de sa brûlure !}[/i]\n{[color=#ff0000][b]-"+str(burndmg)+"[/b][/color]} PVs\n[i]PVs de [b]"+sortedpkmon[index]["name"]+"[/b][/i]: "+self.pvToColor(newpv3,sortedpkmon[index]["pvtotal"])+str(newpv3)+"[/color]/"+str(sortedpkmon[index]["pvtotal"]))
                            sortedpkmon[index]["pvcurrent"]=newpv3
                            self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")

                        if sortedstatut[index]["maledi"] and sortedpkmon[index]["ko"]==False:
                            self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]")
                            maledidmg=round(sortedpkmon[index]["pvtotal"]/4)
                            newpv3=sortedpkmon[index]["pvcurrent"]-maledidmg
                            if newpv3<=0:
                                newpv3=0
                                sortedpkmon[index]["ko"]=True
                            self.ui.outputrp.appendPlainText("[i]{"+sortedpkmon[index]["name"]+" est blessé par la malédiction !}[/i]\n{[color=#ff0000][b]-"+str(maledidmg)+"[/b][/color]} PVs\n[i]PVs de [b]"+sortedpkmon[index]["name"]+"[/b][/i]: "+self.pvToColor(newpv3,sortedpkmon[index]["pvtotal"])+str(newpv3)+"[/color]/"+str(sortedpkmon[index]["pvtotal"]))
                            sortedpkmon[index]["pvcurrent"]=newpv3
                            self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")

                        if sortedstatut[index]["piege"] and sortedpkmon[index]["ko"]==False:
                            self.ui.outputrp.appendPlainText("["+sortedpkmon[index]["side"]+"]")
                            piegedmg=round(sortedpkmon[index]["pvtotal"]/8)
                            newpv3=sortedpkmon[index]["pvcurrent"]-piegedmg
                            if newpv3<=0:
                                newpv3=0
                                sortedpkmon[index]["ko"]=True
                            self.ui.outputrp.appendPlainText("[i]{"+sortedpkmon[index]["name"]+" est blessé par un piège !}[/i]\n{[color=#ff0000][b]-"+str(piegedmg)+"[/b][/color]} PVs\n[i]PVs de [b]"+sortedpkmon[index]["name"]+"[/b][/i]: "+self.pvToColor(newpv3,sortedpkmon[index]["pvtotal"])+str(newpv3)+"[/color]/"+str(sortedpkmon[index]["pvtotal"]))
                            sortedpkmon[index]["pvcurrent"]=newpv3
                            self.ui.outputrp.appendPlainText("[/"+sortedpkmon[index]["side"]+"]")

                        if koinit==False and sortedpkmon[index]["ko"] and sortedpkmon[index]["fightID"] in ["A","B","C"]:
                            self.ui.outputrp.appendPlainText("[center]<img src='"+str(sortedpkmon[index]["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(sortedpkmon[index]["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")
                            for j in range(0,len(sortedpkmon)):
                                if sortedpkmon[j]["fightID"] in ["1","2","3"]:
                                    difflvl=sortedpkmon[index]["lvl"]-sortedpkmon[j]["lvl"]
                                    if difflvl>10:
                                        difflvl=10
                                    if difflvl<-10:
                                        difflvl=-10
                                    xp=50+(difflvl*5)
                                    if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                        xp=50
                                    elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                        xp=0
                                    self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                        elif koinit==False and sortedpkmon[index]["ko"] and sortedpkmon[index]["fightID"] in ["1","2","3"]:
                            self.ui.outputrp.appendPlainText("[center]<img src='"+str(sortedpkmon[index]["sprite"])+"' style='max-width: 96px;max-height: 96px'>\n[i]{"+str(sortedpkmon[index]["name"])+" est K.O !}[/i]\n[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color][/center]")
                            for j in range(0,len(sortedpkmon)):
                                if sortedpkmon[j]["fightID"] in ["A","B","C"]:
                                    difflvl=sortedpkmon[index]["lvl"]-sortedpkmon[j]["lvl"]
                                    if difflvl>10:
                                        difflvl=10
                                    if difflvl<-10:
                                        difflvl=-10
                                    xp=50+(difflvl*5)
                                    if sortedpkmon[j]["lvl"]<20 and difflvl>=-5:
                                        xp=50
                                    elif sortedpkmon[j]["lvl"]<20 and difflvl<-5:
                                        xp=0
                                    self.ui.outputrp.appendPlainText("[center][b]"+sortedpkmon[j]["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP ![/center]")
                    
                    resortedpkmon=sorted(sortedpkmon,key=lambda tmp: tmp["fightID"])
                    resortedstatut=sorted(sortedstatut,key=lambda tmp: tmp["fightID"])
                    globalstatutcode=[]
                    idlist=[]
                    for p in range(0,len(resortedpkmon)):
                        self.ui.outputmodo.append("Code "+resortedpkmon[p]["fightID"]+" : "+resortedpkmon[p]["trainer"]+" - "+resortedpkmon[p]["name"]+" - "+resortedpkmon[p]["realname"]+" - "+str(resortedpkmon[p]["lvl"])+" - "+str(resortedpkmon[p]["pvcurrent"])+"/"+str(resortedpkmon[p]["pvtotal"])+" - "+str(resortedpkmon[p]["att"])+"x"+str(resortedpkmon[p]["def"])+"x"+str(resortedpkmon[p]["atts"])+"x"+str(resortedpkmon[p]["defs"])+"x"+str(resortedpkmon[p]["truevit"])+" - Attaque")
                        statstxt=resortedpkmon[p]["name"]+" :"
                        statutcodetxt=""
                        idlist.append(resortedpkmon[p]["fightID"])

                        if int(resortedpkmon[p]["modifatt"])!=0:
                            statstxt=statstxt+" modif attaque "+str(resortedpkmon[p]["modifatt"])+","
                            if resortedpkmon[p]["modifatt"]>0:
                                statutcodetxt=statutcodetxt+"A0"+str(resortedpkmon[p]["modifatt"])
                            elif resortedpkmon[p]["modifatt"]==-1:
                                statutcodetxt=statutcodetxt+"A07"
                            elif resortedpkmon[p]["modifatt"]==-2:
                                statutcodetxt=statutcodetxt+"A08"
                            elif resortedpkmon[p]["modifatt"]==-3:
                                statutcodetxt=statutcodetxt+"A09"
                            elif resortedpkmon[p]["modifatt"]==-4:
                                statutcodetxt=statutcodetxt+"A10"
                            elif resortedpkmon[p]["modifatt"]==-5:
                                statutcodetxt=statutcodetxt+"A11"
                            elif resortedpkmon[p]["modifatt"]==-6:
                                statutcodetxt=statutcodetxt+"A12"
                        if int(resortedpkmon[p]["modifdef"])!=0:
                            statstxt=statstxt+" modif defense "+str(resortedpkmon[p]["modifdef"])+","
                            if resortedpkmon[p]["modifdef"]>0:
                                statutcodetxt=statutcodetxt+"D0"+str(resortedpkmon[p]["modifdef"])
                            elif resortedpkmon[p]["modifdef"]==-1:
                                statutcodetxt=statutcodetxt+"D07"
                            elif resortedpkmon[p]["modifdef"]==-2:
                                statutcodetxt=statutcodetxt+"D08"
                            elif resortedpkmon[p]["modifdef"]==-3:
                                statutcodetxt=statutcodetxt+"D09"
                            elif resortedpkmon[p]["modifdef"]==-4:
                                statutcodetxt=statutcodetxt+"D10"
                            elif resortedpkmon[p]["modifdef"]==-5:
                                statutcodetxt=statutcodetxt+"D11"
                            elif resortedpkmon[p]["modifdef"]==-6:
                                statutcodetxt=statutcodetxt+"D12"
                        if int(resortedpkmon[p]["modifatts"])!=0:
                            statstxt=statstxt+" modif attaque spé "+str(resortedpkmon[p]["modifatts"])+","
                            if resortedpkmon[p]["modifatts"]>0:
                                statutcodetxt=statutcodetxt+"S0"+str(resortedpkmon[p]["modifatt"])
                            elif resortedpkmon[p]["modifatts"]==-1:
                                statutcodetxt=statutcodetxt+"S07"
                            elif resortedpkmon[p]["modifatts"]==-2:
                                statutcodetxt=statutcodetxt+"S08"
                            elif resortedpkmon[p]["modifatts"]==-3:
                                statutcodetxt=statutcodetxt+"S09"
                            elif resortedpkmon[p]["modifatts"]==-4:
                                statutcodetxt=statutcodetxt+"S10"
                            elif resortedpkmon[p]["modifatts"]==-5:
                                statutcodetxt=statutcodetxt+"S11"
                            elif resortedpkmon[p]["modifatts"]==-6:
                                statutcodetxt=statutcodetxt+"S12"
                        if int(resortedpkmon[p]["modifdefs"])!=0:
                            statstxt=statstxt+" modif defense spé "+str(resortedpkmon[p]["modifdefs"])+","
                            if resortedpkmon[p]["modifdefs"]>0:
                                statutcodetxt=statutcodetxt+"F0"+str(resortedpkmon[p]["modifdefs"])
                            elif resortedpkmon[p]["modifdefs"]==-1:
                                statutcodetxt=statutcodetxt+"F07"
                            elif resortedpkmon[p]["modifdefs"]==-2:
                                statutcodetxt=statutcodetxt+"F08"
                            elif resortedpkmon[p]["modifdefs"]==-3:
                                statutcodetxt=statutcodetxt+"F09"
                            elif resortedpkmon[p]["modifdefs"]==-4:
                                statutcodetxt=statutcodetxt+"F10"
                            elif resortedpkmon[p]["modifdefs"]==-5:
                                statutcodetxt=statutcodetxt+"F11"
                            elif resortedpkmon[p]["modifdefs"]==-6:
                                statutcodetxt=statutcodetxt+"F12"
                        if int(resortedpkmon[p]["modifvit"])!=0:
                            statstxt=statstxt+" modif vitesse "+str(resortedpkmon[p]["modifvit"])+","
                            if resortedpkmon[p]["modifvit"]>0:
                                statutcodetxt=statutcodetxt+"T0"+str(resortedpkmon[p]["modifvit"])
                            elif resortedpkmon[p]["modifvit"]==-1:
                                statutcodetxt=statutcodetxt+"T07"
                            elif resortedpkmon[p]["modifvit"]==-2:
                                statutcodetxt=statutcodetxt+"T08"
                            elif resortedpkmon[p]["modifvit"]==-3:
                                statutcodetxt=statutcodetxt+"T09"
                            elif resortedpkmon[p]["modifvit"]==-4:
                                statutcodetxt=statutcodetxt+"T10"
                            elif resortedpkmon[p]["modifvit"]==-5:
                                statutcodetxt=statutcodetxt+"T11"
                            elif resortedpkmon[p]["modifvit"]==-6:
                                statutcodetxt=statutcodetxt+"T12"
                        if int(resortedpkmon[p]["modifesquive"])!=0:
                            statstxt=statstxt+" modif esquive "+str(resortedpkmon[p]["modifesquive"])+","
                            if resortedpkmon[p]["modifesquive"]>0:
                                statutcodetxt=statutcodetxt+"E0"+str(resortedpkmon[p]["modifesquive"])
                            elif resortedpkmon[p]["modifesquive"]==-1:
                                statutcodetxt=statutcodetxt+"E07"
                            elif resortedpkmon[p]["modifesquive"]==-2:
                                statutcodetxt=statutcodetxt+"E08"
                            elif resortedpkmon[p]["modifesquive"]==-3:
                                statutcodetxt=statutcodetxt+"E09"
                            elif resortedpkmon[p]["modifesquive"]==-4:
                                statutcodetxt=statutcodetxt+"E10"
                            elif resortedpkmon[p]["modifesquive"]==-5:
                                statutcodetxt=statutcodetxt+"E11"
                            elif resortedpkmon[p]["modifesquive"]==-6:
                                statutcodetxt=statutcodetxt+"E12"
                        if int(resortedpkmon[p]["modifprec"])!=0:
                            statstxt=statstxt+" modif précision "+str(resortedpkmon[p]["modifprec"])+","
                            if resortedpkmon[p]["modifprec"]>0:
                                statutcodetxt=statutcodetxt+"P0"+str(resortedpkmon[p]["modifprec"])
                            elif resortedpkmon[p]["modifprec"]==-1:
                                statutcodetxt=statutcodetxt+"P07"
                            elif resortedpkmon[p]["modifprec"]==-2:
                                statutcodetxt=statutcodetxt+"P08"
                            elif resortedpkmon[p]["modifprec"]==-3:
                                statutcodetxt=statutcodetxt+"P09"
                            elif resortedpkmon[p]["modifprec"]==-4:
                                statutcodetxt=statutcodetxt+"P10"
                            elif resortedpkmon[p]["modifprec"]==-5:
                                statutcodetxt=statutcodetxt+"P11"
                            elif resortedpkmon[p]["modifprec"]==-6:
                                statutcodetxt=statutcodetxt+"P12"

                        if int(resortedpkmon[p]["modifatt"])!=0 or int(resortedpkmon[p]["modifdef"])!=0 or int(resortedpkmon[p]["modifatts"])!=0 or int(resortedpkmon[p]["modifdefs"])!=0 or int(resortedpkmon[p]["modifvit"])!=0 or int(resortedpkmon[p]["modifesquive"])!=0 or int(resortedpkmon[p]["modifprec"])!=0:
                            statstxt = statstxt[:-1]
                            self.ui.outputmodo.append(statstxt)
                        statuttxt=resortedpkmon[p]["name"]+" :"
                        if resortedstatut[p]["burn"]:
                            statuttxt=statuttxt+" brûlure,"
                            statutcodetxt=statutcodetxt+"BRL"
                        if resortedstatut[p]["freeze"]:
                            statuttxt=statuttxt+" gel,"
                            statutcodetxt=statutcodetxt+"GEL"
                        if resortedstatut[p]["para"]:
                            statuttxt=statuttxt+" paralysie,"
                            statutcodetxt=statutcodetxt+"PAR"
                        if resortedstatut[p]["poison"]:
                            statuttxt=statuttxt+" poison,"
                            statutcodetxt=statutcodetxt+"PSN"
                        if resortedstatut[p]["sleep"]:
                            statuttxt=statuttxt+" sommeil pour ?? tours,"
                            statutcodetxt=statutcodetxt+"SLP"
                        if resortedstatut[p]["attraction"]:
                            statuttxt=statuttxt+" attraction,"
                            statutcodetxt=statutcodetxt+"ACN"
                        if resortedstatut[p]["conf"]:
                            statuttxt=statuttxt+" confus pour ?? tours,"
                            statutcodetxt=statutcodetxt+"CNF"
                        if resortedstatut[p]["maledi"]:
                            statuttxt=statuttxt+" malédiction,"
                            statutcodetxt=statutcodetxt+"MAL"
                        if resortedstatut[p]["vampi"]:
                            statuttxt=statuttxt+" vampigraine,"
                            statutcodetxt=statutcodetxt+"V"+str(resortedstatut[p]["vampi"])
                        if resortedstatut[p]["piege"]:
                            statuttxt=statuttxt+" piégé pour ?? tours,"
                            statutcodetxt=statutcodetxt+"PIG"
                        if resortedstatut[p]["burn"] or resortedstatut[p]["freeze"] or resortedstatut[p]["para"] or resortedstatut[p]["poison"] or resortedstatut[p]["sleep"] or resortedstatut[p]["attraction"] or resortedstatut[p]["conf"] or resortedstatut[p]["maledi"] or resortedstatut[p]["vampi"] or resortedstatut[p]["piege"]:
                            statuttxt = statuttxt[:-1]
                            self.ui.outputmodo.append(statuttxt)
                        if statutcodetxt=="":
                            statutcodetxt="NA"
                        globalstatutcode.append(statutcodetxt)
                    if "1" not in idlist:
                        globalstatutcode.insert(0,"NA")
                    if "2" not in idlist:
                        globalstatutcode.insert(1,"NA")
                    if "3" not in idlist:
                        globalstatutcode.insert(2,"NA")
                    if "A" not in idlist:
                        globalstatutcode.insert(3,"NA")
                    if "B" not in idlist:
                        globalstatutcode.insert(4,"NA")
                    if "C" not in idlist:
                        globalstatutcode.insert(5,"NA")
                    sep="-"
                    globalstatutcode2=sep.join(globalstatutcode)
                    self.ui.outputmodo.append("Code statut: "+globalstatutcode2)

                    if self.ui.captureauto.isChecked():
                        indexedpkmon2 = self.build_dict(sortedpkmon,key="fightID")
                        indexedstatut = self.build_dict(sortedstatut,key="fightID")
                        target=self.ui.ciblecapture.currentText()
                        if target=="A" and self.ui.poke_2.toPlainText()=="":
                            msgBox1 = QMessageBox()
                            msgBox1.setText("Impossible de capturer le Pokémon A : pas d'informations")
                            msgBox1.exec_()
                        elif target=="B" and self.ui.poke_4.toPlainText()=="":
                            msgBox1 = QMessageBox()
                            msgBox1.setText("Impossible de capturer le Pokémon B : pas d'informations")
                            msgBox1.exec_()
                        elif target=="C" and self.ui.poke_6.toPlainText()=="":
                            msgBox1 = QMessageBox()
                            msgBox1.setText("Impossible de capturer le Pokémon C : pas d'informations")
                            msgBox1.exec_()
                        else:
                            poke=indexedpkmon2[target]["realname"]
                            pv=indexedpkmon2[target]["pvcurrent"]
                            pvmax=indexedpkmon2[target]["pvtotal"]
                            lvl=indexedpkmon2[target]["lvl"]
                            capturestatut1=indexedstatut[target]["poison"] or indexedstatut[target]["burn"] or indexedstatut[target]["para"]
                            capturestatut2=indexedstatut[target]["freeze"] or indexedstatut[target]["sleep"]

                            c.execute('SELECT * FROM pokemons WHERE nom=?',(poke,))
                            pokedata=c.fetchall()[0]
                            pokeid=int(pokedata[0])
                            pokename=pokedata[1]
                            taux_capture=int(pokedata[10])
                            ball=self.ui.ballcapture_2.currentText()

                            if capturestatut1:
                                st1bonus=1.5
                            else:
                                st1bonus=1
                            if capturestatut2:
                                st2bonus=2.5
                            else:
                                st2bonus=1
                            if self.ui.ball.isChecked():
                                if ball=="Poké Ball":
                                    ballbonus=1
                                elif ball=="Super Ball":
                                    ballbonus=1.5
                                elif ball=="Hyper Ball":
                                    ballbonus=2
                            elif self.ui.modifball.isChecked():
                                ball="???"
                                ballbonus=self.ui.modifballvalue.value()

                            a=((((3*pvmax) - (2*pv)) * taux_capture * ballbonus)/(3*pvmax)) * (st1bonus*st2bonus)
                            b = 65536 / ((255/a)**0.1875)
                            resultcapture="[center][img]https://sunrise-db.yo.fr/Sunrise_Champions/Secretchamp.png[/img]\n[spoiler=??? utilise une "+ball+" !]"
                            j=0
                            for i in [0,1,2,3]:
                                j=j+1
                                checkvalue = random.randint(0,65536)
                                if checkvalue < b:
                                    if j==1:
                                        resultcapture=resultcapture+"\n[spoiler=...]"
                                    elif j==2:
                                        resultcapture=resultcapture+"\n[spoiler=... ...]"
                                    elif j==3:
                                        resultcapture=resultcapture+"\n[spoiler=... ... ...]"
                                    else:
                                        resultcapture=resultcapture+"\n[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nFélicitations ! "+pokename+" est capturé !\nIl est [u]niveau "+str(lvl)+"[/u] et prêt à se battre ![/spoiler][/spoiler][/spoiler][/spoiler][/center]"
                                else:
                                    if j==1:
                                        resultcapture=resultcapture+"\n[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nOh, non ! "+pokename+" s'est libéré ![/spoiler][/center]"
                                    if j==2:
                                        resultcapture=resultcapture+"\n[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nRaaah ! Ça y était presque ![/spoiler][/spoiler][/center]"
                                    if j==3:
                                        resultcapture=resultcapture+"\n[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nAaaaah ! Presque ![/spoiler][/spoiler][/spoiler][/center]"
                                    if j==4:
                                        resultcapture=resultcapture+"\n[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nMince ! Ça y était presque ![/spoiler][/spoiler][/spoiler][/spoiler][/center]"
                                    break

                            if "est capturé" in resultcapture:
                                self.ui.outputrp.appendPlainText(resultcapture.replace("[/spoiler]","").replace("[/center]",""))
                                self.ui.outputrp.appendPlainText("[color=#777777][size=10]Mise à jour des informations de statistiques en cours... ... ...[/size][/color]")
                                for pokemon in niceteam:
                                    difflvl=int(lvl)-pokemon["lvl"]
                                    if difflvl>10:
                                        difflvl=10
                                    if difflvl<-10:
                                        difflvl=-10
                                    xp=50+(difflvl*5)
                                    if pokemon["lvl"]<20 and difflvl>=-5:
                                        xp=50
                                    elif pokemon["lvl"]<20 and difflvl<-5:
                                        xp=0
                                    self.ui.outputrp.appendPlainText("[b]"+pokemon["name"]+"[/b] gagne [u]"+str(xp)+"[/u] points d'XP !")
                                self.ui.outputrp.appendPlainText("[/spoiler][/spoiler][/spoiler][/spoiler][/center]")
                            else:
                                self.ui.outputrp.appendPlainText(resultcapture)
                    
                    allko=0
                    howmany=0
                    for p in sortedpkmon:
                        if p["fightID"] in ["A","B","C"]:
                            allko=allko+p["ko"]
                            howmany=howmany+1
                    if self.ui.fighttrainer.isChecked() and allko==howmany:
                        self.ui.outputrp.appendPlainText("[hr]\n[listL][center][img]https://sunrise-db.yo.fr/Sprites/0.png[/img]\nVous avez battu [b]???[/b] !\n[size=10]« Noooooooooon »[/size]\nVous gagnez ???[img]https://i93.servimg.com/u/f93/20/08/72/05/pok-do10.png[/img] pour ce combat ![/center][/listL]")
                    self.ui.outputrp.appendPlainText("[hr]")
                    self.ui.outputrp.appendPlainText("[color=#999999][i]Et maintenant, [b]Dresseur[/b], quelle est la prochaine étape ?[/i][/color]")
                    self.ui.outputmodo.append('[/code][/spoiler][/modo]')

                else:
                    msgBox1 = QMessageBox()
                    msgBox1.setText('Un pokemon sans informations est ciblé !')
                    msgBox1.exec_()
        except:
            msgBox1 = QMessageBox()
            msgBox1.setText('Il y a une erreur quelque part !')
            msgBox1.exec_()


    def clearFun1(self):
        self.ui.pokedex.setCurrentIndex(0)
        self.ui.trainer.clear()
        self.ui.attackdex.clear()
        self.ui.customdatabar.clear()
        self.ui.poke.clear()
        self.ui.attaque.clear()
        self.ui.pokename.clear()
        self.ui.poketype1.clear()
        self.ui.poketype2.clear()
        self.ui.pokelvl.clear()
        self.ui.attaquetype.clear()
        self.ui.attaqueclasse.clear()
        self.ui.attaquepuiss.clear()
        self.ui.attaqueprio.clear()
        self.ui.attaqueprec.clear()
        self.ui.modifprec.setValue(0)
        self.ui.spinlvl.setValue(0)
        self.ui.cible.clear()
        self.ui.pvcurrent.clear()
        self.ui.pvtotal.clear()
        self.ui.att.clear()
        self.ui.defen.clear()
        self.ui.atts.clear()
        self.ui.defs.clear()
        self.ui.vit.clear()
        self.ui.modifatt.setValue(0)
        self.ui.modifdefen.setValue(0)
        self.ui.modifatts.setValue(0)
        self.ui.modifdefs.setValue(0)
        self.ui.modifvit.setValue(0)
        self.ui.modifesquive.setValue(0)
        self.ui.effetbrule.setChecked(False)
        self.ui.effetgel.setChecked(False)
        self.ui.effetpara.setChecked(False)
        self.ui.effetpiege.setChecked(False)
        self.ui.effetpoison.setChecked(False)
        self.ui.effetsommeil.setChecked(False)
        self.ui.effetattrac.setChecked(False)
        self.ui.effetident.setChecked(False)
        self.ui.effetconfus.setChecked(False)
        self.ui.effetmaledi.setChecked(False)
        self.ui.effetdeso.setChecked(False)
        self.ui.vampicible.setCurrentIndex(-1)

    def clearFun2(self):
        self.ui.pokedex_2.setCurrentIndex(0)
        self.ui.trainer_2.clear()
        self.ui.attackdex_2.clear()
        self.ui.customdatabar_2.clear()
        self.ui.poke_2.clear()
        self.ui.attaque_2.clear()
        self.ui.pokename_2.clear()
        self.ui.poketype1_2.clear()
        self.ui.poketype2_2.clear()
        self.ui.pokelvl_2.clear()
        self.ui.attaquetype_2.clear()
        self.ui.attaqueclasse_2.clear()
        self.ui.attaquepuiss_2.clear()
        self.ui.attaqueprio_2.clear()
        self.ui.attaqueprec_2.clear()
        self.ui.modifprec_2.setValue(0)
        self.ui.spinlvl_2.setValue(0)
        self.ui.cible_2.clear()
        self.ui.pvcurrent_2.clear()
        self.ui.pvtotal_2.clear()
        self.ui.att_2.clear()
        self.ui.defen_2.clear()
        self.ui.atts_2.clear()
        self.ui.defs_2.clear()
        self.ui.vit_2.clear()
        self.ui.modifatt_2.setValue(0)
        self.ui.modifdefen_2.setValue(0)
        self.ui.modifatts_2.setValue(0)
        self.ui.modifdefs_2.setValue(0)
        self.ui.modifvit_2.setValue(0)
        self.ui.modifesquive_2.setValue(0)
        self.ui.effetbrule_2.setChecked(False)
        self.ui.effetgel_2.setChecked(False)
        self.ui.effetpara_2.setChecked(False)
        self.ui.effetpiege_2.setChecked(False)
        self.ui.effetpoison_2.setChecked(False)
        self.ui.effetsommeil_2.setChecked(False)
        self.ui.effetattrac_2.setChecked(False)
        self.ui.effetident_2.setChecked(False)
        self.ui.effetconfus_2.setChecked(False)
        self.ui.effetmaledi_2.setChecked(False)
        self.ui.effetdeso_2.setChecked(False)
        self.ui.vampicible_2.setCurrentIndex(-1)

    def clearFun3(self):
        self.ui.pokedex_3.setCurrentIndex(0)
        self.ui.trainer_3.clear()
        self.ui.attackdex_3.clear()
        self.ui.customdatabar_3.clear()
        self.ui.poke_3.clear()
        self.ui.attaque_3.clear()
        self.ui.pokename_3.clear()
        self.ui.poketype1_3.clear()
        self.ui.poketype2_3.clear()
        self.ui.pokelvl_3.clear()
        self.ui.attaquetype_3.clear()
        self.ui.attaqueclasse_3.clear()
        self.ui.attaquepuiss_3.clear()
        self.ui.attaqueprio_3.clear()
        self.ui.attaqueprec_3.clear()
        self.ui.modifprec_3.setValue(0)
        self.ui.spinlvl_3.setValue(0)
        self.ui.cible_3.clear()
        self.ui.pvcurrent_3.clear()
        self.ui.pvtotal_3.clear()
        self.ui.att_3.clear()
        self.ui.defen_3.clear()
        self.ui.atts_3.clear()
        self.ui.defs_3.clear()
        self.ui.vit_3.clear()
        self.ui.modifatt_3.setValue(0)
        self.ui.modifdefen_3.setValue(0)
        self.ui.modifatts_3.setValue(0)
        self.ui.modifdefs_3.setValue(0)
        self.ui.modifvit_3.setValue(0)
        self.ui.modifesquive_3.setValue(0)
        self.ui.effetbrule_3.setChecked(False)
        self.ui.effetgel_3.setChecked(False)
        self.ui.effetpara_3.setChecked(False)
        self.ui.effetpiege_3.setChecked(False)
        self.ui.effetpoison_3.setChecked(False)
        self.ui.effetsommeil_3.setChecked(False)
        self.ui.effetattrac_3.setChecked(False)
        self.ui.effetident_3.setChecked(False)
        self.ui.effetconfus_3.setChecked(False)
        self.ui.effetmaledi_3.setChecked(False)
        self.ui.effetdeso_3.setChecked(False)
        self.ui.vampicible_3.setCurrentIndex(-1)

    def clearFun4(self):
        self.ui.pokedex_4.setCurrentIndex(0)
        self.ui.trainer_4.clear()
        self.ui.attackdex_4.clear()
        self.ui.customdatabar_4.clear()
        self.ui.poke_4.clear()
        self.ui.attaque_4.clear()
        self.ui.pokename_4.clear()
        self.ui.poketype1_4.clear()
        self.ui.poketype2_4.clear()
        self.ui.pokelvl_4.clear()
        self.ui.attaquetype_4.clear()
        self.ui.attaqueclasse_4.clear()
        self.ui.attaquepuiss_4.clear()
        self.ui.attaqueprio_4.clear()
        self.ui.attaqueprec_4.clear()
        self.ui.modifprec_4.setValue(0)
        self.ui.spinlvl_4.setValue(0)
        self.ui.cible_4.clear()
        self.ui.pvcurrent_4.clear()
        self.ui.pvtotal_4.clear()
        self.ui.att_4.clear()
        self.ui.defen_4.clear()
        self.ui.atts_4.clear()
        self.ui.defs_4.clear()
        self.ui.vit_4.clear()
        self.ui.modifatt_4.setValue(0)
        self.ui.modifdefen_4.setValue(0)
        self.ui.modifatts_4.setValue(0)
        self.ui.modifdefs_4.setValue(0)
        self.ui.modifvit_4.setValue(0)
        self.ui.modifesquive_4.setValue(0)
        self.ui.effetbrule_4.setChecked(False)
        self.ui.effetgel_4.setChecked(False)
        self.ui.effetpara_4.setChecked(False)
        self.ui.effetpiege_4.setChecked(False)
        self.ui.effetpoison_4.setChecked(False)
        self.ui.effetsommeil_4.setChecked(False)
        self.ui.effetattrac_4.setChecked(False)
        self.ui.effetident_4.setChecked(False)
        self.ui.effetconfus_4.setChecked(False)
        self.ui.effetmaledi_4.setChecked(False)
        self.ui.effetdeso_4.setChecked(False)
        self.ui.vampicible_4.setCurrentIndex(-1)

    def clearFun5(self):
        self.ui.pokedex_5.setCurrentIndex(0)
        self.ui.trainer_5.clear()
        self.ui.attackdex_5.clear()
        self.ui.customdatabar_5.clear()
        self.ui.poke_5.clear()
        self.ui.attaque_5.clear()
        self.ui.pokename_5.clear()
        self.ui.poketype1_5.clear()
        self.ui.poketype2_5.clear()
        self.ui.pokelvl_5.clear()
        self.ui.attaquetype_5.clear()
        self.ui.attaqueclasse_5.clear()
        self.ui.attaquepuiss_5.clear()
        self.ui.attaqueprio_5.clear()
        self.ui.attaqueprec_5.clear()
        self.ui.modifprec_5.setValue(0)
        self.ui.spinlvl_5.setValue(0)
        self.ui.cible_5.clear()
        self.ui.pvcurrent_5.clear()
        self.ui.pvtotal_5.clear()
        self.ui.att_5.clear()
        self.ui.defen_5.clear()
        self.ui.atts_5.clear()
        self.ui.defs_5.clear()
        self.ui.vit_5.clear()
        self.ui.modifatt_5.setValue(0)
        self.ui.modifdefen_5.setValue(0)
        self.ui.modifatts_5.setValue(0)
        self.ui.modifdefs_5.setValue(0)
        self.ui.modifvit_5.setValue(0)
        self.ui.modifesquive_5.setValue(0)
        self.ui.effetbrule_5.setChecked(False)
        self.ui.effetgel_5.setChecked(False)
        self.ui.effetpara_5.setChecked(False)
        self.ui.effetpiege_5.setChecked(False)
        self.ui.effetpoison_5.setChecked(False)
        self.ui.effetsommeil_5.setChecked(False)
        self.ui.effetattrac_5.setChecked(False)
        self.ui.effetident_5.setChecked(False)
        self.ui.effetconfus_5.setChecked(False)
        self.ui.effetmaledi_5.setChecked(False)
        self.ui.effetdeso_5.setChecked(False)
        self.ui.vampicible_5.setCurrentIndex(-1)

    def clearFun6(self):
        self.ui.pokedex_6.setCurrentIndex(0)
        self.ui.trainer_6.clear()
        self.ui.attackdex_6.clear()
        self.ui.customdatabar_6.clear()
        self.ui.poke_6.clear()
        self.ui.attaque_6.clear()
        self.ui.pokename_6.clear()
        self.ui.poketype1_6.clear()
        self.ui.poketype2_6.clear()
        self.ui.pokelvl_6.clear()
        self.ui.attaquetype_6.clear()
        self.ui.attaqueclasse_6.clear()
        self.ui.attaquepuiss_6.clear()
        self.ui.attaqueprio_6.clear()
        self.ui.attaqueprec_6.clear()
        self.ui.modifprec_6.setValue(0)
        self.ui.spinlvl_6.setValue(0)
        self.ui.cible_6.clear()
        self.ui.pvcurrent_6.clear()
        self.ui.pvtotal_6.clear()
        self.ui.att_6.clear()
        self.ui.defen_6.clear()
        self.ui.atts_6.clear()
        self.ui.defs_6.clear()
        self.ui.vit_6.clear()
        self.ui.modifatt_6.setValue(0)
        self.ui.modifdefen_6.setValue(0)
        self.ui.modifatts_6.setValue(0)
        self.ui.modifdefs_6.setValue(0)
        self.ui.modifvit_6.setValue(0)
        self.ui.modifesquive_6.setValue(0)
        self.ui.effetbrule_6.setChecked(False)
        self.ui.effetgel_6.setChecked(False)
        self.ui.effetpara_6.setChecked(False)
        self.ui.effetpiege_6.setChecked(False)
        self.ui.effetpoison_6.setChecked(False)
        self.ui.effetsommeil_6.setChecked(False)
        self.ui.effetattrac_6.setChecked(False)
        self.ui.effetident_6.setChecked(False)
        self.ui.effetconfus_6.setChecked(False)
        self.ui.effetmaledi_6.setChecked(False)
        self.ui.effetdeso_6.setChecked(False)
        self.ui.vampicible_6.setCurrentIndex(-1)

    def clearFunAll(self):
        self.ui.outputrp.clear()
        self.ui.outputmodo.clear()
        self.ui.outputattack.clear()
        self.clearFun1()
        self.clearFun2()
        self.clearFun3()
        self.clearFun4()
        self.clearFun5()
        self.clearFun6()

    def rolldice(self):
        nbface=self.ui.diceface.currentText()
        if nbface=="D100":
            max=100
        if nbface=="D20":
            max=20
        if nbface=="D6":
            max=6
        result=random.randint(1,max)
        self.ui.diceresult.setText(str(result))

    def pokegen(self):
        if self.ui.methode.currentText()!="":
            self.ui.outputgen.clear()
            continent=self.ui.continent.currentText()
            region=self.ui.region.currentText()
            zone=self.ui.zone.currentText()
            methode=self.ui.methode.currentText()
            lvl=self.ui.advlvl.value()
            nb=self.ui.nbgen.value()
            c2.execute('SELECT Zone_id FROM SunnyData_zones WHERE Continent=? AND Region=? AND Zone=?',(continent,region,zone))
            zoneid=c2.fetchone()[0]
            c2.execute('SELECT Level FROM SunnyData_pokemon WHERE Zone=? AND Place=?',(zoneid,methode))
            zonelvl=c2.fetchone()[0]
            self.ui.outputgen.append(str(zone)+" est une zone de niveau "+str(zonelvl))
            c2.execute('SELECT Rarity FROM SunnyData_pokemon WHERE Zone=? AND Place=?',(zoneid,methode))
            listrarity=c2.fetchall()
            listrarity2=self.unique(listrarity)
            listrarity3=list()
            for x in listrarity2:
                listrarity3.append(x[0])
            advnames=list()
            advlvls=list()
            scienti=self.ui.scienti.currentText()
            if scienti=="Non":
                scientipop=False
            else:
                scientipop=True
            for adv in list(range(0,nb)):
                if scientipop==True and random.randint(1,15)==15:
                    scientipop=False
                    listrarityscienti=list()
                    listrarityscienti.append("Courant")
                    listrarityscienti.append("Peu fréquent")
                    listrarityscienti.append("Assez rare")
                    if scienti=="Scientifique Accompli" or scienti=="Scientifique Eminent":
                        listrarityscienti.append("Rare")
                    if scienti=="Scientifique Eminent":
                        listrarityscienti.append("Très rare")
                        listrarityscienti.append("Extrêmement rare")
                    selectrarity=""
                    while selectrarity not in listrarityscienti:
                        rarity=random.randint(1,100)
                        #Courant (100 - 43), peu fréquent (42 - 23), assez rare (22 - 13), rare (12 - 7), très rare (6 - 3), extemement rare (2-1)
                        if rarity<=2:
                            selectrarity="Extrêmement rare"
                        elif rarity<=6:
                            selectrarity="Très rare"
                        elif rarity<=12:
                            selectrarity="Rare"
                        elif rarity<=22:
                            selectrarity="Assez rare"
                        elif rarity<=42:
                            selectrarity="Peu fréquent"
                        else:
                            selectrarity="Courant"
                    if scienti=="Scientifique Débutant":
                        pokelist=""
                        while len(pokelist)==0:
                            c2.execute('SELECT Zone_id FROM SunnyData_zones WHERE Continent=? AND Pokemon=? ORDER BY random() LIMIT 1',(continent,'Oui'))
                            randomzone=c2.fetchone()[0]
                            c2.execute('SELECT * FROM SunnyData_pokemon WHERE Zone=? AND Rarity=?',(randomzone,selectrarity))
                            pokelist=c2.fetchall()
                        pknb=random.randint(0,len(pokelist)-1)
                        advnames.append(pokelist[pknb][1])
                        advlvls.append(lvl)
                        self.ui.outputgen.append(str(advnames[adv])+" (Scientifique Débutant)")
                    else:
                        if scienti=="Scientifique Eminent" and random.randint(1,5)==5 :
                            advnames.append("Pokémon unique")
                            advlvls.append(lvl)
                        else:
                            pokelist=""
                            while len(pokelist)==0:
                                c2.execute('SELECT * FROM SunnyData_pokemon WHERE Rarity=?',(selectrarity,))
                                pokelist=c2.fetchall()
                            pknb=random.randint(0,len(pokelist)-1)
                            advnames.append(pokelist[pknb][1])
                            advlvls.append(lvl)
                        self.ui.outputgen.append(str(advnames[adv])+" ("+str(scienti)+")")
                else:
                    selectrarity=""
                    while selectrarity not in listrarity3:
                        rarity=random.randint(1,100)
                        #Courant (100 - 43), peu fréquent (42 - 23), assez rare (22 - 13), rare (12 - 7), très rare (6 - 3), extemement rare (2-1)
                        if rarity<=2:
                            selectrarity="Extrêmement rare"
                        elif rarity<=6:
                            selectrarity="Très rare"
                        elif rarity<=12:
                            selectrarity="Rare"
                        elif rarity<=22:
                            selectrarity="Assez rare"
                        elif rarity<=42:
                            selectrarity="Peu fréquent"
                        else:
                            selectrarity="Courant" 
                    c2.execute('SELECT * FROM SunnyData_pokemon WHERE Zone=? AND Place=? AND Rarity=?',(zoneid,methode,selectrarity))
                    pokelist=c2.fetchall()
                    pknb=random.randint(0,len(pokelist)-1)
                    minlvl=int(pokelist[pknb][4].split("-")[0])
                    maxlvl=int(pokelist[pknb][4].split("-")[1])

                    advnames.append(pokelist[pknb][1])

                    if lvl==0:
                        advlvls.append(random.randint(minlvl,maxlvl))
                    elif lvl < minlvl:
                        advlvls.append(minlvl)
                    elif lvl > maxlvl:
                        advlvls.append(maxlvl)
                    else:
                        advlvls.append(random.randint(lvl,lvl+2))
                        if advlvls[adv]<minlvl:
                            advlvls[adv]=minlvl
                        if advlvls[adv]>maxlvl:
                            advlvls[adv]=maxlvl

                    self.ui.outputgen.append(str(advnames[adv])+" niveau "+str(advlvls[adv]))
        else:
             msgBox1 = QMessageBox()
             msgBox1.setText('Informations manquantes')
             msgBox1.exec_()

    def unique(self,seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def checkregion(self):
        self.ui.region.clear()
        c2.execute('SELECT Region FROM SunnyData_zones WHERE Continent=? ORDER BY Region',(self.ui.continent.currentText(),))
        reg = c2.fetchall()
        reg2=self.unique(reg)
        for r in reg2:
            self.ui.region.addItem(r[0])

    def checkzone(self):
        self.ui.zone.clear()
        if self.ui.region.currentText()!="":
            c2.execute('SELECT Zone FROM SunnyData_zones WHERE Region=? AND Pokemon="Oui"',(self.ui.region.currentText(),))
            zone = c2.fetchall()
            zone2=self.unique(zone)
            for z in zone2:
                self.ui.zone.addItem(z[0])

    def checkmethode(self):
        self.ui.methode.clear()
        if self.ui.zone.currentText()!="":
            c2.execute('SELECT Zone_id FROM SunnyData_zones WHERE Continent=? AND Region=? AND Zone=?',(self.ui.continent.currentText(),self.ui.region.currentText(),self.ui.zone.currentText()))
            zoneid=c2.fetchone()[0]
            c2.execute('SELECT Place FROM SunnyData_pokemon WHERE Zone=?',(zoneid,))
            meth = c2.fetchall()
            meth2=self.unique(meth)
            for m in meth2:
                self.ui.methode.addItem(m[0])

    def pokecatch(self):
        # Modified catch rate a = (((3*hpmax - 2*hpcurrent) * rate * ball)/(3*hpmax)) * statut
        # Shake probability b = 65536 / (255/a)^0.1875
        # To perform a shake check, a random number between 0 and 65535 (inclusive) is generated and compared to b. If the number is greater than or equal to b, the check "fails". 
        # Four shake checks are performed. The Pokémon is caught if all four shake checks succeed. Otherwise, the Poké Ball will shake as many times as there were successful shake checks before the Pokémon breaks free.
        # If a is 255 or greater, the capture will always succeed and no shake checks will be performed. 
        if self.ui.pvcapture.toPlainText()!="" or self.ui.pvmaxcapture.toPlainText()!="":
            self.ui.outputcapture.clear()
            c.execute('SELECT * FROM pokemons WHERE nom=?',(self.ui.pokecapture.currentText(),))
            pokedata=c.fetchall()[0]
            pokeid=int(pokedata[0])
            pokename=pokedata[1]
            taux_capture=int(pokedata[10])
            pv=int(self.ui.pvcapture.toPlainText())
            pvmax=int(self.ui.pvmaxcapture.toPlainText())
            lvl=int(self.ui.lvlcapture.toPlainText())
            ball=self.ui.ballcapture.currentText()

            if self.ui.capturestatut1.isChecked():
                st1bonus=1.5
            else:
                st1bonus=1
            if self.ui.capturestatut2.isChecked():
                st2bonus=2.5
            else:
                st2bonus=1
            if ball=="Poké Ball":
                ballbonus=1
            elif ball=="Super Ball":
                ballbonus=1.5
            elif ball=="Hyper Ball":
                ballbonus=2

            a=((((3*pvmax) - (2*pv)) * taux_capture * ballbonus)/(3*pvmax)) * (st1bonus*st2bonus)
            b = 65536 / ((255/a)**0.1875)
            self.ui.outputcapture.append("[center][img]https://sunrise-db.yo.fr/Sunrise_Champions/Secretchamp.png[/img]\n[spoiler=??? utilise une "+ball+" !]")
            j=0
            for i in [0,1,2,3]:
                j=j+1
                checkvalue = random.randint(0,65536)
                if checkvalue < b:
                    if j==1:
                        self.ui.outputcapture.append("[spoiler=...]")
                    elif j==2:
                        self.ui.outputcapture.append("[spoiler=... ...]")
                    elif j==3:
                        self.ui.outputcapture.append("[spoiler=... ... ...]")
                    else:
                        self.ui.outputcapture.append("[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nFélicitations ! "+pokename+" est capturé !\nIl est [u]niveau "+str(lvl)+"[/u] et prêt à se battre ![/spoiler][/spoiler][/spoiler][/spoiler][/center]")
                else:
                    if j==1:
                        self.ui.outputcapture.append("[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nOh, non ! "+pokename+" s'est libéré ![/spoiler][/center]")
                    if j==2:
                        self.ui.outputcapture.append("[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nRaaah ! Ça y était presque ![/spoiler][/spoiler][/center]")
                    if j==3:
                        self.ui.outputcapture.append("[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nAaaaah ! Presque ![/spoiler][/spoiler][/spoiler][/center]")
                    if j==4:
                        self.ui.outputcapture.append("[img]https://sunrise-db.yo.fr/Sprites/"+str(pokeid)+".png[/img]\nMince ! Ça y était presque ![/spoiler][/spoiler][/spoiler][/spoiler][/center]")
                    break
                
        else:
             msgBox1 = QMessageBox()
             msgBox1.setText('Informations manquantes')
             msgBox1.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# pv = int(self.ui.pv.toPlainText())
# lvl = (self.ui.spinlvl.value())
# total_price = pv + lvl
# total_price_string = "The total is " + str(total_price)
# self.ui.outputrp.setText(total_price_string)
