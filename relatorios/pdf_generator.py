"""
Sistema de geração de PDFs para relatórios.
Suporta templates customizáveis e diferentes tipos de relatórios.
"""

from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
from datetime import datetime


class PDFGenerator:
    """Gerador de PDFs com templates customizáveis."""
    
    def __init__(self, title="Relatório", subtitle="", author="Sistema ARES"):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.font_config = FontConfiguration()
        
    def generate_pdf(self, template_name, context, output_path=None):
        """
        Gera PDF a partir de um template HTML.
        
        Args:
            template_name: Nome do template HTML
            context: Contexto para o template
            output_path: Caminho para salvar o PDF (opcional)
            
        Returns:
            bytes: Conteúdo do PDF em bytes
        """
        # Adicionar informações padrão ao contexto
        context.update({
            'report_title': self.title,
            'report_subtitle': self.subtitle,
            'report_author': self.author,
            'generated_at': datetime.now(),
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
        })
        
        # Renderizar HTML
        html_string = render_to_string(template_name, context)
        
        # Criar PDF
        html = HTML(string=html_string, base_url=settings.BASE_DIR)
        
        # CSS customizado para PDF
        css = CSS(string=self._get_pdf_styles(), font_config=self.font_config)
        
        # Gerar PDF
        pdf_bytes = html.write_pdf(stylesheets=[css], font_config=self.font_config)
        
        # Salvar em arquivo se especificado
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _get_pdf_styles(self):
        """Retorna CSS customizado para PDF."""
        return """
        @page {
            size: A4;
            margin: 2cm 1.5cm;
            
            @top-left {
                content: string(report-title);
                font-size: 10pt;
                color: #666;
            }
            
            @top-right {
                content: string(report-date);
                font-size: 10pt;
                color: #666;
            }
            
            @bottom-center {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 9pt;
                color: #999;
            }
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #333;
        }
        
        h1 {
            string-set: report-title content();
            font-size: 24pt;
            color: #c62828;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }
        
        h2 {
            font-size: 18pt;
            color: #c62828;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }
        
        h3 {
            font-size: 14pt;
            color: #333;
            margin-top: 0.5cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1cm;
            font-size: 9pt;
        }
        
        table thead {
            background-color: #f5f5f5;
            border-bottom: 2px solid #c62828;
        }
        
        table th {
            padding: 8px;
            text-align: left;
            font-weight: bold;
            color: #333;
        }
        
        table td {
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        table tr:hover {
            background-color: #fafafa;
        }
        
        .text-primary {
            color: #c62828;
        }
        
        .text-success {
            color: #2e7d32;
        }
        
        .text-danger {
            color: #d32f2f;
        }
        
        .text-warning {
            color: #f57c00;
        }
        
        .text-muted {
            color: #999;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: bold;
        }
        
        .badge-success {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        .badge-warning {
            background-color: #fff3e0;
            color: #f57c00;
        }
        
        .badge-danger {
            background-color: #ffebee;
            color: #d32f2f;
        }
        
        .stats-box {
            background-color: #f5f5f5;
            padding: 1cm;
            border-radius: 5px;
            margin-bottom: 1cm;
        }
        
        .report-header {
            border-bottom: 3px solid #c62828;
            padding-bottom: 0.5cm;
            margin-bottom: 1cm;
        }
        
        .report-footer {
            border-top: 1px solid #e0e0e0;
            padding-top: 0.5cm;
            margin-top: 1cm;
            font-size: 8pt;
            color: #999;
        }
        
        .page-break {
            page-break-after: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        """


class ReportExporter:
    """Exportador de relatórios em múltiplos formatos."""
    
    @staticmethod
    def export_to_excel(data, filename, sheet_name="Relatório"):
        """
        Exporta dados para Excel.
        
        Args:
            data: Lista de dicionários ou DataFrame
            filename: Nome do arquivo
            sheet_name: Nome da planilha
            
        Returns:
            str: Caminho do arquivo gerado
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            
            if not data:
                return None
            
            # Cabeçalhos
            headers = list(data[0].keys())
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="C62828", end_color="C62828", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
            
            # Dados
            for row, item in enumerate(data, 2):
                for col, header in enumerate(headers, 1):
                    ws.cell(row=row, column=col, value=item.get(header, ''))
            
            # Ajustar largura das colunas
            for column in ws.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column[0].column_letter].width = adjusted_width
            
            # Salvar
            output_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            wb.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Erro ao exportar para Excel: {e}")
            return None
    
    @staticmethod
    def export_to_csv(data, filename):
        """
        Exporta dados para CSV.
        
        Args:
            data: Lista de dicionários
            filename: Nome do arquivo
            
        Returns:
            str: Caminho do arquivo gerado
        """
        import csv
        
        if not data:
            return None
        
        output_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return output_path
