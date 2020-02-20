import npyscreen
import random, time, _thread
from datetime import datetime

from GeneticAlgorithms import MotherNature, Evolution

from customBox import MultiLineBox, ProgressBarBox
from IO import *

content = None
avaliation = None
motherNature = None
path = ''
maxScore = 0

def SaveGeneration ():
    import os
    global motherNature
    global path
    global maxScore

    #os.mkdir(f"{path}/{motherNature.generationCont}")
    for index, pop in enumerate(motherNature.population):
        #Serialize(pop, f"{path}/{motherNature.generationCont}", f"{index} - {motherNature.rating[index]}", False)
        if motherNature.rating[index] >= maxScore:

            now = datetime.now()
            maxScore = motherNature.rating[index]
            name = now.strftime("%d-%m-%Y %H:%M:%S")
            Serialize(pop, f"{path}/{maxScore}", f"{name}", False)

class Content:
    def __init__(self, name, inputs, arch:str, outputs, lenPop, avaliationPath, useDataSet, dataSetPath=None):
        self.name = str(name)
        self.inputs = int(inputs)

        arch = arch.replace("[", "").replace("]", "").split(",")
        arch = map(lambda x: int(x), arch)

        self.arch = list(arch)
        self.outputs = int(outputs)
        self.lenPop = int(lenPop)

        self.avaliationPath = str(avaliationPath)
        self.useDataSet = useDataSet
        self.dataSetPath = dataSetPath

class TraingForm (npyscreen.ActionFormMinimal):
    def create(self):
        global content
        global avaliation
        global motherNature

        motherNature = MotherNature(avaliation.Avaliation, 12, content.lenPop, content.inputs, content.arch, content.outputs)

        _thread.start_new_thread(Evolution, (motherNature, content.lenPop//2 + 1, content.inputs, content.arch, content.outputs, SaveGeneration))

        self.keypress_timeout = 1
        y, x = self.useable_space()
        annMsg = f"Inputs:  {content.inputs}\nHidden:  {content.arch}\nOutputs: {content.outputs}"
        self.annBox = self.add(MultiLineBox, name="ANN Configuration", value = annMsg, height = 5, width = x // 2 - 2, editable = False)

        avaliationName = content.avaliationPath.split("/")[-1]
        gaMsg = f"Population: {content.lenPop}\nAvaliation: {avaliationName}"
        self.gaBox = self.add(MultiLineBox, name="GA Configuration", value = gaMsg, relx=x//2 + 1, rely = 2, height = 5, editable = False)

        
        self.evolvBox = self.add(MultiLineBox, name="Evolution Statistics", value = "", relx=x//2 + 1, rely = 7, height = y - 14, editable = False)

        self.add(npyscreen.TitleFixedText, name = "Avaliation Progress:", rely = -7,editable = False)
        self.attProgress = self.add(npyscreen.SliderPercent, rely = -6, editable = False)
        self.add(npyscreen.TitleFixedText, name = "Evolution Progress:", rely = -4,editable = False)
        self.evolProgress = self.add(npyscreen.SliderPercent, rely = -3, editable = False)
    
    def resize (self):
        y, x = self.useable_space()
        self.annBox.width = x // 2 - 2
        self.gaBox.relx=x//2 + 1
        self.gaBox.entry_widget.relx=x//2 + 3

        self.evolvBox.relx=x//2 + 1
        self.evolvBox.entry_widget.relx=x//2 + 3
        self.evolvBox.height = y - 14

    def while_waiting (self):
        global motherNature
        global maxScore
        self.attProgress.set_value(100 * motherNature.avaliator.attTest / motherNature.avaliatorIterations)
        score = ""
        for i in range(13):
            m = f"{i} = {motherNature.rating.count(i)}\n"
            score += m

        evolvMsg = f"G{motherNature.generationCont} -> Rating ({len(motherNature.avaliator.points)}): {motherNature.avaliator.points}\nMax Score: {maxScore}\nScore:\n{score}"
        self.evolvBox.set_value(evolvMsg)

        self.display()

        #if motherNature.generationCont > 10:
        #    motherNature.evolving = False

class NewForm(npyscreen.ActionForm):
    def create(self):
        self.keypress_timeout = 1

        self.name    = self.add(npyscreen.TitleText, name = f"Name:")
        self.path    = self.add(npyscreen.TitleFilenameCombo, name = "Path:", value = os.getcwd())
        self.avaliation = self.add(npyscreen.TitleFilenameCombo, name = "Avaliation:", value_changed_callback = self.on_avaliation_change)
        self.useDataSet = self.add(npyscreen.CheckBox, name="Use DataSet", value=False, relx=18)
        self.dataPath = self.add(npyscreen.TitleFilenameCombo, name = "DataPath:")

        self.add(npyscreen.TitleFixedText, name = " ", editable = False)
        self.add(npyscreen.TitleFixedText, name = "ANN Config:", relx=18, editable = False)
        self.inputs  = self.add(npyscreen.TitleText, name = "Inputs:")
        self.bnt     = self.add(npyscreen.ButtonPress, name = "Random Hidden", relx=16, when_pressed_function = self.on_random_arch)

        self.hidden  = self.add(npyscreen.TitleText, name = "Hidden:")
        self.outputs = self.add(npyscreen.TitleText, name = "Outputs:")

        self.add(npyscreen.TitleFixedText, name = " ", editable = False)
        self.add(npyscreen.TitleFixedText, name = "GA Config:", relx=18, editable = False)
        self.add(npyscreen.TitleFixedText, name = "Population:", relx=18, editable = False)
        self.lenPop  = self.add(npyscreen.TitleText, name = "Size:", value = str(random.randint(10, 100)))

        self.on_random_arch()

    def while_waiting(self):
        global avaliation
        
        if avaliation != None:
            self.inputs.set_value(str(avaliation.inputs))
            self.outputs.set_value(str(avaliation.outputs))
        else:
            self.inputs.set_value(None)
            self.outputs.set_value(None)

        self.refresh()

    def on_avaliation_change (self, widget):
        global avaliation
        if (self.avaliation.value != None):
            try:
                avaliation = loadLibrary(self.avaliation.value)
                self.DISPLAY()
            except Exception as e:
                npyscreen.notify_confirm(str(e), "Entry Error")

    
    def on_random_arch(self):
        h = [random.randint(2, 50)] * random.randint(1, 10)
        self.hidden.value = str(h)
        self.display()
    
    def on_ok (self):
        global content
        global path
        try:
            content = Content (self.name.value, self.inputs.value, self.hidden.value, self.outputs.value, self.lenPop.value, self.avaliation.value, self.useDataSet.value, self.dataPath.value)
            if not str(self.name.value).isspace or str(self.name.value) != "":
                Serialize(content, self.path.value, self.name.value)
            else:
                raise Exception("Name is empyth")

            if self.avaliation.value == None:
                raise Exception("Import .py file on Avaliation")

            self.parentApp.addForm("TRAING", TraingForm, name=f"{content.name} Traing")
            self.parentApp.switchForm("TRAING")

            path = f"{self.path.value}/{self.name.value}"
        except Exception as e:
            npyscreen.notify_confirm(str(e), "Entry Error")
    
    def on_cancel (self):
        self.parentApp.switchFormPrevious()

class MainForm (npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, name = "Open Existing Content", relx=18, editable = False)
        self.contentBin = self.add(npyscreen.TitleFilenameCombo, name = "Content Bin:")

        self.open       = self.add(npyscreen.ButtonPress, name = "Open", relx=16, when_pressed_function = self.on_open_content)
        self.new        = self.add(npyscreen.ButtonPress, name = "Create New", relx=26, rely=5, when_pressed_function = self.on_create_new)

        self.close      = self.add(npyscreen.ButtonPress, name = "Close",relx = -12, rely=-3, when_pressed_function = self.on_close)
    
    def on_open_content(self):
        global content
        global avaliation
        global path
        try:
            content = Deserialize(str(self.contentBin.value))
            avaliation = loadLibrary(content.avaliationPath)

            path = '/'.join(self.contentBin.value.split("/")[:-1])

            self.parentApp.addForm("TRAING", TraingForm, name=f"{content.name} Traing")
            self.parentApp.switchForm("TRAING")
        except Exception as e:
            npyscreen.notify_confirm(str(e), "Entry Error")
    
    def on_create_new (self):
        self.parentApp.switchForm("CREATE")
    
    def on_close (self):
        self.parentApp.switchForm(None)

class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="GA and ANN TUI!")
        self.addForm("CREATE", NewForm, name="Create New Content!")

MyApp = App()
MyApp.run()