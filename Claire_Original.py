import json
from datetime import datetime
import subprocess

# programable paramters

# Lower_Rate_Limit
# Upper_Rate_Limit
# Atrial_Amplitude
# Atrial_Pules_Width
# Ventricular_Amplitude
# Ventricular_Pulse_Width
# VRP
# ARP

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
                   "\nDevice Model: Insert Here"+
                    "\nSerial Number: Insert Here"+
                    "\nDCM Serial Number: Insert Here"+
                    "\nApplication Model: Insert Here"+
                    "\nVersion Number: Insert Here"+
                    "\n----------------------------------"
      )
        
    return file_name
        
subprocess.Popen(["notepad.exe", export_report("Bradycardia")])
