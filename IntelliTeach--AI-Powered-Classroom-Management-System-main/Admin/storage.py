from django.core.files.storage import FileSystemStorage
import os

class CustomFileSystemStorage(FileSystemStorage):
    def save(self, name, content, max_length=None):
        # Call the parent class' save() method
        path = super().save(name, content, max_length=max_length)
        # Set permissions to 777
        os.chmod(path, 0o777)
        return path
