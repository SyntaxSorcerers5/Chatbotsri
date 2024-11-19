from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_first_aid_report(interaction_details, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.drawString(30, height - 50, f"Report Time: {interaction_details.get('timestamp', 'N/A')}")
    c.drawString(30, height - 70, f"Accident Type: {interaction_details.get('accident_type', 'N/A')}")
    c.drawString(30, height - 90, "First Aid Provided:")
    text_obj = c.beginText(30, height - 110)
    text_obj.setFont("Helvetica", 10)
    text_obj.textLines(interaction_details.get("first_aid_provided", "No details available"))

    c.drawText(text_obj)
    c.showPage()
    c.save()
