from unittest.mock import MagicMock
from src.services.pdf_service import generate_pdf_report
import io

def test_generate_pdf_report_success():
    # Setup mock data
    data = {
        "titre": "Table Test",
        "style": "Moderne",
        "verdict_prix": "Correct",
        "scores": {
            "global": 80,
            "solidite": 90,
            "materiaux": 70,
            "restauration": 85
        },
        "avis_menuisier": "Bon état.",
        "avis_tapissier": "RAS.",
        "recommandation_finale": "Acheter."
    }

    # Mock image (empty BytesIO acts as file-like object)
    # Note: FPDF2 image processing might fail if not valid image data.
    # We pass None to skip image rendering logic if possible, or mock properly.
    # Looking at code: `if image_buffer: pdf.image(...)`.
    # Let's pass None first to test text logic.

    pdf_bytes = generate_pdf_report(data, None)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert b"%PDF" in pdf_bytes # Header check
