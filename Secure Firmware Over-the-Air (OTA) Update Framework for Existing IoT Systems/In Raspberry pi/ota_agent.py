#!/usr/bin/env python3 

import os 

import requests 

import zipfile 

from Crypto.Signature import pkcs1_15 

from Crypto.Hash import SHA256 

from Crypto.PublicKey import RSA 

import time 

import logging 

from datetime import datetime 

  

# Set up logging to write to both file and console 

logging.basicConfig( 

    level=logging.INFO,  # You can change this to DEBUG for more detailed logs 

    format="%(asctime)s - %(levelname)s - %(message)s", 

    handlers=[ 

        logging.FileHandler("/home/aprem/secure-ota/ota_agent/ota_agent.out.log"), 

        logging.StreamHandler()  # Optionally log to the console as well 

    ] 

) 

  

logging.info("OTA Agent started.") 

  

VERSION_FILE = "current_version.txt" 

VERSION_URL = "http://192.168.50.13:8000/version.json" 

  

def get_current_version(): 

    if not os.path.exists(VERSION_FILE): 

        logging.warning("Version file not found. Returning default version 'v0'.") 

        return "v0" 

    with open(VERSION_FILE, 'r') as f: 

        current_version = f.read().strip() 

        logging.info(f"Current firmware version: {current_version}") 

        return current_version 

  

def update_version_file(new_version): 

    logging.info(f"Updating version file to {new_version}") 

    with open(VERSION_FILE, 'w') as f: 

        f.write(new_version) 

  

def fetch_metadata(): 

    logging.info(f"Fetching metadata from {VERSION_URL}") 

    try: 

        response = requests.get(VERSION_URL) 

        response.raise_for_status()  # Raise an exception for HTTP errors 

        return response.json() 

    except requests.exceptions.RequestException as e: 

        logging.error(f"Error fetching metadata: {e}") 

        raise 

  

def download_file(url, destination): 

    logging.info(f"Downloading file from {url} to {destination}") 

    try: 

        r = requests.get(url) 

        r.raise_for_status() 

        with open(destination, 'wb') as f: 

            f.write(r.content) 

        logging.info(f"File downloaded: {destination}") 

    except requests.exceptions.RequestException as e: 

        logging.error(f"Error downloading file from {url}: {e}") 

        raise 

  

def verify_signature(firmware_zip, signature_file, public_key_file): 

    logging.info(f"Verifying signature for {firmware_zip} using {signature_file} and {public_key_file}") 

    try: 

        with open(firmware_zip, 'rb') as f: 

            data = f.read() 

        with open(signature_file, 'rb') as f: 

            signature = f.read() 

        with open(public_key_file, 'rb') as f: 

            public_key = RSA.import_key(f.read()) 

  

        h = SHA256.new(data) 

        pkcs1_15.new(public_key).verify(h, signature) 

        logging.info("Signature verified. Firmware is trusted.") 

        return True 

    except (ValueError, TypeError) as e: 

        logging.error(f"Signature verification failed: {e}") 

        return False 

  

def apply_update(zip_path): 

    logging.info(f"Applying firmware update from {zip_path}") 

    try: 

        with zipfile.ZipFile(zip_path, 'r') as zip_ref: 

            zip_ref.extractall("firmware/") 

        logging.info("Firmware applied successfully.") 

        os.system("python3 firmware/firmware_app.py") 

    except Exception as e: 

        logging.error(f"Error applying firmware update: {e}") 

        raise 

  

def run_ota(): 

    metadata = fetch_metadata() 

    current_version = get_current_version() 

  

    if metadata["version"] == current_version: 

        logging.info(f"Firmware is up-to-date (v{current_version}). No update needed.") 

        return 

  

    logging.info(f"New firmware available: {metadata['version']} (Current: {current_version})") 

    firmware_zip = "firmware_update.zip" 

    sig_file = "firmware_update.sig" 

    pub_key = os.path.join(os.path.dirname(__file__), "public_key.pem") 

  

    try: 

        download_file(f"http://192.168.50.13:8000/{metadata['firmware']}", firmware_zip) 

        download_file(f"http://192.168.50.13:8000/{metadata['signature']}", sig_file) 

  

        if verify_signature(firmware_zip, sig_file, pub_key): 

            apply_update(firmware_zip) 

            update_version_file(metadata["version"]) 

        else: 

            logging.error("Update rejected due to invalid signature.") 

    except Exception as e: 

        logging.error(f"Error during OTA update: {e}") 

  

if __name__ == "__main__": 

    TEST_MODE = True  # Set to False for actual 4-hour schedule 

    interval = 30 if TEST_MODE else 4 * 60 * 60  # 20 seconds or 4 hours for production 

  

    logging.info("Starting OTA Agent...") 

  

    while True: 

        try: 

            logging.info("Checking for firmware update...") 

            run_ota() 

        except Exception as e: 

        logging.error(f"Error during OTA update: {e}") 

  

if __name__ == "__main__": 

    TEST_MODE = True  # Set to False for actual 4-hour schedule 

    interval = 30 if TEST_MODE else 4 * 60 * 60  # 20 seconds or 4 hours for production 

  

    logging.info("Starting OTA Agent...") 

  

    while True: 

        try: 

            logging.info("Checking for firmware update...") 

            run_ota() 

        except Exception as e: 

            logging.error(f"Error during OTA update check: {e}") 

        time.sleep(interval) 
