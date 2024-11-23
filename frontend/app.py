import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests

API_URL = "http://127.0.0.1:5002"  # Dirección local del backend


class CryptographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cifrado de Mensajes con Matrices")
        self.root.geometry("700x600")

        self.public_key = None
        self.private_key = None
        self.message = ""
        self.encrypted_message = None

        # Título
        tk.Label(root, text="Cifrado de Mensajes con Matrices", font=("Arial", 18, "bold")).pack(pady=10)

        # Entrada de mensaje
        tk.Label(root, text="Ingrese el Mensaje a Cifrar o Descifrar:", font=("Arial", 12)).pack(pady=5)
        self.message_input = scrolledtext.ScrolledText(root, height=4, width=80, font=("Arial", 12))
        self.message_input.pack(pady=5)        

        # Claves
        tk.Label(root, text="Claves Generadas:", font=("Arial", 12)).pack(pady=5)
        self.key_label = scrolledtext.ScrolledText(root, height=5, width=80, state="disabled", font=("Arial", 10))
        self.key_label.pack(pady=5)

        tk.Button(root, text="Generar Claves", command=self.generate_keys, font=("Arial", 12)).pack(pady=5)

        # Cifrar mensaje
        tk.Button(root, text="Cifrar Mensaje", command=self.encrypt_message, font=("Arial", 12), bg="lightblue").pack(pady=5)
        self.encrypted_label = scrolledtext.ScrolledText(root, height=4, width=80, state="disabled", font=("Arial", 10))
        self.encrypted_label.pack(pady=5)

        # Descifrar mensaje
        tk.Button(root, text="Descifrar Mensaje", command=self.decrypt_message, font=("Arial", 12), bg="lightgreen").pack(pady=5)
        self.decrypted_label = tk.Label(root, text="Mensaje Descifrado: Ninguno aún", font=("Arial", 12), wraplength=600)
        self.decrypted_label.pack(pady=10)

    def generate_keys(self):
        """Genera un par de claves desde el backend."""
        try:
            response = requests.get(f"{API_URL}/generate_keys?size=4")
            if response.status_code == 200:
                data = response.json()
                self.public_key = data.get('public_key')
                self.private_key = data.get('private_key')
                self.key_label.config(state="normal")
                self.key_label.delete("1.0", tk.END)
                self.key_label.insert(tk.END, f"Clave Pública: {self.public_key}\n")
                self.key_label.insert(tk.END, f"Clave Privada: {self.private_key}\n")
                self.key_label.config(state="disabled")
            else:
                raise Exception("Error al generar claves")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar las claves: {e}")

    def encrypt_message(self):
        """Cifra un mensaje usando la clave pública."""
        self.message = self.message_input.get("1.0", tk.END).strip()
        if not self.message:
            messagebox.showerror("Error", "Debe ingresar un mensaje para cifrar.")
            return
        if not self.public_key:
            messagebox.showerror("Error", "Debe generar claves primero.")
            return

        try:
            response = requests.post(f"{API_URL}/encrypt_message", json={
                'message': self.message,
                'public_key': self.public_key
            })
            if response.status_code == 200:
                self.encrypted_message = response.json().get('encrypted_message')
                self.encrypted_label.config(state="normal")
                self.encrypted_label.delete("1.0", tk.END)
                self.encrypted_label.insert(tk.END, f"Mensaje Cifrado: {self.encrypted_message}")
                self.encrypted_label.config(state="disabled")
            else:
                raise Exception("Error al cifrar el mensaje")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cifrar el mensaje: {e}")

    def decrypt_message(self):
        """Descifra un mensaje cifrado usando la clave privada."""
        if not self.encrypted_message:
            messagebox.showerror("Error", "Debe cifrar un mensaje primero.")
            return
        if not self.private_key:
            messagebox.showerror("Error", "Debe generar claves primero.")
            return

        try:
            response = requests.post(f"{API_URL}/decrypt_message", json={
                'encrypted_message': self.encrypted_message,
                'private_key': self.private_key
            })
            if response.status_code == 200:
                decrypted_message = response.json().get('decrypted_message')
                self.decrypted_label.config(text=f"Mensaje Descifrado: {decrypted_message}")
            else:
                raise Exception("Error al descifrar el mensaje")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo descifrar el mensaje: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptographyApp(root)
    root.mainloop()