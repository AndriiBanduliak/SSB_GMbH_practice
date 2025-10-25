"""
Report generation service for PDF reports
"""
from typing import Dict, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports for clients"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_client_report(
        self,
        client_data: Dict,
        pnl_data: Dict,
        transactions: List[Dict],
        period: str
    ) -> BytesIO:
        """
        Generate comprehensive client performance report
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(f"Performance Report - {client_data['full_name']}", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Period and date
            date_text = f"Period: {period}<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            story.append(Paragraph(date_text, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Client Information
            story.append(Paragraph("Client Information", self.styles['CustomHeading']))
            client_info = [
                ['Email:', client_data['email']],
                ['Risk Level:', client_data.get('risk_level', 'N/A')],
                ['Trading Strategy:', client_data.get('trading_strategy', 'N/A')],
                ['Current AUM:', f"${client_data.get('current_aum', 0):,.2f}"]
            ]
            client_table = Table(client_info, colWidths=[2*inch, 4*inch])
            client_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(client_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Performance Summary
            story.append(Paragraph("Performance Summary", self.styles['CustomHeading']))
            
            # Determine color based on P&L
            pnl_color = colors.green if pnl_data['total_pnl'] >= 0 else colors.red
            
            performance_data = [
                ['Metric', 'Value'],
                ['Starting Balance', f"${pnl_data['starting_balance']:,.2f}"],
                ['Ending Balance', f"${pnl_data['ending_balance']:,.2f}"],
                ['Total P&L', f"${pnl_data['total_pnl']:,.2f}"],
                ['ROI', f"{pnl_data['roi_percentage']:.2f}%"],
                ['Total Fees', f"${pnl_data['total_fees']:,.2f}"],
                ['Max Drawdown', f"${pnl_data['max_drawdown']:,.2f} ({pnl_data['max_drawdown_percentage']:.2f}%)"],
            ]
            
            performance_table = Table(performance_data, colWidths=[3*inch, 3*inch])
            performance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('TEXTCOLOR', (1, 3), (1, 3), pnl_color),  # P&L color
                ('FONT', (0, 3), (1, 3), 'Helvetica-Bold', 11),  # P&L bold
            ]))
            story.append(performance_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Trade Statistics
            story.append(Paragraph("Trade Statistics", self.styles['CustomHeading']))
            trade_stats = [
                ['Metric', 'Value'],
                ['Total Trades', str(pnl_data['total_trades'])],
                ['Winning Trades', str(pnl_data['winning_trades'])],
                ['Losing Trades', str(pnl_data['losing_trades'])],
                ['Win Rate', f"{pnl_data['win_rate']:.2f}%"],
            ]
            
            trade_table = Table(trade_stats, colWidths=[3*inch, 3*inch])
            trade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(trade_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Recent Transactions
            if transactions:
                story.append(Paragraph("Recent Transactions", self.styles['CustomHeading']))
                
                tx_data = [['Date', 'Symbol', 'Side', 'Quantity', 'Price', 'Total']]
                for tx in transactions[:10]:  # Show last 10 transactions
                    tx_data.append([
                        tx['executed_at'].strftime('%Y-%m-%d'),
                        tx['symbol'],
                        tx['side'].upper(),
                        f"{tx['quantity']:.4f}",
                        f"${tx['price']:.2f}",
                        f"${tx['total_amount']:.2f}"
                    ])
                
                tx_table = Table(tx_data, colWidths=[1*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
                tx_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                story.append(tx_table)
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            footer_text = "This report is confidential and intended solely for the addressee. Past performance does not guarantee future results."
            story.append(Paragraph(footer_text, self.styles['Italic']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise
    
    def generate_summary_report(self, clients_data: List[Dict], period: str) -> BytesIO:
        """
        Generate summary report for multiple clients
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(f"Portfolio Summary Report", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Period
            date_text = f"Period: {period}<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            story.append(Paragraph(date_text, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Summary table
            story.append(Paragraph("Clients Overview", self.styles['CustomHeading']))
            
            summary_data = [['Client', 'AUM', 'P&L', 'ROI %', 'Trades', 'Win Rate %']]
            total_aum = 0
            total_pnl = 0
            
            for client in clients_data:
                summary_data.append([
                    client['client_name'][:20],  # Truncate long names
                    f"${client['current_aum']:,.0f}",
                    f"${client['total_pnl']:,.0f}",
                    f"{client['roi_percentage']:.1f}",
                    str(client['total_trades']),
                    f"{client['win_rate']:.1f}"
                ])
                total_aum += client['current_aum']
                total_pnl += client['total_pnl']
            
            # Add totals row
            summary_data.append([
                'TOTAL',
                f"${total_aum:,.0f}",
                f"${total_pnl:,.0f}",
                '-',
                '-',
                '-'
            ])
            
            summary_table = Table(summary_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(summary_table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            logger.error(f"Failed to generate summary report: {str(e)}")
            raise

