import math

class Cevirici:
    def __init__(self, sayi):
        self.sayi = sayi
        self.yaziyaCevir()

    def yaziyaCevir(self):
        basaSifirEkle = len(self.sayi)%3
        if basaSifirEkle == 1:
            sayi = "00"+self.sayi
        elif basaSifirEkle == 2:
            sayi = "0"+self.sayi
        else:
            sayi = self.sayi

        kacYuzlerVar =  math.ceil(int(len(sayi))/3.0)
        ucluGrub = {"0":"", "1":"Bin", "2":"Milyon", "3":"Milyar", "4":"Trilyon", "5":"Katrilyon", "6":"Kentilyon", "7":"Seksilyon", "8":"Septilyon", "9":"Oktilyon", "10":"Nobilyon", "11":"Desilyon"}
        oku = ""

        for i in range(int(kacYuzlerVar)):
            if sayi[-1*((i*3)+3)]+sayi[-1*((i*3)+2)]+sayi[-1*((i*3)+1)] == "000":
                oku = oku
            elif sayi[-1*((i*3)+3)]+sayi[-1*((i*3)+2)]+sayi[-1*((i*3)+1)] == "001" and len(sayi) == 6:
                oku = ucluGrub[str(i)] + oku
            else:
                oku = self.ucHaneOku(sayi[-1*((i*3)+3)]+sayi[-1*((i*3)+2)]+sayi[-1*((i*3)+1)]) + ucluGrub[str(i)] + oku

        if oku == "":
            oku = "Sıfır"
        self.yaz = oku
        print(oku)

    def ucHaneOku(self, sayi):
        birler = {"0":"", "1":"Bir", "2":"İki", "3":"Üç", "4":"Dört", "5":"Beş", "6":"Altı", "7":"Yedi", "8":"Sekiz", "9":"Dokuz"}
        onlar = {"0":"", "1":"On", "2":"Yirmi", "3":"Otuz", "4":"Kırk", "5":"Elli", "6":"Altmış", "7":"Yetmiş", "8":"Seksen", "9":"Doksan"}
        yuz = ["Yüz"]
        if len(sayi) == 3:
            if sayi[0] == "1":
                oku = yuz[0]+onlar[sayi[1]]+birler[sayi[2]]
                return oku
            if sayi[0] == "0":
                oku = onlar[sayi[1]]+birler[sayi[2]]
                return oku
            else:
                oku = birler[sayi[0]]+yuz[0]+onlar[sayi[1]]+birler[sayi[2]]
                return oku
