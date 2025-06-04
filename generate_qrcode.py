import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def generate_qr(data, filename="qrcode.png"):
    """
    Generates a QR code from the provided data and saves it as an image file.
    :param data: The text or link to encode in the QR code.
    :param filename: The filename for the saved QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return img

def save_qr():
    data = entry.get()
    if not data.strip():
        messagebox.showwarning("Input Required", "Please enter text or a link.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        img = generate_qr(data, file_path)
        show_qr(img)
        messagebox.showinfo("Success", f"QR code saved as {file_path}")

def show_qr(img):
    img = img.resize((200, 200))
    img_tk = ImageTk.PhotoImage(img)
    qr_label.config(image=img_tk)
    qr_label.image = img_tk

root = tk.Tk()
root.title("QR Code Generator")
root.geometry("350x400")
root.resizable(False, False)

tk.Label(root, text="Enter text or link:", font=("Arial", 12)).pack(pady=10)
entry = tk.Entry(root, width=40, font=("Arial", 12))
entry.pack(pady=5)

tk.Button(root, text="Generate and Save QR Code", command=save_qr, font=("Arial", 12)).pack(pady=15)

qr_label = tk.Label(root)
qr_label.pack(pady=10)

root.mainloop()