from tkinter import * #imports all tkinter classes
import tkinter as tk
from tkinter import ttk

from time import strftime #gets system's time
from datetime import datetime


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

root.title("Modes");

label = tk.Label(root, text = "Selected Mode: ");
label.pack(pady = 5);


combo_box = ttk.Combobox(root, values = ["AOO", "VOO", "AAI", "VVI"], state = 'readonly');
combo_box.pack(pady = 10);

combo_box.set("AOO"); #default state

combo_box.bind("<<ComboboxSelected>>", select_mode);


'''
mode_AOO = IntVar();
Checkbutton(root, text = 'AOO', variable = mode_AOO).place(x=200, y=300);

mode_VOO = IntVar();
Checkbutton(root, text = 'VOO', variable = mode_VOO).place(x=200, y=325);

mode_AAI = IntVar();
Checkbutton(root, text = 'AAI', variable = mode_AAI).place(x=200, y=350);

mode_VVI = IntVar();
Checkbutton(root, text = 'VVI', variable = mode_VVI).place(x=200, y=375);
'''



#######################################SLIDER#######################################################


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

def successful_login(): #function
    root.destroy(); #close main window

    login = tk.Tk();
    login.title("Sceond Screen");
    login.geometry("1080x1080");
    login.mainloop();
    
    #abc = Toplevel(root);
    
    
    
    
    
    
sucesssful_login_button = Button(root, text = "Sucessful_Login", command = successful_login).place(x=400, y=600);



    

    
    



root.mainloop(); #runs application


