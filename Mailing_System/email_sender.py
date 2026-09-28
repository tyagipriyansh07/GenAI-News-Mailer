import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class EmailSender:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, subject, content, attachment_path=None):
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html'))
        
        if attachment_path:
            part = MIMEBase('application', 'octet-stream')
            with open(attachment_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attachment_path}"')
            msg.attach(part)

        self.send_message(msg, recipient_email)

    # def send_thank_you_email(self, recipient_email, article_title, feedback_type):
    #     # Craft the thank-you email content
    #     subject = "Thank You for Your Feedback!"
    #     body = f"""
    #     <html>
    #     <body>
    #         <p>Thank you for your feedback on the article: <strong>{article_title}</strong>.</p>
    #         <p>You gave it a <strong>{'thumbs up' if feedback_type == 'up' else 'thumbs down'}</strong>.</p>
    #         <p>We appreciate your input and will use it to improve future updates.</p>
    #     </body>
    #     </html>
    #     """
    #     self.send_email(recipient_email, subject, body)

    def send_message(self, msg, recipient_email):
        try:
            # Setting up the SMTP server
            print(f"Sending email to {recipient_email}...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
