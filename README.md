📄 Automated PDF Merger & Organizer

A collaborative group project that provides a simple yet powerful web-based tool to upload, merge, rename, organize, update, and delete PDF files — all from one user-friendly interface. Built with Python (Flask), it automates tedious PDF management tasks and is ideal for students, professionals, and anyone dealing with large volumes of documents.

🚀 Features

📤 Upload PDFs – Add single or multiple files quickly.

🔗 Merge PDFs – Combine multiple PDF files into one.

✏ Rename PDFs – Rename files easily from the dashboard.

🗂 Organize PDFs – Automatically sort PDFs into folders based on name, category, or date.

🛠 Update PDFs – Replace or update existing files.

🗑 Delete PDFs – Remove unwanted documents in one click.

🧠 Project Overview

Managing PDFs manually can be time-consuming. This project solves that problem by automating the workflow — from uploading and organizing to merging and deleting — all through a web interface. It’s perfect for managing notes, invoices, research papers, reports, and more.

🛠 Tech Stack

Backend: Python, Flask

Frontend: HTML, CSS

Libraries:

pypdf – PDF merging and manipulation

pdfminer – Text extraction

Werkzeug – Secure file handling

Others: File handling, directory automation

📁 Project Structure
pdf_organizer/
│
├── static/               # CSS and frontend assets
├── templates/            # HTML templates for Flask
├── uploads/              # Uploaded PDFs
├── organized/            # Organized and merged PDFs
├── app.py                # Main Flask application
├── config.py             # Configuration settings
└── README.md             # Project documentation

⚙ Installation & Setup

Follow these steps to run the project locally:

1. Clone the repository
git clone https://github.com/Venugopalchilukuri/pdf_organizer.git
cd pdf_organizer

2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate       # On Windows
source venv/bin/activate   # On macOS/Linux

3. Install dependencies
pip install -r requirements.txt

4. Run the Flask application
python app.py


Then open http://127.0.0.1:5000/ in your browser.

📚 Usage

Launch the web app.

Upload one or more PDF files.

Choose actions like Merge, Rename, Organize, or Delete.

Download or manage processed files from the dashboard.

👥 Team Members

This project was developed collaboratively by:

🧑‍💻 K Sudeep Gouda     3BR23CA046

👩‍💻 B Sai Dikshitha    3BR23CA020

🧑‍💻 C Mohammad Athiq   3BR23CA022

👩‍💻 Chilukuri Venugopal 3BR23CA026

👩‍💻 Anil Kumar T R      3BR23CA007



📜 License

This project is licensed under the MIT License – feel free to use and modify it.
