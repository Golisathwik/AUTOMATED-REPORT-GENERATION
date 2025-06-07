import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from collections import defaultdict

def generate_sales_report(data_file, output_pdf):
    """
    Reads sales data from a CSV file, analyzes it, and generates a PDF report.

    Args:
        data_file (str): Path to the input CSV data file.
        output_pdf (str): Path for the generated PDF report.
    """

    # --- 1. Data Reading and Analysis ---
    sales_data = []
    try:
        with open(data_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row['Sales'] = float(row['Sales'])
                    sales_data.append(row)
                except ValueError:
                    print(f"Skipping row due to invalid 'Sales' value: {row}")
    except FileNotFoundError:
        print(f"Error: Data file '{data_file}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the data file: {e}")
        return

    if not sales_data:
        print("No valid data found to generate a report.")
        return

    # Basic Analysis
    total_sales = sum(item['Sales'] for item in sales_data)
    num_transactions = len(sales_data)
    average_sales_per_transaction = total_sales / num_transactions if num_transactions > 0 else 0

    sales_by_region = defaultdict(float)
    product_counts = defaultdict(int)

    for item in sales_data:
        sales_by_region[item['Region']] += item['Sales']
        product_counts[item['Product']] += 1

    most_popular_product = max(product_counts, key=product_counts.get) if product_counts else "N/A"
    top_region = max(sales_by_region, key=sales_by_region.get) if sales_by_region else "N/A"

    # --- 2. PDF Report Generation ---
    doc = SimpleDocTemplate(output_pdf, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()

    # Custom style for the footer
    footer_style = ParagraphStyle(
        name='FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,  # Center alignment
        textColor=colors.grey
    )

    story = []

    # Title
    title_style = styles['h1']
    title_style.alignment = 1  # Center alignment
    story.append(Paragraph("Sales Performance Report", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Introduction
    story.append(Paragraph("This report provides an overview of recent sales data.", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))

    # Summary of Analysis
    story.append(Paragraph("<u><b>Summary of Key Metrics:</b></u>", styles['h2']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"<b>Total Sales:</b> ${total_sales:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Number of Transactions:</b> {num_transactions}", styles['Normal']))
    story.append(Paragraph(f"<b>Average Sales per Transaction:</b> ${average_sales_per_transaction:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Most Popular Product:</b> {most_popular_product} (sold {product_counts.get(most_popular_product, 0)} times)", styles['Normal']))
    story.append(Paragraph(f"<b>Region with Highest Sales:</b> {top_region} (Total Sales: ${sales_by_region.get(top_region, 0):,.2f})", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Sales by Region Table
    story.append(Paragraph("<u><b>Sales by Region:</b></u>", styles['h2']))
    story.append(Spacer(1, 0.1 * inch))

    region_data = [['Region', 'Total Sales']]
    for region, sales in sorted(sales_by_region.items()):
        region_data.append([region, f"${sales:,.2f}"])

    region_table = Table(region_data, colWidths=[2 * inch, 2 * inch])
    region_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')), # Header background (Bootstrap primary blue)
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')), # Alternating row background (Bootstrap light gray)
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(region_table)
    story.append(Spacer(1, 0.2 * inch))

    # Footer
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawCentredString(letter[0] / 2.0, 0.3 * inch,
                                 f"Report Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.restoreState()

    try:
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        print(f"Report '{output_pdf}' generated successfully!")
    except Exception as e:
        print(f"An error occurred while building the PDF: {e}")

if __name__ == "__main__":
    data_file_name = 'sales_data.csv'
    output_report_name = 'Sales_Performance_Report.pdf'
    generate_sales_report(data_file_name, output_report_name)