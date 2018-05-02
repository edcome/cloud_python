#!/usr/bin/python3

from __future__ import print_function

import httplib2
import os, sys, io
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload
#from apiclient import MediaIoBaseDownload

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']

# Sample (reference) map of Google Docs MIME types to possible exports
# (for more information check about().get() method with exportFormats field)

#from django.http import HttpResponse
#Finally, the MIME type is wrong, it should be like this:
#response = HttpResponse(mimetype="application/vnd.ms-excel")

GOOGLE_MIME_TYPES = {
    'application/vnd.google-apps.document':
    ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
     '.docx'],
    # 'application/vnd.google-apps.document':
    # 'application/vnd.oasis.opendocument.text',
    'application/vnd.google-apps.spreadsheet':
    ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
     '.xlsx'],
    # 'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.google-apps.presentation':
    ['application/vnd.openxmlformats-officedocument.presentationml.presentation',
     '.pptx']
}
"""
,
    'application/vnd.ms-excel':
    ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls']
"""

def get_credentials():
    home_dir = os.path.expanduser('~')

    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def download_file(file_path,file_id,service):
    """ Downloads file from Google Drive.

    If file is Google Doc's type, then it will be downloaded
    with the corresponding non-Google mimetype.

    Args:
        file_path: Directory string, where file will be saved.
        file_id: ID file
        service: Google Drive service instance.
    """
    # Gets a file's metadata by ID
    file = service.files().get(fileId=file_id).execute()

    #print('MIME type: %s' % file['mimeType'])

    file_name = file['name']

    if file['mimeType'] in GOOGLE_MIME_TYPES.keys():
        file_name = file['name']
        if not file_name.endswith(GOOGLE_MIME_TYPES[file['mimeType']][1]):
            file_name = '{}{}'.format(file['name'],GOOGLE_MIME_TYPES[file['mimeType']][1])

        request = service.files().export(
            fileId=file_id,
            mimeType=(GOOGLE_MIME_TYPES[file['mimeType']])[0]).execute()

        with io.FileIO(os.path.join(file_path, file_name), 'wb') as file_write:
            file_write.write(request)

        #print(file_name)
        #print('MIME type: %s' % file['mimeType'])

    else:
        request = service.files().get_media(fileId=file_id)
        file_io = io.FileIO(os.path.join(file_path, file_name), 'wb')
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

def main():

    if len(sys.argv) != 2:
        print("Not define link to file")
        raise SystemExit(1)
    else:
        file_ref = sys.argv[1]

    print(file_ref)
    raise SystemExit(1)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    # Creates a Google Drive API service object and outputs the names and IDs
    service = discovery.build('drive', 'v3', http=http)

    file_id = '0B08GXBJaNroVWDRKRWdUT0t3Ujg'    # ЛИАНА № 1 В Мелитополе.xls
    #file_id = '1CD3Zbvqgmaz4jRygtmcMMFhms59EeB6UogdoJe1TvaY'   # сетка bord.ck.ua.xlsx

    # sys.argv[0] - full_name of this script
    store_dir = os.path.dirname(sys.argv[0]) #+ os.path.sep

    download_file(store_dir, file_id, service)
    
    """
    # Outputs the names and IDs for up to 10 files.

    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))


    # -*- coding: utf-8 -*-
    # -*- coding: cp1251 -*-
    """

if __name__ == '__main__':
    main()
