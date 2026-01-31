import qrcode
import io

def generate_qr(text):
    """
    Generates a QR code from text or URL.
    Returns a BytesIO object containing the PNG image.
    """
    img = qrcode.make(text)
    bio = io.BytesIO()
    bio.name = "qr.png"
    img.save(bio)
    bio.seek(0)
    return bio
