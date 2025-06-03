import qrcode

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
    print(f"QR code saved as {filename}")

if __name__ == "__main__":
    user_input = input("Enter the link or text to generate QR code: ")
    output_file = input("Enter output filename (default: qrcode.png): ").strip() or "qrcode.png"
    generate_qr(user_input, output_file)