!pip install qrcode

import qrcode
from IPython.display import display, Image

def generate_qr_display(data):
    """
    Generates a QR code from the provided data and displays it.
    :param data: The text or link to encode in the QR code.
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

    # Convert the image to a format suitable for display
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    image_bytes = buffer.read()

    # Display the image
    display(Image(image_bytes))
    print("QR code displayed above.")


if __name__ == "__main__":
    user_input = input("Enter the link or text to generate QR code: ")
    generate_qr_display(user_input)