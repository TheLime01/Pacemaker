import json
from datetime import datetime
import subprocess

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
Modes = ["AOO","VOO", "AAI", "VVI"]
Programable_Paramters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pules Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"]
Mode_Parameters = [[True,True,True,True,False,False,False,False],
                   [True,True,False,False,True,True,False,False],
                   [True,True,True,True,False,False,False,True],
                   [True,True,False,False,True,True,True,False]]


# returns true if the username and password match a registered user, false otherwise
def login_request(username, password):
    with open("userdata.json", "r") as file:
        data = json.load(file) 

    for user in data['registered users']:
        if username.strip() == user['username'] and password.strip() == user['password']:
            return True
        
    return False

#print(login_request('testuser4','123456')), returned False
#print(login_request('testuser4','654321')), returned True


def add_new_user(username, password):
    with open("userdata.json", "r") as file:
        data = json.load(file) 

    if len(data['registered users']) > 10:
        return False, "User list at capacity."
        
    new_user = {
        "username": username.strip(),
        "password": password.strip()
    }

    if len(new_user['username']) < 6 or len(new_user['password']) < 6:
        return False, "Username and password must be at least 6 characters."
    elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
        return False, "Username and password cannot exceede 25 characters."
    
    for user in data['registered users']:
        if new_user['username'] == user['username']:
            return False, "Username already taken."

    data["registered users"].append(new_user)
    with open("userdata.json", "w") as file:
        json.dump(data, file, indent=4)
        return True, "User Added!"


#print(add_new_user("12345678901234567890123456","123456")), returned (False, 'Username and password cannot exceede 25 characters.')
#print(add_new_user("abcdef"," ")), returned (False, 'Username and password must be at least 6 characters.')
#print(add_new_user("abc","123456")), returned (False, 'Username and password must be at least 6 characters.')
#print(add_new_user("testuser6","123456")), returned (True, 'User Added!'), then (False, 'Username already taken.')


def export_report(type):
    current_datetime = datetime.now()
    file_name = type + "_Report-" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".txt"

    with open(file_name, 'w') as file:
        file.write(type+ " Parameters Report"+
                   "\nDate: " + current_datetime.strftime("%Y/%M/%D %H:%M:%S")+
                   "\nDevice Model: Pacemaker"+
                    "\nSerial Number: HOOO25"+
                    "\nDCM Serial Number: Insert Here"+
                    "\nApplication Model: Insert Here"+
                    "\nVersion Number: Insert Here"+
                    "\n----------------------------------"
      )
        
    return file_name
        
subprocess.Popen(["notepad.exe", export_report("Bradycardia")])
