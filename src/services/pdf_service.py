from fpdf import FPDF
import io

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(234, 88, 12) # Orange
        self.cell(0, 10, 'Gaskiyar Kaya - Rapport Expertise', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_pdf_report(data, image_buffer):
    """Génère un rapport PDF à partir des données d'analyse."""
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # TITRE MEUBLE
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 41, 55) # Gris foncé
    pdf.cell(0, 10, f"{data.get('titre')} - {data.get('style')}", new_x="LMARGIN", new_y="NEXT")

    # VERDICT PRIX
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Verdict Prix: {data.get('verdict_prix')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # IMAGE (Si disponible)
    if image_buffer:
        try:
            # Sauvegarde temporaire en mémoire pour FPDF
            # FPDF attend un chemin ou un flux
            pdf.image(image_buffer, w=100, x=55) # Centré (A4 = 210mm)
            pdf.ln(10)
        except Exception as e:
            pdf.cell(0, 10, f"[Image non disponible: {str(e)}]", new_x="LMARGIN", new_y="NEXT")

    # SCORES
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(243, 244, 246) # Gris clair
    pdf.cell(0, 10, "PERFORMANCE TECHNIQUE", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    scores = data.get('scores', {})
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Score Global: {scores.get('global')}/100", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Solidite: {scores.get('solidite')}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Materiaux: {scores.get('materiaux')}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Restauration: {scores.get('restauration')}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # AVIS EXPERTS
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "AVIS EXPERTS", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "Menuisier:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, data.get('avis_menuisier', ''))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "Tapissier:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, data.get('avis_tapissier', ''))
    pdf.ln(5)

    # CONSEIL FINAL
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(4, 120, 87) # Vert
    pdf.cell(0, 10, "CONSEIL DU GWANI", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, data.get('recommandation_finale', ''), border=1)

    # Output to buffer
    return pdf.output()
