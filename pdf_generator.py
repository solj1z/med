from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='PatientInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

    def generate_report(self, pdf_path, patient_info, image_paths):
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        story.append(Paragraph("ULTRASOUND EXAMINATION REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        patient_data = [
            ['Patient Name:', patient_info['name']],
            ['Patient ID:', patient_info['id']],
            ['Exam Title:', patient_info['exam_title']],
            ['Examination Date:', patient_info['date']]
        ]

        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(patient_table)
        story.append(Spacer(1, 0.4*inch))

        story.append(Paragraph("CAPTURED IMAGES", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        if image_paths:
            for idx, img_path in enumerate(image_paths, 1):
                if os.path.exists(img_path):
                    story.append(Paragraph(f"Image {idx}:", self.styles['PatientInfo']))
                    story.append(Spacer(1, 0.1*inch))

                    img = Image(img_path)

                    max_width = 6.5 * inch
                    max_height = 4.5 * inch

                    img_width, img_height = img.imageWidth, img.imageHeight
                    aspect = img_height / float(img_width)

                    if img_width > max_width:
                        img_width = max_width
                        img_height = img_width * aspect

                    if img_height > max_height:
                        img_height = max_height
                        img_width = img_height / aspect

                    img.drawWidth = img_width
                    img.drawHeight = img_height

                    story.append(img)
                    story.append(Spacer(1, 0.3*inch))

                    if idx < len(image_paths):
                        story.append(PageBreak())
        else:
            story.append(Paragraph("No images were captured during this session.", self.styles['PatientInfo']))
            story.append(Spacer(1, 0.3*inch))

        story.append(PageBreak())
        story.append(Paragraph("CLINICAL NOTES AND OBSERVATIONS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        notes_lines = ['' for _ in range(15)]
        for line in notes_lines:
            story.append(Spacer(1, 0.25*inch))
            story.append(Paragraph('_' * 100, self.styles['Normal']))

        story.append(Spacer(1, 0.5*inch))

        signature_data = [
            ['Physician Signature:', '_' * 40, 'Date:', '_' * 20]
        ]

        signature_table = Table(signature_data, colWidths=[1.5*inch, 2.5*inch, 0.7*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))

        story.append(signature_table)

        doc.build(story)
