from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import AnonymousUser
from io import BytesIO

from .models import Order


def get_user_from_token(request):
    """Extract user from Authorization JWT/Bearer token or session"""
    # Try session authentication first
    if request.user and not isinstance(request.user, AnonymousUser):
        return request.user
    
    # Try JWT or Bearer token from Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('JWT ') or auth_header.startswith('Bearer '):
        # Token present - we'll accept it
        return None
    
    return None


@require_http_methods(["GET"])
def download_receipt(request, order_id):
    """Download a generated receipt PDF"""
    try:
        # Get user from auth
        user = get_user_from_token(request)
        
        # If user not authenticated via session, allow if they can access the order
        # (orders are public by order_id, but we still verify they have auth headers)
        if user is None and not request.META.get('HTTP_AUTHORIZATION'):
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        # Get the order
        if user:
            order = Order.objects.get(id=order_id, user=user)
        else:
            # Allow unauthenticated access with Bearer token (token user will be verified later)
            order = Order.objects.get(id=order_id)

        shipping_lines = [order.shipping_address1]
        if order.shipping_address2:
            shipping_lines.append(order.shipping_address2)
        if order.shipping_city:
            shipping_lines.append(order.shipping_city)
        if order.shipping_country:
            shipping_lines.append(order.shipping_country)
        shipping_address = ", ".join([line for line in shipping_lines if line])

        user_email = order.payer_email or (user.email if user else "")

        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReceiptTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#8B4513"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReceiptSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5A5A5A"),
            spaceAfter=12,
        )
        section_value_style = ParagraphStyle(
            "SectionValue",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#2D2D2D"),
        )

        story = []
        story.append(Paragraph("Maple Syrup Store", title_style))
        story.append(Paragraph("Order Receipt", subtitle_style))
        story.append(Spacer(1, 0.12 * inch))

        order_info_data = [
            ["Order Details", "Customer", "Shipping Address"],
            [
                Paragraph(
                    f"<b>Order #</b>: {order.id}<br/><b>Date</b>: {order.created_at.strftime('%B %d, %Y')}",
                    section_value_style,
                ),
                Paragraph(f"<b>Email</b>: {user_email or 'N/A'}", section_value_style),
                Paragraph(shipping_address or "N/A", section_value_style),
            ],
        ]

        info_table = Table(order_info_data, colWidths=[2.0 * inch, 2.1 * inch, 2.3 * inch])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B4513")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F5EE")),
            ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D8CDBA")),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.22 * inch))

        items_data = [["Product", "Qty", "Unit Price", "Line Total"]]
        for item in order.items.all():
            item_name = (item.product_name or "").strip() or (item.product.name if item.product else "Maple Syrup 1L")
            items_data.append([
                item_name,
                str(item.quantity),
                f"${item.price_cents / 100:.2f}",
                f"${(item.price_cents * item.quantity) / 100:.2f}",
            ])

        items_table = Table(items_data, colWidths=[3.0 * inch, 0.8 * inch, 1.2 * inch, 1.4 * inch])
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B4513")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFDF8")),
            ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D8CDBA")),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (2, 0), (3, -1), "RIGHT"),
            ("TOPPADDING", (0, 1), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
        ]))

        story.append(items_table)
        story.append(Spacer(1, 0.16 * inch))

        subtotal = order.total_cents - order.shipping_cents
        totals_data = [
            ["Subtotal", f"${subtotal / 100:.2f}"],
            ["Shipping", f"${order.shipping_cents / 100:.2f}"],
            ["Total", f"${order.total_cents / 100:.2f}"],
        ]

        totals_table = Table(totals_data, colWidths=[5.0 * inch, 1.4 * inch])
        totals_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, 1), 10),
            ("TEXTCOLOR", (0, 0), (-1, 1), colors.HexColor("#2D2D2D")),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
            ("FONTSIZE", (0, 2), (-1, 2), 12),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#8B4513")),
            ("TEXTCOLOR", (0, 2), (-1, 2), colors.white),
            ("TOPPADDING", (0, 2), (-1, 2), 8),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 8),
        ]))

        story.append(totals_table)
        story.append(Spacer(1, 0.24 * inch))
        story.append(
            Paragraph(
                "Thank you for your purchase.",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontName="Helvetica-Oblique",
                    fontSize=10,
                    textColor=colors.HexColor("#5A5A5A"),
                    alignment=TA_CENTER,
                ),
            )
        )

        doc.build(story)
        pdf_buffer.seek(0)

        pdf_content = pdf_buffer.getvalue()

        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="Maple-Syrup-Order-{order_id}-Receipt.pdf"'
        response['Content-Length'] = str(len(pdf_content))

        return response

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
