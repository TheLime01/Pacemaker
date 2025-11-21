from tkinter import *
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import subprocess
import serial
from serial.tools import list_ports
import time
import threading
import struct
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



from tkinter import font

'''
Questions/Issues

- make it look better
- Assurance case - weeks , 10-11 slides, etc

Got the saving to work for the parameters between uses, but
    1) when the actual pacemaker is plugged out and then plugged back in again it goes to its intial values
    2) it doesnt save the mode but it'll save the changes made to the other numbers

    3) how will it work for different users?
    4) how will it work for the Off parameter?

 - How the Off programmable parameter work? (already implemented but make sure)
 - The sliders only increment by the amount on the PACEMAKER doc, but should the box only take in certain values too?



'''


'''
Parameters Name                              Range                     Increment              Type

Lower Rate Limit                    [30, 60, 175, 60, 60]                  5                   
Upper Rate Limit                    [50, 120, 175, 120, 120]               5                   
Atrial Amplitude*                   [0.1, 5, 5, 5, 5]                     0.1                  
Atrial Pulse Width*                 [1, 1, 30, 1, 1]                       1                   
Ventricular Amplitude*              [0.1, 5, 5, 5, 5]                     0.1                  
Ventricular Pulse Width*            [1, 30, 1, 1, 1]                       1                   
VRP                                 [150, 320, 500, 320, 320]              10                  
ARP                                 [150, 250, 500, 250, 250]              10                  
Atrial Sensitivity**                [0, 0, 5, 0, 0]                       0.1                  
Ventricular Sensitivity**           [0, 0, 5, 0, 0]                       0.1                  



*adjusted for deliverable 2
**added for deliverable 2

'''


############################## Serial ##############################


class SerialMonitor:
    def __init__(self, param_mgr=None):
        self.last_port = None  # Stores last connection
        self.Status = "Disconnected"  # Default status is disconnected
        self.Port_Description = "JLink CDC UART Port"  # Pacemaker description
        self.param_mgr = param_mgr  # <-- store reference

        # Start monitor thread (daemon so it won't block program exit)
        self.thread = threading.Thread(target=self.Monitor_ports, daemon=True)
        self.thread.start()

    def On_Connect(self, port):
        try:
            ser = serial.Serial(port, 115200, timeout=5)  # Connects serial
            print("Connected to", ser.name)
            
            # Send read request packet
            if self.param_mgr:
                self.Packet_Serial(0x22, self.param_mgr)
                ser.write(self.packet)
                ser.flush()
                print("Read request sent successfully.")
            else:
                print("Warning: No ParameterManager attached; skipping Read_Request")

            time.sleep(0.5)
            response = ser.read(64)  # Expect 64 bytes if echo
            print(f"Received {len(response)} bytes:", response.hex())
            if len(response) == 64:  # If same bytes sent back
                unpacked = struct.unpack("<dddddddd", response)  # Unpacks the packet
                print("Unpacked:", unpacked)
                (
                    lrl,
                    url,
                    atrial_amp,
                    atrial_pw,
                    ventricular_amp,
                    ventricular_pw,
                    vrp,
                    arp,
                ) = unpacked

                if self.param_mgr is None:
                    print("Warning: No ParameterManager attached; cannot write received values")
                else:
                    pm = self.param_mgr
                    pm.parameter_values["Lower Rate Limit"][4] = lrl
                    pm.parameter_values["Upper Rate Limit"][4] = url
                    pm.parameter_values["Atrial Amplitude"][4] = atrial_amp
                    pm.parameter_values["Atrial Pulse Width"][4] = atrial_pw
                    pm.parameter_values["Ventricular Amplitude"][4] = ventricular_amp
                    pm.parameter_values["Ventricular Pulse Width"][4] = ventricular_pw
                    pm.parameter_values["VRP"][4] = vrp
                    pm.parameter_values["ARP"][4] = arp
            else:
                print("Received incomplete packet")
            ser.close()
        except serial.SerialException as e:
            print(f"Serial Port Error: {e}")
    
    def Monitor_ports(self):
        while True: #Continuously checks
            ports = list(list_ports.comports()) #Collects and stores ports in a list
            pacemaker_port = None #Current pacemaker port set to none first

            #Looks only for the pacemaker device
            for p in ports:
                if self.Port_Description in p.description: #Checks each port description to see if there is a match
                    pacemaker_port = p.device #Stores the match
                    break

            #If Pacemaker is found
            if pacemaker_port:
                if pacemaker_port != self.last_port:  #Checks for new connection
                    try:
                        self.On_Connect(pacemaker_port) #Gets sent to serial
                        self.last_port = pacemaker_port #Stores the current port to check for changes
                    except Exception as e:
                        print("On_Connect error:", e)
                self.Status = "Connected"

            #If Pacemaker is not found
            else:
                if self.last_port is not None: #Checks if pacemaker was disconnected
                    print("Pacemaker disconnected")
                self.last_port = None
                self.Status = "Disconnected"
            time.sleep(1)

    def Write_Serial(self, param_mgr=None):
        pm = param_mgr or self.param_mgr  # <-- default to stored reference
        if pm is None:
            print("Write_Serial: No ParameterManager provided/attached.")
            return
        self.Packet_Serial(0x55, pm)
        try:
            ser = serial.Serial(self.last_port, 115200, timeout=1)
            time.sleep(2)
            ser.write(self.packet)  # Writes packet
            ser.flush()
            print("Packet sent successfully.")
            ser.close()
        except serial.SerialException as e:
            print(f"Serial Port Error: {e}")
        

    def Read_Request(self, param_mgr=None): # NOT USED RIGHT NOW
        pm = param_mgr or self.param_mgr  # <-- default to stored reference
        if pm is None:
            print("Read_Request: No ParameterManager provided/attached.")
            return
        self.Packet_Serial(0x22, pm)
        try:
            ser = serial.Serial(self.last_port, 115200, timeout=1)
            time.sleep(2)
            ser.write(self.packet)  # Writes packet
            ser.flush()
            print("Read request sent successfully.")
            ser.close()
        except serial.SerialException as e:
            print(f"Serial Port Error: {e}")

    def Packet_Serial(self, function_code, param_mgr=None):
        pm = param_mgr or self.param_mgr
        if pm is None:
            raise ValueError("Packet_Serial: ParameterManager is required")

        # Packet Parameters - using 2x uint8 + 8x float64 = 66 bytes (matches your unpack)
        self.Sync = 0x16
        self.FN_Code = function_code  # 0x55 setting params, 0x22 echo

        self.Lower_Rate_Limit = pm.parameter_values["Lower Rate Limit"][4]
        self.Upper_Rate_Limit = pm.parameter_values["Upper Rate Limit"][4]
        self.Atrial_Amplitude = pm.parameter_values["Atrial Amplitude"][4]
        self.Atrial_Pulse_Width = pm.parameter_values["Atrial Pulse Width"][4]
        self.Ventricular_Amplitude = pm.parameter_values["Ventricular Amplitude"][4]
        self.Ventricular_Pulse_Width = pm.parameter_values["Ventricular Pulse Width"][4]
        self.VRP = pm.parameter_values["VRP"][4]
        self.ARP = pm.parameter_values["ARP"][4]
        # Sensitivities exist in pm but are not included in the current packet

        # Build packet with doubles, to match the 66-byte expectation and your unpack format
        self.packet = struct.pack(
            "<BBdddddddd",
            int(self.Sync),
            int(self.FN_Code),
            float(self.Lower_Rate_Limit),
            float(self.Upper_Rate_Limit),
            float(self.Atrial_Amplitude),
            float(self.Atrial_Pulse_Width),
            float(self.Ventricular_Amplitude),
            float(self.Ventricular_Pulse_Width),
            float(self.VRP),
            float(self.ARP),
        )
        print(f"Packet ({len(self.packet)} bytes):", " ".join(f"{b:02X}" for b in self.packet))


    def Read_Device_Values(self):
        """
        Reads the current device values from the SerialMonitor's attached ParameterManager.
        Returns a dict {param_name: value}.
        """
        if self.Status != "Connected":
            print("Read_Device_Values: Device not connected, returning current ParameterManager values")
            return {param: vals[4] for param, vals in self.param_mgr.parameter_values.items()}

        # If device connected, attempt to read (reuse On_Connect logic)
        try:
            ser = serial.Serial(self.last_port, 115200, timeout=1)
            self.Packet_Serial(0x22, self.param_mgr)  # request current values
            ser.write(self.packet)
            ser.flush()
            time.sleep(0.5)
            response = ser.read(64)
            ser.close()
            if len(response) == 64:
                unpacked = struct.unpack("<dddddddd", response)
                (
                    lrl, url, atrial_amp, atrial_pw,
                    ventricular_amp, ventricular_pw, vrp, arp
                ) = unpacked

                values = {
                    "Lower Rate Limit": lrl,
                    "Upper Rate Limit": url,
                    "Atrial Amplitude": atrial_amp,
                    "Atrial Pulse Width": atrial_pw,
                    "Ventricular Amplitude": ventricular_amp,
                    "Ventricular Pulse Width": ventricular_pw,
                    "VRP": vrp,
                    "ARP": arp
                }

                # Update your ParameterManager
                for param, val in values.items():
                    self.param_mgr.parameter_values[param][4] = val

                return values
            else:
                print("Read_Device_Values: Incomplete response, returning current values")
                return {param: vals[4] for param, vals in self.param_mgr.parameter_values.items()}

        except serial.SerialException as e:
            print("Read_Device_Values Serial Error:", e)
            return {param: vals[4] for param, vals in self.param_mgr.parameter_values.items()}



############################## Parameters / Data ##############################

class ParameterManager:

    def __init__(self):
        self.Device_model = "Pacemaker"
        self.Device_serial_number = "HOOO25"
        self.DCM_serial_number = "400325598"
        self.Model_number = "4230"
        self.Version_number = "1.0"

        # Modes and parameters
        self.Modes = ["AOO", "VOO", "AAI", "VVI", "AOOR", "VOOR", "AAIR", "VVIR"]
        self.Parameters_Units = [" ppm", " ppm", " V", " ms", " V", " ms", " ms", " ms", "mV", "mV"]
        self.mode_parameters = {
            "AOO": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width"],
            "VOO": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width"],
            "AAI": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width", "ARP", "Atrial Sensitivity"],
            "VVI": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "Ventricular Sensitivity"],
            "AOOR": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width"],
            "VOOR": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width"],
            "AAIR": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width", "ARP", "Atrial Sensitivity"],
            "VVIR": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "Ventricular Sensitivity"]
        }

        # Mode and parameter values
        self.Mode = ["AOO", "AOO"]  #0=temporary paramater, 1=permanent parameter
        self.parameter_values = { #min, nominal, max, temp, permanent
            "Lower Rate Limit": [30, 60, 175, 60, 60],
            "Upper Rate Limit": [50, 120, 175, 120, 120],
            "Atrial Amplitude": [0.1, 5, 5, 5, 5],
            "Atrial Pulse Width": [1, 1, 30, 1, 1],
            "Ventricular Amplitude": [0.1, 5, 5, 5, 5],
            "Ventricular Pulse Width": [1, 30, 1, 1, 1],
            "VRP": [150, 320, 500, 320, 320],
            "ARP": [150, 250, 500, 250, 250],
            "Atrial Sensitivity": [0, 0, 5, 0, 0],
            "Ventricular Sensitivity": [0, 0, 5, 0, 0]
        }


############################## User management ##############################

class UserManager:

    def __init__(self, filename="userdata.json"):
        self.filename = filename

    def userdata_exists(self):
        #check if userdata.json file exists, creates empty one if not
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"registered users": []}
            with open(self.filename, 'w') as file:
                json.dump(data, file, indent=4)

    def Verify_account(self, username, password):
        #Check if username and password is correct
        self.userdata_exists()
        with open(self.filename, "r") as file:
            data = json.load(file)
        for user in data['registered users']:
            if username.strip() == user['username'] and password.strip() == user['password']:
                return True
        return False

    def Add_new_user(self, username, password):
        #Checks sign up conditions and if it's all correct then signs up the user
        self.userdata_exists()
        with open(self.filename, "r") as file:
            data = json.load(file)

        if len(data['registered users']) > 9:  #checks if user list is full
            return False, "User list at capacity."
        new_user = {"username": username.strip(), "password": password.strip()}

        #checks username and password lengths
        if len(new_user['username']) < 6 or len(new_user['password']) < 6:
            return False, "Username & password must be at least 6 characters."
        elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
            return False, "Username & password cannot exceed 25 characters."
        for user in data['registered users']:  #checks if username already exists
            if new_user['username'] == user['username']:
                return False, "Username already taken, please try again."

        #adds new user
        data["registered users"].append(new_user)
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)
            return True, "New user added, please sign in!"


############################## Egram Graphs ##############################

class EgramViewer(tk.Toplevel):

    def __init__(self, parent, time_data, voltageA_data, voltageV_data):
        super().__init__(parent)
        self.title("Egram Data Viewer")
        self.geometry("800x600")
        self.bg_colour = "#CBC3E3"
        self.config(background=self.bg_colour)
        try:
            self.iconphoto(True, PhotoImage(file="Pacemaker Logo.png"))
        except Exception:
            pass

        # max length for deques
        self.maxlen = 4000

        # initialize deques
        self.time_data = deque(time_data, maxlen=self.maxlen)
        self.voltageA_data = deque(voltageA_data, maxlen=self.maxlen)
        self.voltageV_data = deque(voltageV_data, maxlen=self.maxlen)

        # flags for showing graphs
        self.show_atrium = True
        self.show_ventricle = True

        # plot buttons
        button_frame = tk.Frame(self, bg=self.bg_colour)
        button_frame.pack(side=tk.TOP, pady=10)

        self.atrium_btn = tk.Button(button_frame, text="Toggle Atrium", command=self.toggle_atrium)
        self.atrium_btn.pack(side=tk.LEFT, padx=8)

        self.ventricle_btn = tk.Button(button_frame, text="Toggle Ventricle", command=self.toggle_ventricle)
        self.ventricle_btn.pack(side=tk.LEFT, padx=8)

        # figure and subplots
        self.fig = Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
        self.axA = self.fig.add_subplot(211)
        self.axV = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.draw_graphs()

    def toggle_atrium(self):
        self.show_atrium = not self.show_atrium
        self.draw_graphs()

    def toggle_ventricle(self):
        self.show_ventricle = not self.show_ventricle
        self.draw_graphs()

    def draw_graphs(self):
        self.axA.clear()
        self.axV.clear()

        if len(self.time_data) == 0:
            self.canvas.draw()
            return

        # compute scrolling window edges
        last_time = self.time_data[-1]
        left_edge = last_time - (self.maxlen - 1)

        # atrium plot
        if self.show_atrium:
            self.axA.plot(self.time_data, self.voltageA_data, color="blue")
            self.axA.set_title("Atrium Signals")
            self.axA.set_xlabel("Time (ms)")
            self.axA.set_ylabel("Voltage (mV)")
            self.axA.grid(True)
            self.axA.set_xlim(left_edge, last_time)
            self.axA.set_visible(True)
        else:
            self.axA.set_visible(False)

        # ventricle plot
        if self.show_ventricle:
            self.axV.plot(self.time_data, self.voltageV_data, color="red")
            self.axV.set_title("Ventricle Signals")
            self.axV.set_xlabel("Time (ms)")
            self.axV.set_ylabel("Voltage (mV)")
            self.axV.grid(True)
            self.axV.set_xlim(left_edge, last_time)
            self.axV.set_visible(True)
        else:
            self.axV.set_visible(False)

        self.canvas.draw()

    def update_graph(self, new_time, new_voltageA=None, new_voltageV=None):
        self.time_data.append(new_time)
        if new_voltageA is not None:
            self.voltageA_data.append(new_voltageA)
        if new_voltageV is not None:
            self.voltageV_data.append(new_voltageV)
        self.draw_graphs()


############################## GUI ##############################

class PacemakerGUI:

    def __init__(self):
        # Initialize managers
        self.param_mgr = ParameterManager()
        self.serial_monitor = SerialMonitor(self.param_mgr)
        self.user_mgr = UserManager()
        

        # Setup main login Window
        self.Window = Tk()  #Initiates a window
        self.Window.geometry("1080x1080") #Sets size of the window
        self.Window.title("Pacemaker") #Sets the title


        self.high_contrast = False


        try:
            Icon = PhotoImage(file="Pacemaker Logo.png")  #Sets the icon
            self.Window.iconphoto(True, Icon)  #Displays the icon
        except Exception:
            # preserve original behavior (it assumed file exists); if not, continue silently
            pass

        self.Window.config(background="#CBC3E3")  # Sets colour of background

        self.root = None  #will be created on successful login
        self.Status_button = None
        self.label = None
        self.combo_box = None
        self.sliders = {}
        self.Status = self.serial_monitor.Status  #mirror serial status (kept in sync via update)

        #Create initial widgets
        self._create_login_widgets()


    ############################## Functions ##############################

    def About(self):
        About_window = Toplevel()  #Initiates about window
        About_window.geometry("360x180")
        About_window.title("About")  #Sets title

        Model_Number = Label(About_window, text="Model Number: " + self.param_mgr.Model_number, font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        Model_Number.place(x=10, y=10)  #Displays model number text

        Software_Revision_Number = Label(About_window, text="Software Revision Number: Version " + self.param_mgr.Version_number, font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        Software_Revision_Number.place(x=10, y=40)  #Displays software revision number text

        DCM_Serial_Number = Label(About_window, text="DCM Serial Number: " + self.param_mgr.DCM_serial_number, font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        DCM_Serial_Number.place(x=10, y=70)  #Displays DCM serial number text

        Institution_Name = Label(About_window, text="Institution Name: McMaster University", font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        Institution_Name.place(x=10, y=100)  #Displays institution name text

        About_window.mainloop()  #Displays the about window

    def Get_input(self):  #Get username and password and returns it
        Username_input = self.Username_box.get()
        Password_input = self.Password_box.get()
        return Username_input, Password_input

    def Verify_account(self, username, password):  #Check if username and password is correct
        return self.user_mgr.Verify_account(username, password)

    def update_status_button(self):

        if self.Status_button:
            #read latest status from serial_monitor
            self.Status = self.serial_monitor.Status
            self.Status_button.config(text=self.Status)
      
            # Enable or disable save button based on connection
            if self.Status == "Connected":
                self.save_button.config(state="normal")
            else:
                self.save_button.config(state="disabled")

        #schedule again
        try:
            self.root.after(100, self.update_status_button)
        except Exception:
            #If root was closed, ignore
            pass

    def Successful_login(self):  #Gives access to my account page

        self.Window.destroy();  #Close main window
        self.root = tk.Tk()  #Open new window
        self.root.title("My Account")
        self.root.geometry("1080x1080")
        self.root.config(background="#CBC3E3")  #Sets colour of background



        ######################## Fonts ###########################
        
        self.font_size = 14  # default size
        self.font_family = "Arial"

        # Create a font object for labels, buttons, and entries
        self.global_font = font.Font(family=self.font_family, size=self.font_size)

        increase_btn = Button(self.root, text="A+", command=self.increase_font, font=self.global_font)
        increase_btn.place(x=900, y=20)

        decrease_btn = Button(self.root, text="A-", command=self.decrease_font, font=self.global_font)
        decrease_btn.place(x=950, y=20)

        contrast_btn = Button(self.root, text="Toggle Contrast", command=self.toggle_contrast_logged_in, font=self.global_font)
        contrast_btn.place(x=900, y=50)


        ######################## Fonts ###########################

        About_button = Button(self.root, text="About", font=self.global_font, fg='black', bg="white")  #Sets text settings
        About_button.place(x=15, y=15)  #Displays about button
        About_button.config(command=self.About)  #Sets button to about function

        Quit_button = Button(self.root, text="Quit", font=self.global_font, fg='black', bg="white")  #Sets text settings
        Quit_button.place(x=1010, y=15)  #Displays quit button
        Quit_button.config(command=self.Quit2)  #Sets button to quit function

        # Status button
        self.Status_button = Button(self.root, text=self.Status, font=self.global_font, fg='black', bg="white")
        self.Status_button.place(x=15, y=725)

        # Build mode selector and sliders
        self.combo_box_create()  #makes the drop-down menu to choose mode
        self.initializes_sliders()  #makes all the sliders

        self.sync_sliders_with_device()    # sync sliders to device
        self.select_mode(self.param_mgr.Mode[0])
        self.update_temp_values()       

        
        #self.select_mode(self.param_mgr.Mode[0])  #sets the starting mode (AOO) with correct states of sliders
        #self.update_temp_values()  #keeps updating the values in the slides

        self.save_button = Button(self.root, text="Save Parameters", command=self.save_parameters, font=self.global_font)
        self.save_button.place(x=495, y=300)

        temp_report_button = Button(self.root, text="Temporary Report", command=lambda: self.export_report("Temporary"), font=self.global_font)
        temp_report_button.place(x=490, y=400)

        Bradycardia_report_button = Button(self.root, text="Bradycardia Report", command=lambda: self.export_report("Bradycardia"), font=self.global_font)
        Bradycardia_report_button.place(x=490, y=450)

        self.graph_button = Button(self.root, text="View Egram Graphs", command=self.open_graph_window, font=self.global_font)
        self.graph_button.place(x=490, y=500)

        self.update_status_button()

    
    def open_graph_window(self):
        # disable combo box, save button, sliders and entry boxes
        self.combo_box.config(state="disabled")
        self.save_button.config(state="disabled")
        self.graph_button.config(state="disabled")
        for param, (scale, entry, _, toggle, _) in self.sliders.items():
            scale.config(state="disabled")
            entry.config(state="disabled")
            if toggle:
                toggle.config(state="disabled")

        # FAKE DATA FOR NOW!!!!!!
        time_data = [i for i in range(4000)]
        voltageA_data = [0 for _ in range(3250)] + [0.5 for _ in range(250)] + [-0.2 for _ in range(250)] + [0 for _ in range(250)]
        voltageV_data = [0 for _ in range(3250)] + [-0.5 for _ in range(300)] + [0.2 for _ in range(200)] + [0 for _ in range(250)]

        # Create egram graph window
        graph_window = EgramViewer(self.root, time_data, voltageA_data, voltageV_data)

        # When graph window closes, re-enable sliders
        def on_close():
            self.combo_box.config(state="readonly")
            self.save_button.config(state="normal")
            self.graph_button.config(state="normal")
            self.select_mode(self.combo_box.get())
            graph_window.destroy()

        graph_window.protocol("WM_DELETE_WINDOW", on_close)


    def combo_box_create(self):  #function to make dropdown menu
        self.root.title("Modes")
        self.label = tk.Label(self.root, text="Selected Mode: ", font=self.global_font, fg='black')
        self.label.place(x=450, y=90)

        self.combo_box = ttk.Combobox(self.root, values=self.param_mgr.Modes, state='readonly', font=self.global_font)
        self.combo_box.place(x=450, y=130)

        self.combo_box.set("AOO")  #default state
        self.combo_box.bind("<<ComboboxSelected>>", self.select_mode)

    def select_mode(self, event):  #updates sliders - according to mode


        selected_mode = None
        
        try:
            #if called from bind, event will be passed; get current combo value
            selected_mode = self.combo_box.get()
        except Exception:
            #If called directly with a mode (as in Successful_login), event will be a string
            if isinstance(event, str):
                selected_mode = event
            else:
                selected_mode = self.param_mgr.Mode[0]

        self.label.config(text="Selected Mode: " + selected_mode)

        self.root.focus()  # or self.label.focus_set()

        allowed = self.param_mgr.mode_parameters[selected_mode]  #get the parameters that are relevent to the mode

        for param, (scale, entry, var, toggle, toggle_var) in self.sliders.items():

            
            if param in allowed:  #if the parameter is in the current mode make available, else no
                scale.config(state="normal")
                entry.config(state="normal")
                if toggle:
                    toggle_var.set(False)
                    toggle.config(state="normal")
            else:
                scale.config(state="disabled")
                entry.config(state="disabled")
                if toggle:
                    toggle_var.set(True)
                    toggle.config(state="disabled")

    def create_slider_with_entry(self, parent, label_text, from_, to, x, y, initial, has_toggle=False):  #can type in entry for slider
        var = tk.DoubleVar(value=initial)  #creates a double int and initializes it to nominal value


        tk.Label(parent, text=label_text, font=self.global_font).place(x=x, y=y)  #puts parameter name above the slider

        if label_text == "Lower Rate Limit" or label_text == "Upper Rate Limit":
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=5, variable=var, showvalue=False, length=150)
            

        elif label_text == "Atrial Amplitude" or label_text == "Ventricular Amplitude" or label_text == "Atrial Sensitivity" or label_text == "Ventricular Sensitivity":
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=0.1, variable=var, showvalue=False, length=150)

        elif label_text == "Atrial Pulse Width" or label_text == "Ventricular Pulse Width":
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=1, variable=var, showvalue=False, length=150)


        else:
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=10, variable=var, showvalue=False, length=150)
            
            
        # resolution - step size of decimal
        # variable=var --> scale widget is linked to var, meaning moving the slider updates var automatically
        # hides the default value display
        # pixel length of the slider
        scale.place(x=x, y=y + 20)

        #creates the box to type into
        entry = tk.Entry(parent, width=6, font=self.global_font)
        entry.place(x=x + 180, y=y + 30)
        entry.insert(0, str(initial))  #show the inital value

        entry.is_slider_related = True
        

        #shows min and max values of the sliders
        min_label = tk.Label(parent, text=str(from_), font=self.global_font)
        min_label.place(x=x, y=y + 40)  # min
        
        max_label = tk.Label(parent, text=str(to), font=self.global_font)
        max_label.place(x=x + 130, y=y + 40)  # max

        min_label.is_slider_related = True
        max_label.is_slider_related = True

        #when user types number into box
        def update_from_entry(event):
            try:
                val = float(entry.get())  #try coverting the text to number
                if from_ <= val <= to:  #can only be within the range
                    var.set(val)  #update value
                else:
                    print("Error")

            except ValueError:
                print("Error")

        #when user hits enter or clicks out - updates slider
        entry.bind("<Return>", update_from_entry)
        entry.bind("<FocusOut>", update_from_entry)

        #when slider moves - update box to show current value
        def update_from_scale(*args):  #called whenever the slider's value changes
            entry.delete(0, tk.END)  #clears entry box
            entry.insert(0, str(round(var.get(), 2)))  #inserts new number to 2 decimal places

        var.trace_add("write", update_from_scale)  #when sliders value changes - call function to update box

        
        if has_toggle:
            toggle_var = tk.BooleanVar(value=False)# True = slider enabled
            toggle = tk.Checkbutton(parent, text="Off", variable=toggle_var, font=self.global_font)
            toggle.place(x=x-70, y=y + 20)

        

            def toggle_slider():
                if toggle_var.get():
                    scale.config(state="disabled")
                    entry.config(state="disabled")
                    
                else:
                    scale.config(state="normal")
                    entry.config(state="normal")


            toggle_var.trace_add("write", lambda *args: toggle_slider())

        else:
            toggle = None
            toggle_var = None


        
        return scale, entry, var, toggle, toggle_var  #return scale, entry box and the shared value

    def initializes_sliders(self):  #initializes all the sliders

        self.sliders = {}

        # (parent, label, min value, max value, x pos, y pos, nominal value)
        self.sliders["Lower Rate Limit"] = self.create_slider_with_entry(self.root, "Lower Rate Limit", 30, 180, 150, 220, 60)
        self.sliders["Upper Rate Limit"] = self.create_slider_with_entry(self.root, "Upper Rate Limit", 50, 200, 150, 300, 120)
        self.sliders["Atrial Amplitude"] = self.create_slider_with_entry(self.root, "Atrial Amplitude", 0.1, 5.0, 150, 380, 5, has_toggle=True)

        self.sliders["Atrial Pulse Width"] = self.create_slider_with_entry(self.root, "Atrial Pulse Width", 1, 30, 150, 460, 1)
        self.sliders["Ventricular Amplitude"] = self.create_slider_with_entry(self.root, "Ventricular Amplitude", 0.1, 5.0, 710, 220, 5, has_toggle=True)

        self.sliders["Ventricular Pulse Width"] = self.create_slider_with_entry(self.root, "Ventricular Pulse Width", 1, 30, 710, 300, 1)
        self.sliders["VRP"] = self.create_slider_with_entry(self.root, "VRP", 150, 500, 710, 380, 320)
        self.sliders["ARP"] = self.create_slider_with_entry(self.root, "ARP", 150, 500, 710, 460, 250)

        self.sliders["Atrial Sensitivity"] = self.create_slider_with_entry(self.root, "Atrial Sensitivity", 0, 5, 150, 540, 0)
        self.sliders["Ventricular Sensitivity"] = self.create_slider_with_entry(self.root, "Ventricular Sensitivity", 0, 5, 710, 540, 0)




    def update_temp_values(self):

        for param, (scale, entry, var, toggle, toggle_var) in self.sliders.items():
            self.param_mgr.parameter_values[param][3] = var.get()  # only store temp value locally

        self.param_mgr.Mode[0] = self.combo_box.get()

        try:
            self.root.after(500, self.update_temp_values)
        except Exception:
            pass
        

    def save_parameters(self):
        for param in self.param_mgr.parameter_values:
            self.param_mgr.parameter_values[param][4] = self.param_mgr.parameter_values[param][3]  # save temp as permanent
        self.param_mgr.Mode[1] = self.combo_box.get()
        self.serial_monitor.Write_Serial(self.param_mgr)  # writes all parameters at once



################## Pacemaker Stuff #############################

    def sync_sliders_with_device(self):
        """Reads permanent values from pacemaker and sets sliders to match."""
        if self.serial_monitor.Status != "Connected":
            return

        values = self.serial_monitor.Read_Device_Values()

        for param, val in values.items():
            if param in self.param_mgr.parameter_values:
                self.param_mgr.parameter_values[param][4] = val  # permanent
                self.param_mgr.parameter_values[param][3] = val  # temporary
                if param in self.sliders:
                    scale, entry, var, toggle, toggle_var = self.sliders[param]
                    var.set(val)







    #creates a new report of the type given (Bradycardia or Temporary)
    def export_report(self, type: str):

        #saves current time and labels the output file
        current_datetime = datetime.now()
        file_name = type + "_Report-" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".txt"

        #uses i to output temp or brady paramaters
        i = 3
        if type == "Bradycardia":
            i = 4

        param_str = "\n\tMode: " + self.param_mgr.Mode[i - 3] + "\n"
        for param in self.param_mgr.mode_parameters[self.param_mgr.Mode[i - 3]]:

            value = self.param_mgr.parameter_values[param][i]

            if param in self.sliders:
                _,_,_,_,toggle_var = self.sliders[param]

                if toggle_var is not None and toggle_var.get():
                    value = "Off"
            
            param_str += f"\t{param}: {value}\n"

        #writes report
        with open(file_name, 'w') as file:
            file.write(type + " Parameters Report" +
                       "\nDate: " + current_datetime.strftime("%Y-%m-%d %H:%M:%S") +
                       "\nDevice Model: " + self.param_mgr.Device_model +
                       "\nSerial Number: " + self.param_mgr.Device_serial_number +
                       "\nDCM Serial Number: " + self.param_mgr.DCM_serial_number +
                       "\nApplication Model: " + self.param_mgr.Model_number +
                       "\nVersion Number: " + self.param_mgr.Version_number +
                       "\n----------------------------------" + param_str
                       )

        subprocess.Popen(["notepad.exe", file_name])

    def userdata_exists(self):
        #check is userdata.json file exists, creates empty one if not
        try:
            with open("userdata.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {
                "registered users": []
            }
            with open("userdata.json", 'w') as file:
                json.dump(data, file, indent=4)

    def Add_new_user(self, username, password):  #Checks sign up conditions and if it's all correct then signs up the user
        self.userdata_exists()
        with open("userdata.json", "r") as file:
            data = json.load(file)
        if len(data['registered users']) > 9:  #checks if user list is full
            return False, "User list at capacity."
        new_user = {
            "username": username.strip(),
            "password": password.strip()
        }

        #checks username and password lengths
        if len(new_user['username']) < 6 or len(new_user['password']) < 6:
            return False, "Username & password must be at least 6 characters."
        elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
            return False, "Username & password cannot exceed 25 characters."
        for user in data['registered users']:  # checks if username already exists
            if new_user['username'] == user['username']:
                return False, "Username already taken, please try again."

        #adds new user
        data["registered users"].append(new_user)
        with open("userdata.json", "w") as file:
            json.dump(data, file, indent=4)
            return True, "New user added, please sign in!"

    def Sign_in(self):  #Gets username and password and verifies if it's correct
        Username_input, Password_input = self.Get_input()
        Verify = self.Verify_account(Username_input, Password_input)
        if (Verify == True):
            self.Successful_login()
        else:
            Sign_in_label = Label(self.Window, text="Incorrect username/password", font=('Arial', 14), fg='black', bg="#CBC3E3")  #Sets text settings
            Sign_in_label.place(x=395, y=425)  #Displays sign in text
            Sign_in_label.after(3000, Sign_in_label.destroy)  #Removes sign in text after some time

    def Sign_up(self):  #Gets username and password and verifies sign up conditions
        Username_input, Password_input = self.Get_input()
        Verify, Message = self.Add_new_user(Username_input, Password_input)

        Sign_up_label = Label(self.Window, text=Message, font=('Arial', 14), fg='black', bg="#CBC3E3")  # Sets text settings
        Sign_up_label.place(x=350, y=425)  # Displays sign up text

        Sign_up_label.after(3000, Sign_up_label.destroy)  # Removes sign up text after some time

    def Quit(self):
        self.Window.destroy()  #Quits window

    def Quit2(self):
        if self.root:
            self.root.destroy()  #Quits secondary window

    ############################## Widgets (login window) ##############################

    def _create_login_widgets(self):
        # Labels



        self.font_size = 14
        self.font_family = "Arial"
        self.global_font = font.Font(family=self.font_family, size=self.font_size)

        increase_btn = Button(self.Window, text="A+", command=self.increase_font, font=self.global_font)
        increase_btn.place(x=900, y=20)

        decrease_btn = Button(self.Window, text="A-", command=self.decrease_font, font=self.global_font)
        decrease_btn.place(x=950, y=20)

        toggle_btn = Button(self.Window, text="Toggle Contrast", command=self.toggle_contrast)
        toggle_btn.place(x=800, y=20)




        
        Username_label = Label(self.Window, text="Username", font=self.global_font, fg='black', bg="#CBC3E3")
        Username_label.place(x=345, y=500)

        Password_label = Label(self.Window, text="Password", font=self.global_font, fg='black', bg="#CBC3E3")
        Password_label.place(x=345, y=550)

        # Buttons
        Welcome_button = Button(self.Window, text="Welcome :)", font=('Arial', 40), fg='black', bg="white")
        Welcome_button.place(x=375, y=250)

        About_button = Button(self.Window, text="About", font=self.global_font, fg='black', bg="white")
        About_button.place(x=15, y=15)

        About_button.config(command=self.About)

        Sign_in_button = Button(self.Window, text="Sign In", font=self.global_font, fg='black', bg="white")
        Sign_in_button.place(x=625, y=495)

        Sign_in_button.config(command=self.Sign_in)

        Sign_up_button = Button(self.Window, text="Sign Up", font=self.global_font, fg='black', bg="white")
        Sign_up_button.place(x=620, y=545)

        Sign_up_button.config(command=self.Sign_up)

        Quit_button = Button(self.Window, text="Quit", font=self.global_font, fg='black', bg="white")
        Quit_button.place(x=1010, y=15)

        Quit_button.config(command=self.Quit)

        # Entry Boxes
        self.Username_box = Entry(self.Window)  #Box for username input
        self.Password_box = Entry(self.Window)  #Box for password input
        self.Username_box.place(x=470, y=505)  #Display username box
        self.Password_box.place(x=470, y=555)  #Display password box



    ######################### Acessibility #########################

    def increase_font(self):

        if self.font_size < 30:
            self.font_size += 2  # increase size by 2
            self.global_font.config(size=self.font_size)

    def decrease_font(self):

        if self.font_size > 6:  # prevent it from becoming too small
            self.font_size -= 2
            self.global_font.config(size=self.font_size)



    def toggle_contrast(self):
        self.high_contrast = not self.high_contrast
        bg = "black" if self.high_contrast else "#CBC3E3"
        fg = "white" if self.high_contrast else "black"
        
        # Update window background
        self.Window.config(bg=bg)
        
        # Update all children widgets
        for widget in self.Window.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=bg, fg=fg)
            elif isinstance(widget, tk.Entry):
                widget.config(bg="white", fg="black")  # keep entries white background and black text


    def toggle_contrast_logged_in(self):

        # Toggle contrast state
        self.high_contrast = not getattr(self, "high_contrast", False)

        # Color scheme
        bg_color = "black" if self.high_contrast else "#CBC3E3"
        fg_color = "white" if self.high_contrast else "black"
        entry_bg = "black" if self.high_contrast else "white"
        entry_fg = "white" if self.high_contrast else "black"

        # Set main window background
        self.root.config(bg=bg_color)

        def apply_contrast(widget):
            """Apply contrast mode to widgets, skipping slider-related objects."""

            # Skip widgets that are part of sliders
            if hasattr(widget, "is_slider_related") and widget.is_slider_related:
                return

            try:
                # Normal Entry widgets (that aren't slider entries)
                if isinstance(widget, tk.Entry):
                    widget.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)

                # Skip ALL Scale widgets (sliders)
                elif isinstance(widget, tk.Scale):
                    return

                # Labels and Buttons
                elif isinstance(widget, tk.Button):
                    return #skips buttons

                # Frame or container: process children
                if hasattr(widget, "winfo_children"):
                    for child in widget.winfo_children():
                        apply_contrast(child)

            except tk.TclError:
                pass  # Some widgets don't support bg/fg; ignore them

        # Apply to all children of root
        for widget in self.root.winfo_children():
            apply_contrast(widget)


############################## Run ##############################
    def run(self):
        self.Window.mainloop()


if __name__ == "__main__":
    app = PacemakerGUI()
    app.run()
