import os


current_dir = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_FOLDER_PATH = os.path.join(current_dir, "../data/uploads")
UPLOAD_FOLDER_PATH = os.getenv("UPLOAD_FOLDER_PATH", os.path.join(current_dir, "../data/uploads"))
METADATA_FILE_PATH = os.path.join(current_dir, "../data/metadata.csv")


# if not os.path.exists(UPLOAD_FOLDER_PATH):
#     os.makedirs(UPLOAD_FOLDER_PATH)