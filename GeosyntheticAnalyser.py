
from cgitb import text
from dataclasses import dataclass
from abc import ABC, abstractmethod
from itertools import product
import itertools
from multiprocessing.sharedctypes import Value
from pickle import FALSE, TRUE
import string
from math import log
from subprocess import STARTUPINFO
from tracemalloc import start
from urllib.robotparser import RobotFileParser
from xmlrpc.client import boolean
import pylightxl as xl

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.base import runTouchApp
from kivy.uix.slider import Slider


@dataclass
class Geosynthetic(ABC):
    brand: string
    name: string
    strength: float

    Tdes : float
   
    Tchar: float    #Characteristic short-term strength
    RFcr: float     #Reduction Factor for long-term creep
    RFid: float     #Reduction factor for installation damage
    RFw: float      #Reduction Factor for Weathering
    RFch: float     #Reduction Factor for Chemical and Enviromental effects
    fn: float       #Partial factor for ramification of failure
    fs: float       #Factor of safety for extrapolation of data
    strain: int

    printFlag: bool = TRUE

    def __str__(self):
        return f"{self.brand} {self.name}"
    def getStrength(self):
        # if self.Tdes is float:
        #     return self.Tdes
        # else:
        #     return 0
        try:
            return float(self.Tdes)
        except ValueError:
            return float('inf')
    @abstractmethod 
    def calc_Tchar(self):
        pass
    @abstractmethod
    def calc_RFcr(self):
        pass
    @abstractmethod
    def calc_RFid(self):
        pass
    @abstractmethod
    def calcRFw(self):
        pass
    @abstractmethod
    def calc_RFch(self):
        pass
    @abstractmethod
    def calc_fn(self):
        pass
    @abstractmethod
    def calc_fs(self):
        pass
    @abstractmethod
    def calc_Tdes(self):
        pass

class Stabilenka(Geosynthetic):
    def __init__(self,name, maxstrength):
        self.brand="Stabilenka"
        self.name=name
        self.strength = maxstrength
        self.Tchar=self.calc_Tchar(ui_strain)
        self.RFcr=self.calc_RFcr(ui_soilTemp,ui_designLife)
        self.RFid=self.calc_RFid(ui_soilType)
        self.RFw=self.calcRFw(ui_weathering)
        self.RFch=self.calc_RFch(ui_soilTemp, ui_designLife, ui_soilpH)
        self.fn=self.calc_fn(ui_structureCat)
        self.fs=self.calc_fs(ui_soilTemp,ui_designLife)
        self.Tdes=self.calc_Tdes()
    def calc_Tchar(self, strain):
        if strain in range(1,11):
            match strain:
                case 1:
                    value=self.strength*.13
                    self.strain=1              
                case 2:
                    value=self.strength*.22
                    self.strain=2
                case 3:
                    self.strain=3
                    value=self.strength*.31
                case 4:
                    self.strain=4
                    value=self.strength*.40
                case 5:
                    self.strain=5
                    value=self.strength*.51
                case 6:
                    self.strain=6
                    value=self.strength*.65
                case 7:
                    self.strain=7
                    value=self.strength*.80        
                case 8:
                    self.strain=8
                    value=self.strength*.89
                case 9:
                    value=self.strength*.96
                    self.strain=9
                case 10:
                    value=self.strength*1   
                    self.strain=10
        else:
            value=self.strength
            self.strain=10
        return value
    def calc_RFcr(self, soilTemp, designLife):
        match soilTemp:
            case 15: value=0.0281*log(designLife)+1.3552
            case 20: value=0.0281*log(designLife)+1.3852
            case 25: value=0.0281*log(designLife)+1.4152
            case 30: value=0.0325*log(designLife)+1.4257
            case 35: value=0.0325*log(designLife)+1.4557
        return value
    def calc_RFid(self,soilType):
        value=0
        match soilType:
            case 1: #sand
                if self.name in ["150/45", "120/120" , "150/150" , "200/200"]:
                    value=1.2
                elif self.name in ["200/45" , "300/45"]:
                    value=1.15
                else:
                    value=1.1
            case 2: #mixed (sandy gravel)
                if self.name in ["150/45" , "120/120" , "150/150"]:
                    value=1.3
                elif self.name in ["200/45" , "300/45" , "200/200"]:
                    value=1.2
                elif self.name in ["400/50"]:
                    value=1.14
                else:
                    value=1.1
            case 3: #coarse 
                if self.name in ["150/45" , "120/120" , "150/150"]:
                    value="Measurment Required"
                elif self.name in ["200/45" , "300/45" , "200/200"]:
                    value=1.6
                elif self.name in ["400/50"]:
                    value=1.54
                elif self.name in ["600/50" , "800/100"]:
                    value=1.3
                else:
                    value=1.1
        return value
    def calcRFw(self, weathering):
        if weathering == 2: #Covered within 1 day
            value=1.00
        else: #covered within two weeks and remains protected from sunlight
            value=1.25
        return value 
    def calc_RFch(self, soilTemp, designLife, soilpH):
        if soilpH < 4:
            value="Soil pH too low"
        elif soilpH>9:
            value="Soil pH too high"
        else:
            chList= [[1.00,1.00,1.01,1.01,1.02],
                    [1.01,1.01,1.03,1.07,1.16],
                    [1.01,1.03,1.07,1.16,1.38]]
            match soilTemp:
                case 15: n=0
                case 20: n=1
                case 25: n=2
                case 30: n=3
                case 35: n=4
            if designLife <= 10:
                value = chList[0][n]
            elif 10<designLife<=60:
                value = chList[1][n]
            elif 60<designLife<=120:
                value = chList[2][n]
        return value  
    def calc_fn(self,structureCat):
        if structureCat == 3:
            value=1.1
        else: #i.e category 1 or 2
            value=1.0
        return value  
    def calc_fs(self, soilTemp, designLife):
        chList= [[1.00,1.00,1.00,1.00,1.01],
                [1.00,1.01,1.02,1.03,1.07],
                [1.01,1.02,1.03,1.07,1.17]]
        match soilTemp:
            case 15: n=0
            case 20: n=1
            case 25: n=2
            case 30: n=3
            case 35: n=4
        if designLife <= 10:
            value = chList[0][n]
        elif 10<designLife<=60:
            value = chList[1][n]
        elif 60<designLife<=120:
            value = chList[2][n]
        else:
            raise ValueError("Design Life must be under 120 years.")
        return value
    def calc_Tdes(self):
        try:
            value=self.Tchar/(self.RFcr*self.fn*self.RFid*self.RFw*self.RFch*self.fs)
        except:
            value="Can't compute"
        return value


class Secugrid(Geosynthetic):
    def __init__(self,name, maxstrength):
        self.brand="Secugrid"
        self.name=name
        self.strength = maxstrength
        self.Tchar=self.calc_Tchar(ui_strain)
        self.RFcr=self.calc_RFcr(ui_soilTemp,ui_designLife)
        self.RFid=self.calc_RFid(ui_soilType)
        self.RFw=self.calcRFw(ui_weathering)
        self.RFch=self.calc_RFch(ui_soilTemp, ui_designLife, ui_soilpH)
        self.fn=self.calc_fn(ui_structureCat)
        self.fs=self.calc_fs(ui_soilTemp,ui_designLife)
        self.Tdes=self.calc_Tdes()
    def calc_Tchar(self, strain):
        value=self.strength
        self.strain=strain
        list=["30/30 Q6","40/40 Q6","60/60 Q6","80/80 Q6"]
        if self.name in list:
            if strain < 6:
                value="Strain too low (6% min)"
            else:
                self.strain=6
        else:
            if strain < 6.5:
                value="Strain too low (6.5% min)"
            else:
                self.strain=6.5
        return value
    def calc_RFcr(self, soilTemp, designLife):
        if soilTemp>20:
            value="Soil temperature too high"
        elif soilTemp<20:
            value="Soil temperature too low"
        else:
            value=0.0225*log(designLife)+1.295
        return value
    def calc_RFid(self,soilType):
        list1=["30/30 Q6","40/40 Q6","40/20 R6"]
        list2=["60/60 Q6", "60/20 R6"]
        list3=["80/80 Q6","80/20 R6"]
        match soilType:
            case 1: #sand
                if self.name in list1:
                    value=1.09
                elif self.name in list2:
                    value=1.08
                else:
                    value=1.05
            case 2: #mixed (sandy gravel)
                if self.name in list1:
                    value=1.08
                elif self.name in list2:
                    value=1.05
                elif self.name in list3:
                    value=1.03
                else:
                    value=1.02
            case 3: #coarse 
                if self.name in list1:
                    value=1.06
                elif self.name in list2:
                    value=1.02
                elif self.name in list3:
                    value=1.01
                else:
                    value=1.00
        return value
    def calcRFw(self, weathering):
        value=1 #protected from sunlight, exposure period up to a month 
        return value 
    def calc_RFch(self, soilTemp, designLife,soilpH):
        if soilTemp > 20:
            value="Soil temperature too high"
        elif soilTemp <20:
            value="Soil temperature too low"
        else:
            chList= [[1.07,1.00,1.01,1.03,1.11],
                    [1.10,1.01,1.02,1.06,1.21]]
            if 0<=soilpH<2:
                value="Soil pH too low"
            elif 2<=soilpH<=4:
                n=1
            elif 4<soilpH<=9:
                n=2
            elif 9<soilpH<=10:
                n=3
            elif 10<soilpH<=11:
                n=4
            elif 11<soilpH<=12.5:
                n=5
            else:
                value="soil pH too high"
            if designLife <= 60:
                value = chList[0][n]
            else:
                value = chList[1][n]
        return value  
    def calc_fn(self,structureCat):
        if structureCat == 3:
            value=1.1
        else: #i.e category 1 or 2
            value=1.0
        return value  
    def calc_fs(self, soilTemp, designLife):
        if designLife <= 60:
            value = 1.03
        else:
            value = 1.05
        return value
    def calc_Tdes(self):
        try:
            value=self.Tchar/(self.RFcr*self.fn*self.RFid*self.RFw*self.RFch*self.fs)
        except:
            value="Can't compute"
        return value

def writeExcel(*lists):
    dataList=itertools.chain(*lists)
    dataList=sorted(dataList,key=lambda x: x.getStrength())
    wb=xl.Database()
    wb.add_ws(ws="Geosynthethics")
    titleData=["Brand:","Name:","Max Strength:","Strain:","Characteristic strength (Tchar):",
    "Long-term creep reduction factor (RFcr):","Installation damage reduction factor (RFid):","Weathering reduction factor (RFw):",
    "Chemical & Enviromental reduction factor (RFch):","Ramification of failure safety factor (fn):",
    "Data extrapolation safety factor (fs):","DESIGN STRENGTH:"]
    for row_id, data in enumerate(titleData,start=1):
        wb.ws(ws="Geosynthethics").update_index(row=row_id, col=1, val=data)
    for col_id, i in enumerate(dataList,start=2):
        x=1
        for attName, attValue in vars(i).items():
            wb.ws(ws="Geosynthethics").update_index(row=x, col=col_id, val=attValue)
            # wb.ws(ws="Geosynthethics").update_index(row=x, col=1, val=attName)
            x=x+1
    xl.writexl(db=wb,fn="geosynthethicOutputs.xlsx")

def main(): #Create list of geosynthetics to be analysed
    stabilenkaMono=[]
    stabilenkaMono.append(Stabilenka("150/45",100))
    stabilenkaMono.append(Stabilenka("300/45",300))
    stabilenkaMono.append(Stabilenka("400/50",400))
    stabilenkaMono.append(Stabilenka("600/50",600))
    stabilenkaMono.append(Stabilenka("800/100",800))
    stabilenkaMono.append(Stabilenka("1000/100",1000))
    stabilenkaMono.append(Stabilenka("1200/100",1200))
    stabilenkaMono.append(Stabilenka("1400/100",1400))
    stabilenkaMono.append(Stabilenka("1500/100",1500))
    stabilenkaDual=[]
    stabilenkaDual.append(Stabilenka("120/120",120))
    stabilenkaDual.append(Stabilenka("150/150",150))
    stabilenkaDual.append(Stabilenka("200/200",200))
    secugridQ=[]
    secugridQ.append(Secugrid("30/30 Q6",30))
    secugridQ.append(Secugrid("40/40 Q6",40))
    secugridQ.append(Secugrid("60/60 Q6",60))
    secugridQ.append(Secugrid("80/80 Q6",80))
    secugridR=[]
    secugridR.append(Secugrid("40/20 R6",40))
    secugridR.append(Secugrid("60/20 R6",60))
    secugridR.append(Secugrid("80/20 R6",80))
    secugridR.append(Secugrid("120/40 R6",120))
    secugridR.append(Secugrid("150/40 R6",150))
    secugridR.append(Secugrid("200/40 R6",200))
    secugridR.append(Secugrid("400/40 R6",400))
    
    
    writeExcel(stabilenkaMono,stabilenkaDual,secugridQ,secugridR)

class appLayout(GridLayout):
    def __init__(self,**kwargs):
        #Setting up space and writing title and greeting message
        super(appLayout,self).__init__(**kwargs)
        self.cols=1
        self.add_widget(Label(text="Geosynthetic Analyser",font_size=35,size_hint_y=None,height=70))
        self.greeting=Label(text="Insert parameters and press on 'Calculate' to output an excel file.",size_hint_y=None,height=70,halign='center')
        self.add_widget(self.greeting)
      
        #Creating more columns for user inputs
        self.inputGrid = GridLayout()
        self.inputGrid.cols=2
        self.inputGrid.cols_minimum={0:400,1:100}
        # self.inputGrid.size_hint = None, None
        self.add_widget(self.inputGrid)

        #Strain Slifer
        self.inputGrid.add_widget(Label(text="Strain Value:"))
        self.strainGrid=GridLayout()
        self.strainGrid.cols=2
        self.inputGrid.add_widget(self.strainGrid)
        self.inStrain = Slider(min=1, max=10, value=10, step=1)
        self.strainGrid.add_widget(self.inStrain)
        self.inStrain.bind(value=self.on_value_change)
        self.strainLabel=Label(text='10%')
        self.strainGrid.add_widget(self.strainLabel) 

        #Design life input and dropdown
        self.inputGrid.add_widget(Label(text="Design Life Value:"))
        self.designLifeGrid=GridLayout()
        self.designLifeGrid.cols=2
        self.inputGrid.add_widget(self.designLifeGrid)
        self.inDesignLife = TextInput(multiline=False)
        self.designLifeGrid.add_widget(self.inDesignLife)
        self.designLifeTable = DropDown()
        yearBtn = Button(text='Years',size_hint_y=None, height=44)
        yearBtn.bind(on_release=lambda yearBtn: self.designLifeTable.select(yearBtn.text))
        self.designLifeTable.add_widget(yearBtn)
        monthBtn=Button(text='Months',size_hint_y=None, height=44)
        monthBtn.bind(on_release=lambda monthBtn: self.designLifeTable.select(monthBtn.text))
        self.designLifeTable.add_widget(monthBtn)
        self.mainbutton=Button(text="Years")
        self.mainbutton.bind(on_release=self.designLifeTable.open)
        self.designLifeTable.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.designLifeGrid.add_widget(self.mainbutton)
    
        #Soil Temperature dropdown
        self.inputGrid.add_widget(Label(text="Soil Temperature (°):"))
        self.soilTempTable=DropDown()
        for index in range(15,36,5):
            btn = Button(text='%d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.soilTempTable.select(btn.text))
            self.soilTempTable.add_widget(btn)
        self.soilTempBtn=Button(text="20")
        self.soilTempBtn.bind(on_release=self.soilTempTable.open)
        self.soilTempTable.bind(on_select=lambda instance, x: setattr(self.soilTempBtn, 'text', x))
        self.inputGrid.add_widget(self.soilTempBtn)

        #Soil Type dropdown
        self.inputGrid.add_widget(Label(text="Soil type, where:\n[1]-Sand  [2]-Mixed (Sands & Gravels)  [3]-Coarse",halign='center'))
        self.soilTypeTable=DropDown()
        for index in range(1,4):
            btn = Button(text='%d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.soilTypeTable.select(btn.text))
            self.soilTypeTable.add_widget(btn)
        self.soilTypeBtn=Button(text="1")
        self.soilTypeBtn.bind(on_release=self.soilTypeTable.open)
        self.soilTypeTable.bind(on_select=lambda instance, x: setattr(self.soilTypeBtn, 'text', x))
        self.inputGrid.add_widget(self.soilTypeBtn)
        
        #Struture Category dropdown
        self.inputGrid.add_widget(Label(text="Structure category from BS 8006-1:2010:\n1: Low impact 3: High impact:\n(Used to calculate ramification of failure safety factor)",halign='center'))
        self.structureCatTable=DropDown()
        for index in range(1,4):
            btn = Button(text='%d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.structureCatTable.select(btn.text))
            self.structureCatTable.add_widget(btn)
        self.structureCatBtn=Button(text="1")
        self.structureCatBtn.bind(on_release=self.structureCatTable.open)
        self.structureCatTable.bind(on_select=lambda instance, x: setattr(self.structureCatBtn, 'text', x))
        self.inputGrid.add_widget(self.structureCatBtn)
        
        #Weathering dropdown
        self.inputGrid.add_widget(Label(text="Weathering where:\n[1]-Covered withing 2 weeks and protected from sunlight\n[2]-Covered within one day",halign='center'))
        self.weatheringTable=DropDown()
        for index in range(1,3):
            btn = Button(text='%d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.weatheringTable.select(btn.text))
            self.weatheringTable.add_widget(btn)
        self.weatheringBtn=Button(text="1")
        self.weatheringBtn.bind(on_release=self.weatheringTable.open)
        self.weatheringTable.bind(on_select=lambda instance, x: setattr(self.weatheringBtn, 'text', x))
        self.inputGrid.add_widget(self.weatheringBtn)

        self.inputGrid.add_widget(Label(text="Soil pH Value:"))
        self.pHGrid=GridLayout()
        self.pHGrid.cols=2
        self.inputGrid.add_widget(self.pHGrid)
        self.inSoilpH = Slider(min=0, max=14, value=7, step=.5)
        self.pHGrid.add_widget(self.inSoilpH)
        self.inSoilpH.bind(value=self.on_value_change2)
        self.pHLabel=Label(text='7')
        self.pHGrid.add_widget(self.pHLabel) 

        self.calculate = Button(text="CALCULATE",size_hint_y=None,height=55)
        self.calculate.bind(on_press=self.press)
        self.add_widget(self.calculate)

        self.add_widget(Label(text=f"Following procedure of BS8006. Geosynthetic data collected from the British Board of Agrément. Program version v{programVersion}",font_size=12,size_hint_y=None,height=12))
    
    def on_value_change(self,instance,val):
        self.strainLabel.text = (f"{val}%")
    def on_value_change2(self,instance,val):
        self.pHLabel.text = (f"{val}")

    def press(self,instance):
        global ui_strain, ui_designLife, ui_soilTemp, ui_structureCat,ui_soilType, ui_weathering, ui_soilpH
        ui_strain, ui_designLife, ui_soilTemp, ui_structureCat,ui_soilType, ui_weathering,ui_soilpH = 1,1,1,1,1,1,1
        try:
            ui_strain=float(self.inStrain.value)
            ui_soilTemp=float(self.soilTempBtn.text)
            ui_soilType=float(self.soilTypeBtn.text)
            ui_structureCat=float(self.structureCatBtn.text)
            ui_weathering=float(self.weatheringBtn.text)
            ui_soilpH=float(self.inSoilpH.value)
            if self.mainbutton.text=="Years":
                ui_designLife=float(self.inDesignLife.text)
            else:
                ui_designLife=float(self.inDesignLife.text)*(1/12)
            if 120<ui_designLife <= 0:
                raise ValueError("Design life has to be within the range (0,120]")  
            self.greeting.text = (f'Excel created.\nStrain: {ui_strain}% | Design Life: {ui_designLife} Years | ' +
                                f'Soil Temperature: {ui_soilTemp}° | Soil Type: {ui_soilType}\nStructure Category: {ui_structureCat} | Weathering: {ui_weathering} '+
                                f'| Soil pH: {ui_soilpH}')
            main()
        except ValueError:
            self.greeting.text = "Problem calculating. Please check data (such as Design Life) have been properly inputted and try again."
        
class GeosyntheticAnalyserApp(App):
    def build(self):
        return appLayout()

def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}


if __name__=="__main__":
    global programVersion
    programVersion=1.1
    reset()
    GeosyntheticAnalyserApp().run()


"""
CHANGES NOTES: (To keep track of database)
v1.0
2022.05.26 - Added Stabilenka Geotextiles (Agrément Certificate 13/4979 sheet 1)
v1.1
2022.05.28 - Added Secugrid PET geogrids (HAPAS Certificate 14/H218 sheet 1)


"""
