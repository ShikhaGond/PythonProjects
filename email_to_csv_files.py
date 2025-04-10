import csv
import os
from datetime import datetime
from email.parser import Parser
from email.policy import default

class EmailCSVStorage:
    """A class to store email data in CSV format"""
    
    def __init__(self, csv_file_path="emails.csv"):
        """Initialize with path to CSV file"""
        self.csv_file_path = csv_file_path
        self.headers = ["Date", "From", "To", "Subject", "Body", "Attachments"]
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)
    
    def parse_email_file(self, email_file_path):
        """Parse an email file and return a dictionary of its data"""
        with open(email_file_path, 'r', encoding='utf-8') as file:
            email_content = file.read()
        
        # Parse the email content
        email_parser = Parser(policy=default)
        email_message = email_parser.parsestr(email_content)
        
        # Extract email data
        email_data = {
            "Date": email_message.get("Date", ""),
            "From": email_message.get("From", ""),
            "To": email_message.get("To", ""),
            "Subject": email_message.get("Subject", ""),
            "Body": self._get_email_body(email_message),
            "Attachments": self._get_attachment_names(email_message)
        }
        
        return email_data
    
    def _get_email_body(self, email_message):
        """Extract the body text from an email message"""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8', errors='replace')
        else:
            return email_message.get_payload(decode=True).decode('utf-8', errors='replace')
        
        return ""
    
    def _get_attachment_names(self, email_message):
        """Get a list of attachment filenames from an email message"""
        attachments = []
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
        
        return ", ".join(attachments)
    
    def store_email(self, email_data):
        """Store an email's data to the CSV file"""
        with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                email_data["Date"],
                email_data["From"],
                email_data["To"],
                email_data["Subject"],
                email_data["Body"],
                email_data["Attachments"]
            ])
    
    def store_email_from_file(self, email_file_path):
        """Parse and store an email from a file"""
        email_data = self.parse_email_file(email_file_path)
        self.store_email(email_data)
    
    def store_email_from_data(self, from_addr, to_addr, subject, body, attachments=""):
        """Store an email from provided data"""
        email_data = {
            "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
            "From": from_addr,
            "To": to_addr,
            "Subject": subject,
            "Body": body,
            "Attachments": attachments
        }
        self.store_email(email_data)
    
    def read_all_emails(self):
        """Read all emails from the CSV file"""
        emails = []
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                emails.append(row)
        return emails
    
    def search_emails(self, search_term):
        """Search emails with a search term"""
        matching_emails = []
        emails = self.read_all_emails()
        
        for email in emails:
            for value in email.values():
                if search_term.lower() in value.lower():
                    matching_emails.append(email)
                    break
        
        return matching_emails


# Example usage
if __name__ == "__main__":
    # Create a sample email file for testing
    sample_email = """Date: Mon, 8 Apr 2025 12:34:56
From: sender@example.com
To: recipient@example.com
Subject: Hello from Python
Content-Type: text/plain

This is a test email for our CSV storage system.
"""
    
    with open("sample_email.txt", "w") as file:
        file.write(sample_email)
    
    # Initialize the email storage
    email_storage = EmailCSVStorage()
    
    # Store email from file
    email_storage.store_email_from_file("sample_email.txt")
    
    # Store email from data
    email_storage.store_email_from_data(
        "another@example.com",
        "user@example.com",
        "Another test email",
        "This is the body of another test email.",
        "document.pdf"
    )
    
    # Read all emails
    print("All emails:")
    all_emails = email_storage.read_all_emails()
    for email in all_emails:
        print(f"From: {email['From']}, Subject: {email['Subject']}")
    
    # Search emails
    print("\nSearch results for 'test':")
    search_results = email_storage.search_emails("test")
    for email in search_results:
        print(f"From: {email['From']}, Subject: {email['Subject']}")