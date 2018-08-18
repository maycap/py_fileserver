# coding: utf-8
import os

from flask import jsonify, request, Flask, send_from_directory, url_for
from flask_restful import Resource, Api, abort
from werkzeug.utils import secure_filename, redirect

from models import FileManager
from app.helper import lock_access, get_config, check_manage, check_remote, get_md5
from app.helper import get_logger

logger = get_logger()


app = Flask(__name__)
APP_API = Api(app)

Myconfig = get_config()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Myconfig.ALLOWED_EXTENSIONS

class OK(Resource):

    def get(self):
        return 'ok'


class TokenApi(Resource):

    @check_manage
    def get(self):
        user = request.args.get('user')
        dst_ip = request.args.get('dst_ip')
        if not user:
            abort(400, message=u'params user is required!')
        if not dst_ip:
            abort(400, message=u'params dst_ip is required!')
        fm = FileManager()
        logger.info(u'用户：{} 申请远程ip: {} 的上传token'.format(user, dst_ip))
        return fm.create(user, dst_ip)

    @check_manage
    def put(self):
        data = request.json
        file_token = data.get('file_token', None)
        if not file_token:
            abort(400, message=u'params file_token is required!')
        download_counter = data.get('download_counter', None)
        if not download_counter or not isinstance(download_counter, int):
            abort(400, message=u'params download_counter is required!')
        fm = FileManager()
        ret, result = fm.update_counter(file_token, download_counter)
        logger.info(u'文件：{} 下载计数器更新为: {}'.format(file_token, download_counter))
        return jsonify(status=ret, message=result)


class ClientApi(Resource):

    @lock_access
    def get(self, file_token, filename):
        logger.info(u'文件: {} token:{} 将被远程ip: {} 下载'.format(filename, file_token, request.remote_addr))
        return send_from_directory(Myconfig.UPLOAD_FOLDER, file_token)


class FileApi(Resource):

    def get(self, file_token):
        fm = FileManager()
        filename = fm.get_download(file_token)
        if not filename:
            logger.warning(u'远程ip: {} 尝试申请下载: {} 被阻止!'.format(request.remote_addr, file_token))
            abort(403)
        return redirect(url_for('download_file', file_token=file_token, filename=filename))

    @check_remote
    def post(self, file_token):
        md5 = request.form['md5']
        file = request.files['file']
        if md5 and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            check = get_md5(file)
            if check != md5:
                logger.error(u'上传文件:{}, token:{} md5校验不过,原始值为: {}'.format(filename, file_token, md5))
                abort(600, message=u'文件校验不一样: {}'.format(check))
            file.save(os.path.join(Myconfig.UPLOAD_FOLDER, file_token))
            fm = FileManager()
            fm.update(file_token, file.filename)
            logger.info(u'文件: {} 上传通过: {}'.format(filename, file_token))
            return jsonify(filename=filename, url=request.base_url, md5=md5)
        abort(400, message=u'只允许以下格式上传: {}'.format(','.join(Myconfig.ALLOWED_EXTENSIONS)))

APP_API.add_resource(OK, '/ok.htm')
APP_API.add_resource(TokenApi, '/api/token')
APP_API.add_resource(FileApi, '/api/file/<file_token>')
APP_API.add_resource(ClientApi, '/api/<file_token>/<filename>', endpoint='download_file', methods=['GET'])
