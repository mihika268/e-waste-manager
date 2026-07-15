"""
Certificate of Recycling Generation

This module handles PDF certificate generation for recycled items.
Certificates serve as proof of proper e-waste disposal.

Author: Muskan Uttam
Created: 2025
"""

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
import os

class CertificateGenerator:
    """Generate PDF certificates for recycling"""
    
    @staticmethod
    def generate_certificate(user, item, file_path=None):
        """Generate a PDF certificate for recycling"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#28a745'),
            alignment=1,
            spaceAfter=30
        )
        
        story.append(Paragraph("🌱 E-Waste Management System", title_style))
        story.append(Paragraph("Certificate of Recycling", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        cert_number = f"#{datetime.now().strftime('%Y%m%d%H%M%S')}"
        story.append(Paragraph(f"<b>Certificate No:</b> {cert_number}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        cert_text = f"""
        This certifies that <b>{user.first_name} {user.last_name}</b> has properly 
        disposed of the following electronic waste item through our certified recycling program.
        """
        story.append(Paragraph(cert_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        item_data = [
            ['Item Name:', item.name],
            ['Brand:', item.brand or 'N/A'],
            ['Model:', item.model or 'N/A'],
            ['Serial Number:', item.serial_number or 'N/A'],
            ['Category:', item.category.name if item.category else 'N/A'],
            ['Weight:', f"{item.weight} kg" if item.weight else 'N/A'],
            ['Collection Date:', item.created_at.strftime('%Y-%m-%d') if item.created_at else 'N/A']
        ]
        
        item_table = Table(item_data, colWidths=[2*inch, 4*inch])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(item_table)
        story.append(Spacer(1, 0.3*inch))
        
        impact_text = """
        <b>Environmental Impact:</b><br/>
        By properly recycling this item, you have contributed to:
        • Reduced carbon footprint
        • Conservation of natural resources
        • Prevention of harmful materials entering landfills
        • Support for a circular economy
        """
        story.append(Paragraph(impact_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        footer_text = f"""
        This certificate is issued by E-Waste Management System on {datetime.now().strftime('%B %d, %Y')}.
        For verification, visit our website or contact support.
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content
    
    @staticmethod
    def generate_summary_certificate(user, items, year=None):
        """Generate a summary certificate for multiple items"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#28a745'),
            alignment=1,
            spaceAfter=30
        )
        
        story.append(Paragraph("🌱 E-Waste Management System", title_style))
        story.append(Paragraph("Annual Recycling Certificate", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        cert_text = f"""
        This certifies that <b>{user.first_name} {user.last_name}</b> has properly 
        disposed of <b>{len(items)} electronic waste items</b> through our certified recycling program.
        """
        story.append(Paragraph(cert_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        total_weight = sum(item.weight or 0 for item in items)
        
        summary_data = [
            ['Total Items Recycled:', str(len(items))],
            ['Total Weight:', f"{total_weight} kg"],
            ['Certificate Issued:', datetime.now().strftime('%Y-%m-%d')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        impact_text = f"""
        <b>Environmental Impact Summary:</b><br/>
        Through recycling {len(items)} items:
        • Estimated CO₂ reduction: {len(items) * 15} kg
        • Energy saved: {len(items) * 37.5} kWh
        • Materials recovered: {len(items) * 3} kg
        """
        story.append(Paragraph(impact_text, styles['Normal']))
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content

