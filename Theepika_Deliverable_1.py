from tkinter import * #imports all tkinter classes
import tkinter as tk
from tkinter import ttk #for combobox - drop-down menu

from time import strftime #gets system's time
from datetime import datetime #gets system's date


# programable paramters [1=lower limit, 2=nominal, 3=upper limit, 4=temporary paramater, 5=permanent parameter]
Lower_Rate_Limit = [30,60,175,60,60] #ppm
Upper_Rate_Limit = [50,120,175,120,120] #ppm
Atrial_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Atrial_Pules_Width = [0.05,0.4,1.9,0.4,0.4] #ms
Ventricular_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Ventricular_Pulse_Width = [0.05,0.4,1.9,0.4,0.4] #ms
VRP = [150,320,500,320,320] #ms
ARP = [150,250,500,250,250] #ms

Modes = ["Off", "AOO","VOO", "AAI", "VVI"] #modes

Programable_Paramters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pules Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"] #list of paramenters

#array to show which parameters apply to which mode
Mode_Parameters = [[False,False,False,False,False,False,False,False], #Off
                   [True,True,True,True,False,False,False,False], #AOO
                   [True,True,False,False,True,True,False,False], #VOO
                   [True,True,True,True,False,False,False,True], #AAI
                   [True,True,False,False,True,True,True,False]] #VVI


mode_parameters = {
    "Off": [" "],
    "AOO": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Atrial_Amplitude", "Atrial_Pules_Width"],
    "VOO": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Ventricular_Amplitude", "Ventricular_Pulse_Width"],
    "AAI": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Atrial_Amplitude", "Atrial_Pules_Width", "ARP"],
    "VVI": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Ventricular_Amplitude", "Ventricular_Pulse_Width", "VRP"]
    }


##Functions

def select_mode(event): #selects mode

    global selected_mode

    selected_mode = combo_box.get();
    label.config(text = "Selected Mode: " + selected_mode);
    parameters(selected_mode);



def update_temp_values(): #updates value
    Lower_Rate_Limit[3] = s_LowerRateLimit.get()
    Upper_Rate_Limit[3] = s_UpperRateLimit.get()
    Atrial_Amplitude[3] = s_AtrialAmplitude.get()
    Atrial_Pules_Width[3] = s_AtrialPulesWidth.get()
    Ventricular_Amplitude[3] = s_VentricularAmplitude.get()
    Ventricular_Pulse_Width[3] = s_VentricularPulseWidth.get()
    VRP[3] = s_VRP.get()
    ARP[3] = s_ARP.get()

    root.after(500, update_temp_values); #updates every 0.5s



def save_parameters(): #saves parameters
    Lower_Rate_Limit[4] = Lower_Rate_Limit[3]
    Upper_Rate_Limit[4] = Upper_Rate_Limit[3]
    Atrial_Amplitude[4] = Atrial_Amplitude[3]
    Atrial_Pules_Width[4] = Atrial_Pules_Width[3]
    
    Ventricular_Amplitude[4] = Ventricular_Amplitude[3]
    Ventricular_Pulse_Width[4] = Ventricular_Pulse_Width[3]
    VRP[4] = VRP[3]
    ARP[4] = ARP[3]


def print_parameters():

    parameters = {
        "Lower_Rate_Limit": Lower_Rate_Limit[4],
        "Upper_Rate_Limit": Upper_Rate_Limit[4],
        "Atrial_Amplitude": Atrial_Amplitude[4],
        "Atrial_Pules_Width": Atrial_Pules_Width[4],
        "Ventricular_Amplitude": Ventricular_Amplitude[4],
        "Ventricular_Pulse_Width": Ventricular_Pulse_Width[4],
        "VRP": VRP[4],
        "ARP": ARP[4]

    }

    print(f"\nParameters for mode {selected_mode}:")
    for param in mode_parameters[selected_mode]:
        print(f"{param}: {parameters[param]}")



def parameters(selected_mode):

    match selected_mode:

        case "Off":
            mode = 0
        case "AOO":
            mode = 1

        case "VOO":
            mode = 2
        case "AAI":
            mode = 3
        case "VVI":
            mode = 4

    for i in range(8):
        if Mode_Parameters[mode][i]:
            sList[i].place(x=100, y=70+i*70)
            lList[i].place(x=100, y= 50+i*70)

        else:
            sList[i].place_forget()
            lList[i].place_forget()







###############################MAIN_WINDOW#######################################################

root = tk.Tk(); #initializes main window
root.geometry("1080x1080"); #Sets size of the window
root.title("Home Screen");

###############################MENU##############################################################

mb = Menubutton(root, text = 'Main'); #creates button that shows dropdown menu
mb.grid();
mb.menu = Menu(mb, tearoff=0);
mb['menu'] = mb.menu;
aboutVar = IntVar();
mb.menu.add_checkbutton(label = 'About', variable = aboutVar);
mb.pack();


##################################SELECT_MODES#####################################################


root.title("Modes");

label = tk.Label(root, text = "Selected Mode: ");
label.pack(pady = 50);


combo_box = ttk.Combobox(root, values = Modes, state = 'readonly');
combo_box.pack(pady = 10);


combo_box.set("Off"); #default state
combo_box.bind("<<ComboboxSelected>>", select_mode); #allows user to select mode




##Making scales and setting it to default value

#LowerRateLimit
label_LowerRateLimit = Label(root, text = Programable_Paramters[0]); 
s_LowerRateLimit = Scale(root, from_=Lower_Rate_Limit[0], to=Lower_Rate_Limit[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_LowerRateLimit.set(Lower_Rate_Limit[1]); #sets lower rate limit to nominal value

#UpperRateLimit
label_UpperRateLimit = Label(root, text = Programable_Paramters[1]); 
s_UpperRateLimit = Scale(root, from_=Upper_Rate_Limit[0], to=Upper_Rate_Limit[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_UpperRateLimit.set(Upper_Rate_Limit[1]);

#AtrialAmplitude
label_AtrialAmplitude = Label(root, text = Programable_Paramters[2]); 
s_AtrialAmplitude = Scale(root, from_=Atrial_Amplitude[0], to=Atrial_Amplitude[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_AtrialAmplitude.set(Atrial_Amplitude[1]); 


#AtrialPulesWidth
label_AtrialPulesWidth = Label(root, text = Programable_Paramters[3]); 
s_AtrialPulesWidth = Scale(root, from_=Atrial_Pules_Width[0], to=Atrial_Pules_Width[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_AtrialPulesWidth.set(Atrial_Pules_Width[1]);

#VentricularAmplitude
label_VentricularAmplitude = Label(root, text = Programable_Paramters[4]); 
s_VentricularAmplitude = Scale(root, from_=Ventricular_Amplitude[0], to=Ventricular_Amplitude[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_VentricularAmplitude.set(Ventricular_Amplitude[1]);

#VentricularPulseWidth
label_VentricularPulseWidth = Label(root, text = Programable_Paramters[5]); 
s_VentricularPulseWidth = Scale(root, from_=Ventricular_Pulse_Width[0], to=Ventricular_Pulse_Width[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_VentricularPulseWidth.set(Ventricular_Pulse_Width[1]);

#VRP
label_VRP = Label(root, text = Programable_Paramters[6]); 
s_VRP = Scale(root, from_=VRP[0], to=VRP[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_VRP.set(VRP[1]);

#ARP
label_ARP = Label(root, text = Programable_Paramters[7]); 
s_ARP = Scale(root, from_=ARP[0], to=ARP[2], orient = HORIZONTAL); #creates scale from 0 to 100
s_ARP.set(ARP[1]);




#Puts scales into a list
sList = [s_LowerRateLimit, s_UpperRateLimit,s_AtrialAmplitude,s_AtrialPulesWidth,s_VentricularAmplitude,s_VentricularPulseWidth, s_VRP, s_ARP];

#Puts labels into a list
lList = [label_LowerRateLimit, label_UpperRateLimit, label_AtrialAmplitude,label_AtrialPulesWidth,label_VentricularAmplitude, label_VentricularPulseWidth,
         label_VRP, label_ARP];


update_temp_values();


save_button = Button(root, text="Save", command=save_parameters);
save_button.pack(pady=20);


Button(root, text="Print Parameters", command=print_parameters).pack()


root.mainloop(); #runs application
