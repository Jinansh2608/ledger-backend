#!/usr/bin/env python3
"""
Create a sample Bajaj PO PDF for testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, date

# Create PDF
output_path = "sample_bajaj_po.pdf"
doc = SimpleDocTemplate(output_path, pagesize=letter)
story = []
styles = getSampleStyleSheet()

# Title
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#1f4e78'),
    spaceAfter=10,
    alignment=1
)

story.append(Paragraph("PURCHASE ORDER", title_style))
story.append(Spacer(1, 0.2*inch))

# PO Details
po_details_data = [
    ["PO Number:", "123456789"],
    ["Date:", date.today().strftime("%d %b %Y")],
    ["Vendor:", "SUPPLIER NAME"],
    ["Location:", "MAHARASHTRA MUMBAI"]
]

po_table = Table(po_details_data, colWidths=[1.5*inch, 3*inch])
po_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7e6e6')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
]))

story.append(po_table)
story.append(Spacer(1, 0.3*inch))

# Line Items Header
story.append(Paragraph("Line # Part # / Description", styles['Heading2']))
story.append(Spacer(1, 0.1*inch))

# Line Items
line_items_data = [
    ["Line", "Part No", "Description", "Qty", "Unit", "Rate", "Amount"],
    ["1", "P001", "Steel Plate 5mm x 1000x2000mm", "10", "PCS", "500.00", "5000.00"],
    ["2", "P002", "Aluminum Angle 40x40x5mm", "25", "KG", "150.00", "3750.00"],
    ["3", "P003", "Mild Steel Pipe D50 x 2.5mm", "15", "MTR", "200.00", "3000.00"],
]

items_table = Table(line_items_data, colWidths=[0.5*inch, 1*inch, 2.5*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.9*inch])
items_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
]))

story.append(items_table)
story.append(Spacer(1, 0.3*inch))

# Total Amount
total_data = [
    ["", "", "", "", "", "Subtotal:", "11750.00"],
    ["", "", "", "", "", "Tax Rate:", "18%"],
    ["", "", "", "", "", "Tax Amount:", "2115.00"],
    ["", "", "", "", "", "Total Amount:", "13865.00"],
]

total_table = Table(total_data, colWidths=[0.5*inch, 1*inch, 2.5*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.9*inch])
total_table.setStyle(TableStyle([
    ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
    ('FONTNAME', (5, 0), (-1, 2), 'Helvetica'),
    ('FONTNAME', (5, 3), (-1, 3), 'Helvetica-Bold'),
    ('FONTSIZE', (5, 3), (-1, 3), 11),
    ('BACKGROUND', (5, 3), (-1, 3), colors.HexColor('#d9e1f2')),
    ('GRID', (5, 0), (-1, -1), 1, colors.grey),
]))

story.append(total_table)
story.append(Spacer(1, 0.2*inch))

# Footer
footer_text = "This Purchase Order confirms our commitment to supply the above items as per specifications."
story.append(Paragraph(footer_text, styles['Normal']))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("Authorized by: Procurement Department", styles['Normal']))

# Build PDF
doc.build(story)

print(f"✅ Sample PDF created: {output_path}")
print(f"📊 File size: {__import__('os').path.getsize(output_path)} bytes")
