import re
import subprocess
import random
import argparse
import sys
import signal

def banner():
    print("""
    ######################################################
    #            MAC Address Changer Tool                #
    #         Created by Abhinav VK                      #
    #   Use for ethical and educational purposes only    #
    ######################################################
    """)

def get_interfaces():
    output = subprocess.check_output(["ifconfig"]).decode()
    interfaces = re.findall(r"(\w+): flags", output)
    return interfaces

def get_current_mac(interface):
    try:
        output = subprocess.check_output(["ifconfig", interface]).decode()
        mac_address = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", output)
        return mac_address.group(0) if mac_address else None
    except subprocess.CalledProcessError:
        print("\033[91m[ERROR] Failed to get MAC address. Check your interface.\033[0m")
        sys.exit(1)

def change_mac(interface, new_mac):
    try:
        subprocess.call(["sudo", "ifconfig", interface, "down"])
        subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
        subprocess.call(["sudo", "ifconfig", interface, "up"])
        print(f"\033[92m[SUCCESS] MAC address changed to {new_mac}\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Failed to change MAC: {e}\033[0m")
        sys.exit(1)

def generate_random_mac():
    return ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])

def restore_original_mac(interface, original_mac):
    change_mac(interface, original_mac)
    print("\033[94m[INFO] MAC address restored to original.\033[0m")

def exit_handler(signal, frame):
    if original_mac:
        restore_original_mac(interface, original_mac)
    print("\033[93m[INFO] Exiting and restoring MAC address.\033[0m")
    sys.exit(0)

def main():
    global interface, original_mac
    banner()
    
    interfaces = get_interfaces()
    print("\nAvailable Network Interfaces:")
    for i, iface in enumerate(interfaces, 1):
        print(f"{i}. {iface}")
    
    choice = int(input("\nSelect an interface: "))
    interface = interfaces[choice - 1]
    
    original_mac = get_current_mac(interface)
    print(f"\033[91m\n[DANGER] Current MAC Address: {original_mac}\033[0m")
    
    print("\n1. Generate Random MAC")
    print("2. Enter Custom MAC")
    choice = int(input("\nSelect an option: "))
    
    print("\033[91m\n[DANGER] Use this tool only for ethical and educational purposes! Creator is not responsible for illegal actions.\033[0m")
    consent = input("\n[Y/N]: ").strip().lower()
    if consent != 'y':
        print("\033[91m[INFO] Exiting tool.\033[0m")
        sys.exit(0)
    
    if choice == 1:
        new_mac = generate_random_mac()
    else:
        new_mac = input("Enter new MAC address: ")
    
    change_mac(interface, new_mac)
    print(f"\033[91m[INFO] Original MAC: {original_mac}\033[0m")
    print(f"\033[92m[INFO] Spoofed MAC: {new_mac}\033[0m")
    
    restore_choice = input("\nDo you want to restore the original MAC? (Y/N): ").strip().lower()
    if restore_choice == 'y':
        restore_original_mac(interface, original_mac)
    
    signal.signal(signal.SIGINT, exit_handler)
    
if __name__ == "__main__":
    main()
