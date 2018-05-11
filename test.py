#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import httplib2
import os, sys, io, re, datetime
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload
"""
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
"""
VER = "V0.1"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ed3googledrive'
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
    'application/vnd.google-apps.spreadsheet':
    ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
     '.xlsx']
}
"""
,
    'application/vnd.ms-excel':
    ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls']
"""

def getIdFromUrl(url):
    result = re.search(r'[-\w]{25,}', url)
    if result == None:
        return result
    else:
        return result.group(0)

def get_credentials(f):
    #home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.credentials')
    credential_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    #credential_dir = os.path.dirname(sys.argv[0])
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    try:
        credentials = None
        store = Storage(credential_path)
        credentials = store.get()
    except:
        pass
    
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # https://stackoverflow.com/questions/7783308/os-path-dirname-file-returns-empty/15598983
        flags = tools.argparser.parse_args(args=[])
        #flags = None
        credentials = tools.run_flow(flow, store, flags)
        AddDateTime("Info: Права доступа сохранены в файле '" + credential_path + "'",f)
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
        #file_name = file['name']
        if not file_name.endswith(GOOGLE_MIME_TYPES[file['mimeType']][1]):
            file_name = '{}{}'.format(file['name'],GOOGLE_MIME_TYPES[file['mimeType']][1])
        
        request = service.files().export(
            fileId=file_id,
            mimeType=(GOOGLE_MIME_TYPES[file['mimeType']])[0]).execute()
        
        # important !!!
        file_name = file_name.replace('"','_')
        file_name = os.path.join(file_path, file_name)
        with io.FileIO(file_name, 'wb') as file_write:
            file_write.write(request)

    else:
        request = service.files().get_media(fileId=file_id)
        file_name = os.path.join(file_path, file_name)
        file_io = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

    
    return file_name

# Возвращает True, если ссылка на файл GoogleDrive
def IsGoogleDriveUrl(url):
    t = re.search(r'google.com', url)   # поиск в любом месте строки; re.match - поиск с начала строки
    return t != None

# Добавляет дату и время в начало сообщения и выводит его
def AddDateTime(msg,f):
    dt = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y %H:%M:%S ")
    #print(dt + msg)
    f.write(dt + msg + '\n')

"""
argv[1] - <url>	- ссылка на файл сетки. В ссылке обязательно должен присутствовать сайт
1. google
	Для google в ссылке обязательно должен присутствовать id файла
	скачивает файл независимо от того, расшарен он всем или только конкретному пользователю.
	Если расшарена папка - скачивание всех файлов в ней
	URL для скачивания это всегда ссылка на отдельный файл или возможен случай, когда "расшаривается" папка и из неё нужно выкачать все сетки ?
	Это всегда будет только один файл.
2. dropbox
3. onedrive

argv[2] - <store_dir> - каталог для сохранения скачанного файла (должен существовать).


Выходные параметры:
<ret_code>		- код завершения
0 - завершено успешно
1 - Error: Не все параметры заданы
2 - Error: Это не ссылка на GoogleDrive
3 - Error: Каталог сохранения сетки не найден
4 - Error: В ссылке не найден ID файла
5 - Error: Ошибка аутенфикации
6 - Error: Ошибка скачивания файла
"""

def main():

    fname = sys.argv[0]
    fname = os.path.splitext(fname)[0] + '.log'
    #fname = fname + '.log'
    log_file = open(fname,"w")
    ret_code = 1
    try:
        AddDateTime("Info: Старт CLoader " + VER,log_file)
        if len(sys.argv) < 3:
            msg = """Error: Не все параметры заданы.
            script.py "url" "store_dir"
            "url"       - ссылка на файл сетки
            "store_dir" - каталог для сохранения скачанного файла (должен существовать)
            """
            AddDateTime(msg,log_file)
            raise SystemExit(ret_code)

        url = sys.argv[1]
        ret_code = ret_code + 1

        if IsGoogleDriveUrl(url):
            AddDateTime("Info: Ссылка на GoogleDrive",log_file)
        else:
            AddDateTime("Error: Это не ссылка на GoogleDrive",log_file)
            raise SystemExit(ret_code)

        # каталог для сохранения скачанного файла
        ret_code = ret_code + 1
        store_dir = sys.argv[2]
        # проверка существования каталога
        if os.path.exists(store_dir):
            AddDateTime("Info: Каталог сохранения сетки '" + store_dir + "' найден",log_file)
        else:
            AddDateTime("Error: Каталог сохранения сетки '" + store_dir + "' не найден",log_file)
            raise SystemExit(ret_code)

        ret_code = ret_code + 1
        file_id = getIdFromUrl(url)
        if file_id == None:
            AddDateTime("Error: В ссылке не найден ID файла")
            raise SystemExit(ret_code)

        AddDateTime("Info: ID файла = '" + file_id +"'",log_file)
        ret_code = ret_code + 1

        credentials = get_credentials(log_file)
        AddDateTime("Info: Права найдены",log_file)
        ret_code = ret_code + 1
        http = credentials.authorize(httplib2.Http())

        ret_code = ret_code + 1
        # Creates a Google Drive API service object and outputs the names and IDs
        service = discovery.build('drive', 'v3', http=http)

        #file_id = '0B08GXBJaNroVWDRKRWdUT0t3Ujg'    # ЛИАНА № 1 В Мелитополе.xls
        #file_id = '1CD3Zbvqgmaz4jRygtmcMMFhms59EeB6UogdoJe1TvaY'   # сетка bord.ck.ua.xlsx
        #https://drive.google.com/open?id=1b3O5j35Fr6GFRlZluE6Tzvm12F317jVv7C_Nf5LEA6k
        # sys.argv[0] - full_name of this script

        #store_dir = os.path.dirname(sys.argv[0]) #+ os.path.sep

        ret_code = ret_code + 1
        file_name = download_file(store_dir, file_id, service)
        AddDateTime("Info: Файл '" + file_name + "' успешно скачан",log_file)
    except Exception as ex:
        AddDateTime("Error: {0}".format(ex),log_file)
        raise SystemExit(ret_code)
    finally:
        AddDateTime("Info: Стоп CLoader",log_file)
        log_file.close()

if __name__ == '__main__':
    main()
