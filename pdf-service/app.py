from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os

app = FastAPI(title="PDF Receipt Service")

# Directory to store PDFs
PDF_STORAGE_DIR = os.getenv("PDF_STORAGE_DIR", "/tmp/receipts")
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)


class OrderItem(BaseModel):
    name: str
    quantity: int
    price_cents: int


class ReceiptRequest(BaseModel):
    order_id: int
    user_email: str
    total_cents: int
    shipping_cents: int
    created_at: str
    items: list[OrderItem]
    shipping_address: str = ""
    shipping_city: str = ""
    shipping_country: str = ""


def generate_pdf_receipt(order_data: ReceiptRequest, pdf_path: str) -> None:
    """Generate PDF receipt using ReportLab"""
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    style = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=style['Heading1'], fontSize=24, textColor=colors.HexColor('#8B4513'), spaceAfter=6, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=style['Heading2'], fontSize=10, textColor=colors.HexColor('#8B4513'), spaceAfter=6, fontName='Helvetica-Bold')
    normal_style = style['Normal']
    
    # Content
    story = []
    
    # Header
    story.append(Paragraph("🍁 Maple Syrup Store", title_style))
    story.append(Paragraph("Order Receipt", style['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Order info
    order_info_data = [
        ['Order Details', 'Customer', 'Shipping Address'],
        [
            f"<b>Order #:</b> {order_data.order_id}<br/><b>Date:</b> {order_data.created_at}",
            f"<b>Email:</b><br/>{order_data.user_email}",
            f"{order_data.shipping_address}<br/>{order_data.shipping_city}<br/>{order_data.shipping_country}"
        ]
    ]
    
    info_table = Table(order_info_data, colWidths=[2*inch, 2*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B4513')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items table
    items_data = [['Product', 'Qty', 'Price', 'Total']]
    for item in order_data.items:
        items_data.append([
            item.name,
            str(item.quantity),
            f"${item.price_cents/100:.2f}",
            f"${(item.price_cents * item.quantity)/100:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.2*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B4513')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals
    subtotal = order_data.total_cents - order_data.shipping_cents
    totals_data = [
        ['Subtotal:', f"${subtotal/100:.2f}"],
        ['Shipping:', f"${order_data.shipping_cents/100:.2f}"],
        ['TOTAL:', f"${order_data.total_cents/100:.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[5.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('FONTSIZE', (0, 2), (-1, 2), 12),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#8B4513')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
        ('TOPPADDING', (0, 2), (-1, 2), 8),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("Thank you for your purchase! 🙏", style['Normal']))
    
    # Build PDF
    doc.build(story)


@app.post("/generate-receipt")
async def generate_receipt(order_data: ReceiptRequest):
    """Generate a PDF receipt for an order"""
    try:
        pdf_filename = f"receipt-order-{order_data.order_id}.pdf"
        pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)

        generate_pdf_receipt(order_data, pdf_path)

        return {
            "success": True,
            "filename": pdf_filename,
            "path": pdf_path,
            "order_id": order_data.order_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating receipt: {str(e)}")


@app.get("/receipt/{order_id}")
async def get_receipt(order_id: int):
    """Get a previously generated receipt"""
    pdf_filename = f"receipt-order-{order_id}.pdf"
    pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Receipt not found")

    return {"filename": pdf_filename, "path": pdf_path}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
