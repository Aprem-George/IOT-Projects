from Crypto.Signature import pkcs1_15 

from Crypto.Hash import SHA256 

from Crypto.PublicKey import RSA 

import zipfile 

import os 

  

FIRMWARE_DIR = "../firmware_v2" 

ZIP_PATH = "../firmware_v2.zip" 

SIG_PATH = "../firmware_v2.sig" 

PRIVATE_KEY_PATH = "private_key.pem" 

PUBLIC_KEY_PATH = "../public_key.pem" 

  

def generate_keys(): 

    if not os.path.exists(PRIVATE_KEY_PATH): 

        key = RSA.generate(2048) 

        private_key = key.export_key() 

        public_key = key.publickey().export_key() 

        with open(PRIVATE_KEY_PATH, 'wb') as f: 

            f.write(private_key) 

        with open(PUBLIC_KEY_PATH, 'wb') as f: 

            f.write(public_key) 

        print("Keys generated.") 

    else: 

        print("Keys already exist.") 

  

def zip_firmware(): 

    with zipfile.ZipFile(ZIP_PATH, 'w') as zipf: 

        for root, _, files in os.walk(FIRMWARE_DIR): 

            for file in files: 

                full_path = os.path.join(root, file) 

                arcname = os.path.relpath(full_path, FIRMWARE_DIR) 

                zipf.write(full_path, arcname) 

    print("Firmware zipped.") 

  

def sign_firmware(): 

    with open(ZIP_PATH, 'rb') as f: 

        data = f.read() 

    key = RSA.import_key(open(PRIVATE_KEY_PATH).read()) 

    h = SHA256.new(data) 

    signature = pkcs1_15.new(key).sign(h) 

    with open(SIG_PATH, 'wb') as f: 

        f.write(signature) 

    print("Firmware signed.") 

  

if __name__ == "__main__": 

    generate_keys() 

    zip_firmware() 

    sign_firmware() 

    print("Firmware package ready.") 
