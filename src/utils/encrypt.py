from cryptography.fernet import Fernet

clave = Fernet.generate_key()
cipher_suite = Fernet(clave)

def encrypt_information(information):
    encrypted_data = information.encode()
    encrypted_data_sensibility = cipher_suite.encrypt(encrypted_data)
    return encrypted_data_sensibility

def decrypt_information(information_decrypt):
    decrypted_data = cipher_suite.decrypt(information_decrypt)
    return decrypted_data.decode()
