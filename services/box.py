from boxsdk import OAuth2, Client
import os


class Box:
    def __init__(self):
      auth = OAuth2(
          client_id=os.environ.get('BOX_CLIENT_ID'),
          client_secret=os.environ.get('BOX_CLIENT_SECRET'),
          access_token=os.environ.get('BOX_ACCESS_TOKEN'),
      )
      self.client = Client(auth)
    
    def get_or_create_folder(self, parent_folder, folder_name):
        """ Helper function to find or create a folder """
        items = parent_folder.get_items()
        for item in items:
            if item.type == 'folder' and item.name == folder_name:
                return item
        return parent_folder.create_subfolder(folder_name)

    def store(self, folder_name, filename):
        story_forge_folder = self.get_or_create_folder(self.client.folder(folder_id='0'), 'StoryForgeUploads')
    
        # Find or create the specified folder inside 'StoryForgeUploads'
        target_folder = self.get_or_create_folder(story_forge_folder, folder_name)
    
        # Check if the file already exists in the folder
        file_to_replace = None
        for item in target_folder.get_items():
            if item.type == 'file' and item.name == filename:
                file_to_replace = item
                break
    
        # Upload or replace the file
        if file_to_replace:
            file_to_replace.update_contents(filename)
            print(f"File '{filename}' has been updated in folder '{folder_name}'")
        else:
            with open(filename, 'rb') as file:
                target_folder.upload_stream(file, filename)
                print(f"File '{filename}' uploaded to folder '{folder_name}'")

    def retrieve(self, folder_name, file_name):
        # Find 'StoryForgeUploads' folder
        story_forge_folder = self.get_or_create_folder(self.client.folder(folder_id='0'), 'StoryForgeUploads')
    
        # Find the specified folder within 'StoryForgeUploads'
        target_folder = self.get_or_create_folder(story_forge_folder, folder_name)
    
        # Find the specified file within the target folder
        for item in target_folder.get_items():
            if item.type == 'file' and item.name == file_name:
                file_info = {
                    "url": item.get_shared_link_download_url(),
                    "name": item.name,
                    "content": item.content().decode('utf-8')
                }
                return file_info
    
        return f"File '{file_name}' not found in folder '{folder_name}'"