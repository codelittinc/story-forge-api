from boxsdk import OAuth2, Client
import os
from io import BytesIO
import requests

class Box:
    def __init__(self):
      auth = OAuth2(
          client_id=os.environ.get('BOX_CLIENT_ID'),
          client_secret=os.environ.get('BOX_CLIENT_SECRET'),
          access_token=os.environ.get('BOX_ACCESS_TOKEN'),
      )
      self.client = Client(auth)

    def delete(self, box_id):
        try:
            file_item = self.client.file(file_id=box_id)
            file_item.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_or_create_folder(self, parent_folder, folder_name):
        """ Helper function to find or create a folder """
        items = parent_folder.get_items()
        for item in items:
            if item.type == 'folder' and item.name == folder_name:
                return item
        return parent_folder.create_subfolder(folder_name)

    def store(self, folder_name, filename):
        story_forge_folder = self.get_or_create_folder(self.client.folder(folder_id='0'), 'StoryForgeUploads')
    
        target_folder = self.get_or_create_folder(story_forge_folder, folder_name)
        clean_filename = self.clean_filename(filename)
    
        file_to_replace = None
        for item in target_folder.get_items():
            if item.type == 'file' and item.name == clean_filename:
                file_to_replace = item
                break
    
        file_info = None
        if file_to_replace:
            file_info = file_to_replace.update_contents(clean_filename)
        else:
            with open(filename, 'rb') as file:
                file_info = target_folder.upload_stream(file, clean_filename)
    
        public_url = file_info.get_shared_link_download_url()
    
        _, file_extension = os.path.splitext(clean_filename)
        file_extension = file_extension.lstrip('.')  # Remove the leading dot

        return {
            "original_filename": filename,
            "stored_filename": clean_filename,
            "public_url": public_url,
            "file_extension": file_extension,
            "box_id": file_info.id
        }

    def retrieve(self, file_id):
        try:
            file_item = self.client.file(file_id=file_id).get()
            file_info = {
                "url": file_item.get_shared_link_download_url(),
                "name": file_item.name,
            }
            return file_info
        except Exception as e:
            print(f"Error retrieving file: {e}")
            return None


    def clean_filename(self, filename):
      filename = filename.strip()
      filename = "".join(char for char in filename if char.isprintable() and ord(char) < 0x10000)
      filename = filename.replace("/", "_").replace("\\", "_")
      if filename in [".", ".."]:
          filename = "InvalidFilename"

      return filename
    
    def get_text_representation(self, file_id):
      rep_hints = '[extracted_text]'
      file = self.client.file(file_id).get()
      file_representation = file.get_representation_info(rep_hints)[0]
    
      if file_representation["status"]["state"] != "success":
          return None
  
      url_template = file_representation["content"]["url_template"]
      url = url_template.replace("{+asset_path}", "")
      access_token = self.client.auth.access_token
  
      content = self.do_request(url, access_token)
      return content.decode("utf-8")
  

    def do_request(self, url: str, access_token: str):
        resp = requests.get(
            url, 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        resp.raise_for_status()
        return resp.content

