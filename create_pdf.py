from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'John Doe - Software Engineer')
pdf.ln()
pdf.cell(40, 10, 'Experience: 5 years Python, FastAPI, RAG pipelines.')
pdf.ln()
pdf.cell(40, 10, 'Education: B.S. in Computer Science')
pdf.output('apps/resume-analyzer/dummy_resume.pdf')
