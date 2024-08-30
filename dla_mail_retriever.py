import os.path
import win32com.client

class dla_mail_retrieval:
    def __init__(self,source):
        self.source = source
        self.connect()
    def connect(self):
        # Thank you, Josh Perkins!
        # Where the file is being saved
        self.path = self.source
        # Initializes an Outlook session and provides access to email-related functionalities through the MAPI namespace.
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI") 
        # Find the root folder by its name
        self.root_folder = None
        for folder in self.outlook.Folders:
            if folder.Name == "Brand Analytics Data Dump":
                self.root_folder = folder
                break
        if self.root_folder is None:
            #entry(">>> Root folder not found")
            exit()
        # Access the secondary inbox from the root folder
        self.inbox = self.root_folder.Folders.Item('Inbox')
        # Create a link to the folder where the emails will be moved
        self.downloaded = self.root_folder.Folders.Item('Downloaded')
        # Retrieves a collection of all email items within the specified folder
        self.messages = self.inbox.Items
        self.keyword_to_search = "deutsch"
        self.save_attachments(
                              keyword=self.keyword_to_search
                              ,messages=self.messages
                              ,downloaded=self.downloaded
                              ,path=self.path)
        self.info = (self.path
                , self.outlook
                , self.root_folder
                , self.inbox
                , self.downloaded
                , self.messages
                , self.keyword_to_search)
        return self.info
    # Sender Keyword
    def save_attachments(self,keyword,messages,downloaded,path):
        # Create a list of messages to move
        messages_to_move = [message for message in messages if keyword.lower() in message.SenderEmailAddress.lower()]
        for message in messages_to_move:
            attachments = message.Attachments
            for attachment in attachments: 
                if attachment.FileName.lower().endswith(('.xls', '.xlsx', '.csv')):
                    #entry("Saving attachment: {attachment.FileName}")
                    attachment.SaveAsFile(os.path.join(path, attachment.FileName))
            # Changes the email to Read
            if message.Unread:
                message.Unread = False
            # Move the message to the 'Downloaded' folder
            message.Move(downloaded)
            print(f"Moving Email: {message.Subject}")
        print("Attachments saved.")

if __name__ == '__main__':
    print ("Direct invocation")
else: 
    print ("Importation")