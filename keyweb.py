import json
import os

from flask import Flask, request, abort, send_from_directory

server = Flask(__name__)


@server.route('/getkeys', methods=['get'])
def getkeys():
    items = request.query_string.decode('utf8').split('&')
    query_dict = dict([i.split('=') for i in items])
    if query_dict.get('token') == '69557629c3856d5846137c0a5e6d1a47':
        with open('./keys.txt') as f:
            data = f.readlines()
            data[-1] += '\n'
            return json.dumps([key[:-1] for key in data])
    else:
        abort(404)


@server.route('/update', methods=['get'])
def update():
    items = request.query_string.decode('utf8').split('&')
    query_dict = dict([item.split('=') for item in items])
    if query_dict.get('token') == '69557629c3856d5846137c0a5e6d1a47':
        with open('version.txt', 'r') as f:
            version_list = json.load(f)
            if query_dict['version'] != version_list[-1]:
                if os.path.exists(os.getcwd() + '/download/windowActivate.exe'):
                    os.remove(os.getcwd() + '/download/windowActivate.exe')
                os.system(f'cp ./download/{version_list[-1]}.exe ./download/windowActivate.exe')
                return send_from_directory('./download', filename=f'windowActivate.exe'
                                           , as_attachment=True, path=os.getcwd() + '/download/windowActivate.exe')
            else:
                abort(404)
    else:
        abort(404)


@server.route('/getversion', methods=['get'])
def get_version():
    items = request.query_string.decode('utf8').split('&')
    query_dict = dict([item.split('=') for item in items])
    if query_dict.get('token') == '69557629c3856d5846137c0a5e6d1a47':
        with open('version.txt', 'r') as f:
            version_list = json.load(f)
            return json.dumps([version_list[-1]])
    else:
        abort(404)


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=6676, debug=True)
