from tkinter import * #imports all tkinter classes
import tkinter as tk
from tkinter import ttk

from time import strftime #gets system's time
from datetime import datetime


# programable paramters [1=lower limit, 2=nominal, 3=upper limit, 4=temporary paramater, 5=permanent parameter]
Lower_Rate_Limit = [30,60,175,60,60] #ppm
Upper_Rate_Limit = [50,120,175,120,120] #ppm
Atrial_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Atrial_Pules_Width = [0.05,0.4,1.9,0.4,0.4] #ms
Ventricular_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Ventricular_Pulse_Width = [0.05,0.4,1.9,0.4,0.4] #ms
VRP = [150,320,500,320,320] #ms
ARP = [150,250,500,250,250] #ms

# Const 
Modes = ["Off", "AOO","VOO", "AAI", "VVI"]
Programable_Paramters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pules Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"]
Mode_Parameters = [[False,False,False,False,False,False,False,False],
                   [True,True,True,True,False,False,False,False],
                   [True,True,False,False,True,True,False,False],
                   [True,True,True,True,False,False,False,True],
                   [True,True,False,False,True,True,True,False]]










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


###############################OPEN_SECOND_WINDOW################################################

def open_Second_Window(): #function
    second = Toplevel(root);
    second.title("Second Screen");
    second.geometry("1080x1080");


###button_to_open_second window###

open_window_button = Button(root, text = "Open Second Screen", command = open_Second_Window);
open_window_button.pack(pady=20);



###############################CLOCK#############################################################

#live clock
'''
def time():
    string = strftime('%H:%M:%S %p');
    lbl.config(text = string);
    lbl.after(1000, time);

lbl = Label(root, font =('calibri', 40, 'bold'), background='purple', foreground='white');
lbl.pack(anchor = 'center')
time()
'''

def set_clock():
    #get user inputs
    date = date.get();
    time = time.get();

Label(root, text = "Enter Date (YYYY-MM-DD): ").pack(pady=5)
date = Entry(root)
date.pack();

Label(root, text = "Enter Time (HH:MM:SS): ").pack(pady=5);
time = Entry(root);
time.pack();

Button(root, text = "Set Clock", command = set_clock).pack(pady=10);

confirmation_label = Label(root, text= "");
confirmation_label.pack(pady=5);



##################################SELECT_MODES#####################################################


def select_mode(event):

    selected_mode = combo_box.get();
    label.config(text = "Selected Mode: " + selected_mode);
    parameters(selected_mode);





root.title("Modes");

label = tk.Label(root, text = "Selected Mode: ");
label.pack(pady = 50);


combo_box = ttk.Combobox(root, values = Modes, state = 'readonly');
combo_box.pack(pady = 10);




combo_box.set("Off"); #default state
combo_box.bind("<<ComboboxSelected>>", select_mode); #allows user to select mode


#LowerRateLimit
label_LowerRateLimit = Label(root, text = Programable_Paramters[0]); 
s_LowerRateLimit = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100

#UpperRateLimit
label_UpperRateLimit = Label(root, text = Programable_Paramters[1]); 
s_UpperRateLimit = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100


#AtrialAmplitude
label_AtrialAmplitude = Label(root, text = Programable_Paramters[2]); 
s_AtrialAmplitude = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100

#AtrialPulesWidth
label_AtrialPulesWidth = Label(root, text = Programable_Paramters[3]); 
s_AtrialPulesWidth = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100


#VentricularAmplitude
label_VentricularAmplitude = Label(root, text = Programable_Paramters[4]); 
s_VentricularAmplitude = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100

#VentricularPulseWidth
label_VentricularPulseWidth = Label(root, text = Programable_Paramters[5]); 
s_VentricularPulseWidth = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100

#VRP
label_VRP = Label(root, text = Programable_Paramters[6]); 
s_VRP = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100

#ARP
label_ARP = Label(root, text = Programable_Paramters[7]); 
s_ARP = Scale(root, from_=0, to=100, orient = HORIZONTAL); #creates scale from 0 to 100



sList = [s_LowerRateLimit, s_UpperRateLimit,s_AtrialAmplitude,s_AtrialPulesWidth,s_VentricularAmplitude,s_VentricularPulseWidth, s_VRP, s_ARP];

lList = [label_LowerRateLimit, label_UpperRateLimit, label_AtrialAmplitude,label_AtrialPulesWidth,label_VentricularAmplitude, label_VentricularPulseWidth,
         label_VRP, label_ARP];





'''
AOO - Lower Rate Limit, Upper Rate Limit, Atrial Amplitude, Atrial Pulse Width
VOO - Lower Rate Limit, Upper Rate Limit,Ventricular Amplitude, Ventricular Pulse Width
AAI - Lower Rate Limit, Upper Rate Limit, Atrial Amplitude, Atrial Pulse Width, ARP
VVI - Lower Rate Limit, Upper Rate Limit,Ventricular Amplitude, Ventricular Pulse Width, VRP
'''




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


            
    

    




#######################################SLIDER#######################################################

'''
label_LowerRateLimit = Label(root, text = "Lower Rate Limit").place(x=100, y= 50); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 70); #creates scale from 0 to 100
#s.pack();

label_UpperRateLimit = Label(root, text = "Upper Rate Limit").place(x=100, y= 120); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 140); #creates scale from 0 to 100

label_AtrialAmplitude = Label(root, text = "Atrial Amplitude").place(x=100, y= 190); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 210); #creates scale from 0 to 100

label_AtrialPulesWidth = Label(root, text = "Atrial Pules Width").place(x=100, y= 260); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 280); #creates scale from 0 to 100

label_VentricularAmplitude = Label(root, text = "Ventricular Amplitude").place(x=100, y= 330); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 350); #creates scale from 0 to 100

label_VentricularPulseWidth = Label(root, text = "Ventricular Pulse Width").place(x=100, y= 400); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 420); #creates scale from 0 to 100

label_VRP = Label(root, text = "VRP").place(x=100, y= 470); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 490); #creates scale from 0 to 100

label_ARP = Label(root, text = "ARP").place(x=100, y= 540); 
s = Scale(root, from_=0, to=100, orient = HORIZONTAL).place(x=100, y= 560); #creates scale from 0 to 100
'''


#########################################SAVE_BUTTON#####################################################

#right now its just a button that says save but DOESNT DO ANYTHING

save_button = Button(root, text = "Save") #, command = open_Second_Window);
save_button.pack(pady=20);



'''
###OPENING NEW WINDOW###

root.title('Hello'); #main window titled 'Hello'
second = Toplevel(); #creates new sperate window
second.title('Hello2');


label = Label(window, text = "Hello World", font = ('Arial', 40), fg = 'white', bg = "#CBC3E3") #sets text settings
label.place(x=200, y=300) #displays text
 
button = Button(window, text = "Yes", font = ('Arial', 40), fg = 'white', bg = "#CBC3E3") #sets button settings
button.place(x= 250, y=400) #displays button

#button.config(command = name) - Sets button to function

second.mainloop(); #runs application


###############################OPEN_SECOND_WINDOW################################################

def open_Second_Window(): #function
    second = Toplevel(root);
    second.title("Second Screen");
    second.geometry("1080x1080");


###button_to_open_second window###

open_window_button = Button(root, text = "Open Second Screen", command = open_Second_Window);
open_window_button.pack(pady=20);

'''

#############################Opens_new_screen_and_closes_old_screen############################################## 
def successful_login(): #function
    root.destroy(); #close main window

    login = tk.Tk();
    login.title("Sceond Screen");
    login.geometry("1080x1080");
    login.mainloop();
    
    #abc = Toplevel(root);
    
        
sucesssful_login_button = Button(root, text = "Sucessful_Login", command = successful_login).place(x=400, y=600);


root.mainloop(); #runs application






