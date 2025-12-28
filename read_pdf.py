from pypdf import PdfReader

reader = PdfReader("d:/University Management System/University_Management_System_DBMS_Project.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print(text)
