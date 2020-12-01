from __future__ import print_function
import pickle
import os
import googleapiclient
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
import PIL
import tkinter
from PIL import Image, ImageTk

# Necessary for Raspberry Pi display after switching to LCD screen
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

SCOPES = ['https://www.googleapis.com/auth/drive']

# From Google Drive API docs
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)

# Call the Drive v3 API
results = service.files().list(
    pageSize=10, q="'1MmWQxjmFkXtddiQJmBfDsfZRVaHExkCb' in parents", fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

for item in items:
    file_id = item['id']
    filename = 'tmp/' + item['name']
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

files = []
for filename in os.listdir('./tmp'):
    files.append('tmp/' + filename)
files.remove('tmp/.DS_Store')

win = tkinter.Tk()
win.attributes("-fullscreen", True)
win.title("TEST")
w, h = win.winfo_screenwidth(), win.winfo_screenheight()

files = [Image.open(x).resize((w, h), Image.ANTIALIAS) for x in files]
photos = [ImageTk.PhotoImage(x) for x in files]
label = tkinter.Label()
label.photos = photos
label.counter = 0

def next_pic():
    label['image'] = label.photos[label.counter%len(label.photos)]
    label.after(2500, next_pic)
    label.counter += 1
label.pack()
next_pic()
win.mainloop()
