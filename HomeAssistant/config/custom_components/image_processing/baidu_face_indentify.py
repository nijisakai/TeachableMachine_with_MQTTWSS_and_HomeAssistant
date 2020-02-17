"""
百度人脸识别、人脸检测

# 基于百度人脸识别api:
    https://ai.baidu.com/tech/face

# Author:
    lidicn

# Edition：V1.26


# Update:
    2018-7-18

# 配置方法参见:
https://bbs.hassbian.com/thread-2460-1-1.html
"""
import logging
import io
import os
import voluptuous as vol
from base64 import b64encode
from homeassistant.core import split_entity_id
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, CONF_SOURCE, CONF_ENTITY_ID, CONF_NAME)
from homeassistant.components.image_processing import ATTR_CONFIDENCE
from homeassistant.components.image_processing.microsoft_face_identify import (
    ImageProcessingFaceEntity)
import homeassistant.helpers.config_validation as cv
import requests
import json
import base64
from requests import get
import time
from PIL import Image
import sys
import homeassistant.loader as loader
import threading
from requests.exceptions import ReadTimeout,ConnectionError,RequestException
_LOGGER = logging.getLogger(__name__)

ATTR_NAME = 'name'
ATTR_MATCHES = 'faces'
ATTR_TOTAL_MATCHES = 'total faces'
ATTR_FACE_STRING = 'face_string'
ATTR_GET_PICTURE_COSTTIME = '获取照片耗时'
ATTR_RESIZE_PICTURE_COSTTIME = '调整分辨率耗时'
ATTR_RECOGNITION_COSTTIME = '人脸识别耗时'
ATTR_TOTAL_COSTTIME = '总耗时'

GROUP_ID = 'normal_group'


CONF_APP_ID = 'app_id'
CONF_API_KEY = 'api_key'
CONF_SECRET_KEY = 'secret_key'
CONF_SNAPSHOT_FILEPATH = 'snapshot_filepath'
CONF_RESIZE = 'resize'
CONF_HA_URL = 'ha_url'
CONF_HA_PASSWORD = 'ha_password'
CONF_DETECT_TOP_NUM = 'detect_top_num'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_APP_ID): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_SECRET_KEY): cv.string,
    vol.Required(CONF_RESIZE,default='0'): cv.string,
    vol.Required(CONF_HA_URL): cv.url,
    vol.Required(CONF_HA_PASSWORD): cv.string,
    vol.Required(CONF_SNAPSHOT_FILEPATH): cv.string,
    vol.Optional(CONF_DETECT_TOP_NUM,default=1): cv.positive_int,
})

ATTR_USERINFO = 'user_info'
ATTR_IMAGE = 'image'
ATTR_UID = 'uid'
ATTR_GROUPID = 'group_id'
DOMAIN = 'image_processing'

SERVUCE_REGISTERUSERFACE = 'baidu_face_indentify_registerUserFace'
SERVUCE_REGISTERUSERFACE_SCHEMA = vol.Schema({
    vol.Required(ATTR_USERINFO): cv.string,
    vol.Required(ATTR_IMAGE): cv.isfile,
    vol.Required(ATTR_UID): cv.string,
})

SERVUCE_GETUSERLIST = 'baidu_face_indentify_getUserList'
SERVUCE_GETUSERLIST_SCHEMA = vol.Schema({
    vol.Optional(ATTR_GROUPID,default=GROUP_ID): cv.string,
})

SERVUCE_DELETEUSER = 'baidu_face_indentify_deleteUser'
SERVUCE_DELETEUSER_SCHEMA = vol.Schema({
    vol.Required(ATTR_UID): cv.string,
})

SERVUCE_DETECTFACE = 'baidu_face_indentify_detectface'
SERVUCE_DETECTFACE_SCHEMA = vol.Schema({
    vol.Required(ATTR_IMAGE): cv.isfile,
})

face_fields = {"face_token":"唯一标识",
"location":"人脸位置",
"left":"离左边界的距离",
"top":"离上边界的距离",
"width":"宽度",
"height":"高度",
"rotation":"人脸框相对于竖直方向的顺时针旋转角[-180(逆时针),180(顺时针)]",
"face_probability":"人脸置信度[0最小、1最大]",
"angel":"人脸旋转角度参数",
"yaw":"三维旋转之左右旋转角[-90(左),90(右)]",
"pitch":"三维旋转之俯仰角度[-90(上),90(下)]",
"roll":"平面内旋转角[-180(逆时针),180(顺时针)]",
"age":"年龄",
"beauty":"美丑打分[范围0-100，越大表示越美]",
"expression":"表情",
"probability":"置信度[0-1]",
"gender":"性别",
"glasses":"是否带眼镜",
"race":"人种",
"face_type":"人脸类型",
"quality":"人脸质量信息",
"occlusion":"遮挡概率",
"left_eye":"左眼遮挡[0-1]",
"right_eye":"右眼遮挡[0-1]",
"nose":"鼻子遮挡[0-1]",
"mouth":"嘴巴遮挡[0-1]",
"left_cheek":"左脸颊遮挡[0-1]",
"right_cheek":"右脸颊遮挡[0-1]",
"chin":"下巴遮挡[0-1]",
"blur":"人脸模糊程度(0清晰，1模糊)",
"illumination":"光照程度(0-255)",
"completeness":"人脸完整度(0-1)",
"type":"类型",
"none":"无",
"smile":"微笑",
"laugh":"大笑",
"face_shape":"脸型",
"square":"正方形",
"triangle":"三角形",
"oval":"椭圆",
"heart":"心形",
"round":"圆形",
"male":"男性",
"female":"女性",
"common":"普通眼镜",
"sun":"墨镜",
"yellow":"黄种人",
"white":"白种人",
"black":"黑种人",
"arabs":"阿拉伯人",
"human":"真实人脸",
"cartoon":"卡通人脸"}

human_type = {
    "human": ["真实人脸置信度","%"],
    "cartoon": ["卡通人脸置信度","%"],
}
faceshape = {
    "square":["国字脸","%"],
    "triangle":["倒三角脸","%"],
    "oval":["鹅蛋脸","%"],
    "heart":["心形脸","%"],
    "round":["圆脸","%"],
}

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the demo image processing platform."""
    app_id = config.get(CONF_APP_ID)
    api_key = config.get(CONF_API_KEY)
    secret_key = config.get(CONF_SECRET_KEY)
    snapshot_filepath = config.get(CONF_SNAPSHOT_FILEPATH)
    resize = config.get(CONF_RESIZE)
    ha_url = config.get(CONF_HA_URL)
    ha_password = config.get(CONF_HA_PASSWORD)
    detect_top_num = config.get(CONF_DETECT_TOP_NUM)
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(BaiduFaceIdentifyEntity(
            hass,camera[CONF_ENTITY_ID], camera.get(CONF_NAME),app_id,api_key,secret_key,snapshot_filepath,resize,ha_url,ha_password,detect_top_num
        ))
    add_devices(entities)
    persistent_notification = loader.get_component(hass,'persistent_notification')
    def getAccessToken():
        #请求参数
        client_id = api_key
        client_secret = secret_key
        grant_type = 'client_credentials'
        request_url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': grant_type}
        r = requests.get(url=request_url, params=params)
        access_token = json.loads(r.text)['access_token']
        return access_token

    def get_image_base64(image_path):
        with open(image_path, 'rb') as fp:
            return base64.b64encode(fp.read())

    #人脸注册服务
    def registerUserFace(service):

        def register():
            user_info = service.data[ATTR_USERINFO]
            uid = service.data[ATTR_UID]
            image = service.data[ATTR_IMAGE]
            group_id = GROUP_ID
            #request_url = "https://aip.baidubce.com/rest/2.0/face/v2/faceset/user/add"
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
            img = get_image_base64(image)

            params = {'access_token': getAccessToken()}
            #data = {"group_id": group_id, "image": img, "uid": uid, "user_info": user_info}
            data = {"image_type": "BASE64","group_id": group_id, "image": img, "user_id": uid, "user_info": user_info}
            r = requests.post(url=request_url, params=params, data=data)
            resultjson = json.loads(r.text)
            print ('人脸注册服务返回：',resultjson)
            if 'error_code' in resultjson and resultjson['error_code'] != 0:
                persistent_notification.create(hass,resultjson['error_msg'],title='百度人脸识别')
            else:
                persistent_notification.create(hass,'人脸数据注册成功',title='百度人脸识别')
            return json.loads(r.text)
        threading.Thread(target=register).start()
    hass.services.register(DOMAIN, SERVUCE_REGISTERUSERFACE, registerUserFace,schema=SERVUCE_REGISTERUSERFACE_SCHEMA)

    #人脸数据查询服务
    def getUserInfo(service):
        def userinfo():
            group_id = service.data[ATTR_GROUPID]
            #request_url = "https://aip.baidubce.com/rest/2.0/face/v2/faceset/group/getusers"
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getusers"
            params = {'access_token': getAccessToken()}
            data = {"group_id": group_id}
            r = requests.post(url=request_url, params=params, data=data)
            resultjson = json.loads(r.text)
            print ('人脸数据查询服务返回：',resultjson)
            #outputst = ''
            br_string = ''
            if 'error_code' in resultjson and resultjson['error_code'] != 0:
                persistent_notification.create(hass,resultjson['error_msg'],title='百度人脸识别')
            elif len(resultjson['result']['user_id_list']) == 0:
                persistent_notification.create(hass,'无人脸注册数据',title='百度人脸识别')
            else:
                for i in range(len(resultjson['result']['user_id_list'])):
                    br_string = br_string + str(resultjson['result']['user_id_list'][i]) + '<br />'

                persistent_notification.create(hass,br_string,title='百度人脸识别')
            return json.loads(r.text)
        threading.Thread(target=userinfo).start()
    hass.services.register(DOMAIN, SERVUCE_GETUSERLIST, getUserInfo,schema=SERVUCE_GETUSERLIST_SCHEMA)

    #人脸数据删除服务
    def delUserInfo(service):
        def deluserinfo():
            uid = service.data[ATTR_UID]
            group_id = service.data[ATTR_GROUPID]
            #request_url = "https://aip.baidubce.com/rest/2.0/face/v2/faceset/user/delete"
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/delete"
            params = {'access_token': getAccessToken()}
            #data = {'uid': uid}
            data = {"group_id": group_id,'user_id': uid}
            r = requests.post(url=request_url, params=params, data=data)
            resultjson = json.loads(r.text)
            print ('人脸数据删除服务返回：',resultjson)
            if 'error_code' in resultjson and resultjson['error_code'] != 0:
                persistent_notification.create(hass,resultjson['error_msg'],title='百度人脸识别')
            else:
                persistent_notification.create(hass,'人脸数据删除成功',title='百度人脸识别')
            return json.loads(r.text)
        threading.Thread(target=deluserinfo).start()
    hass.services.register(DOMAIN, SERVUCE_DELETEUSER, delUserInfo,schema=SERVUCE_DELETEUSER_SCHEMA)

    def dict_generator(indict, pre=None):
        pre = pre[:] if pre else []
        if isinstance(indict, dict):
            for key, value in indict.items():
                if isinstance(value, dict):
                    if len(value) == 0:
                        yield pre+[key, '{}']
                    else:
                        for d in dict_generator(value, pre + [key]):
                            yield d
                elif isinstance(value, list):
                    if len(value) == 0:                   
                        yield pre+[key, '[]']
                    else:
                        for v in value:
                            for d in dict_generator(v, pre + [key]):
                                yield d
                elif isinstance(value, tuple):
                    if len(value) == 0:
                        yield pre+[key, '()']
                    else:
                        for v in value:
                            for d in dict_generator(v, pre + [key]):
                                yield d
                else:
                    yield pre + [key, value]
        else:
            yield indict
            
    
    def details_faceinfo(jsonObj):
        infostr = ''
        for i in dict_generator(jsonObj):
            for j in range(len(i[0:-1])):
                if i[j] in face_fields:
                   infostr = infostr + "-" + face_fields[str(i[j])]
            if str(i[-1]) in face_fields:
                infostr = infostr + ":" + face_fields[str(i[-1])] + "<br />"
            else:
                infostr = infostr + ":" + str(i[-1]) + "<br />"
        return infostr




    #人脸检测服务
    def detectface(service):
        def detect():
            image = service.data[ATTR_IMAGE]
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
            img = get_image_base64(image)
            params = {'access_token': getAccessToken()}
            data = {"image": img,"image_type":"BASE64","face_field": "age,beauty,expression,face_shape,gender,glasses,race,quality"}
            r = requests.post(url=request_url, params=params, data=data)
            resultjson = json.loads(r.text)
            print ('人脸检测服务返回：',resultjson)
            if 'error_code' in resultjson and resultjson['error_code'] != 0:
                persistent_notification.create(hass,resultjson['error_msg'],title='百度人脸识别')
            elif 'result' in resultjson:
                if resultjson['result']['face_num'] == 0:
                    persistent_notification.create(hass,'没检测到人脸存在！',title='百度人脸识别')
                else:
                    persistent_notification.create(hass,details_faceinfo(resultjson['result']['face_list'][0]),title='百度人脸识别')
            else:
                if resultjson['face_num'] == 0:
                    persistent_notification.create(hass,'没检测到人脸存在！',title='百度人脸识别')
                else:
                    persistent_notification.create(hass,details_faceinfo(resultjson['face_list'][0]),title='百度人脸识别')
            return json.loads(r.text)
        threading.Thread(target=detect).start()
    hass.services.register(DOMAIN, SERVUCE_DETECTFACE, detectface,schema=SERVUCE_DETECTFACE_SCHEMA)

class BaiduFaceIdentifyEntity(ImageProcessingFaceEntity):
    """Dlib Face API entity for identify."""


    def __init__(self, hass, camera_entity, name, app_id, api_key, secret_key, snapshot_filepath,resize,ha_url,ha_password,detect_top_num):
        """Initialize demo ALPR image processing entity."""

        super().__init__()
        self.hass = hass
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.snapshot_filepath = snapshot_filepath
        self.resize = resize
        self.ha_url = ha_url
        self.ha_password = ha_password

        if name:
            self._name = name
        else:
            self._name = "Baidu Face {0}".format(
                split_entity_id(camera_entity)[1])
        self._camera = camera_entity
        self.unknowns_face_path = os.path.join(self.snapshot_filepath,'face.jpg')
        self.resize_face_path = os.path.join(self.snapshot_filepath,'resize.jpg')
        self.detect_top_num = detect_top_num


        self._matches = {}
        self._total_matches = 0
        self._face_string = ''

        self._get_picture_costtime = ''
        self._reszie_picture_costtime = ''
        self._recognition_costtime = ''
        self._total_costtime = ''


    def get_file_content(self,filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def getAccessToken(self):
        #请求参数
        client_id = self.api_key
        client_secret = self.secret_key
        grant_type = 'client_credentials'

        request_url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': grant_type}

        try:
            response = requests.get(url=request_url, params=params,timeout=5)
            access_token = json.loads(response.text)['access_token']
        except ReadTimeout:
            _LOGGER.error("百度人脸识别获取access_token连接超时")
        except ConnectionError:
            _LOGGER.error("百度人脸识别获取access_token连接错误")
        except RequestException:
            _LOGGER.error("百度人脸识别获取access_token发生未知错误")
        return access_token

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._total_matches

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        return {
            ATTR_MATCHES: self._matches,
            ATTR_TOTAL_MATCHES: self._total_matches,
            ATTR_FACE_STRING: self._face_string,
            ATTR_GET_PICTURE_COSTTIME: self._get_picture_costtime,
            ATTR_RESIZE_PICTURE_COSTTIME: self._reszie_picture_costtime,
            ATTR_RECOGNITION_COSTTIME: self._recognition_costtime,
            ATTR_TOTAL_COSTTIME: self._total_costtime,

        }

    def resize_picture(self,imagepath,resize):
        im = Image.open(imagepath)
        (x,y) = im.size #read image size
        x_s = resize #define standard width
        y_s = int(y * x_s / x) #calc height based on standard width
        out = im.resize((x_s,y_s),Image.ANTIALIAS) #resize image with high-quality
        out.save(self.resize_face_path)

    def get_picture(self):
        host=self.ha_url
        t=time.time()
        url = '{}/api/camera_proxy/{}?time={}'.format(host, self._camera , int(round(t * 1000)))
        headers = {'x-ha-access': self.ha_password,
                   'content-type': 'application/json'}
        response = get(url, headers=headers)
        with open(self.unknowns_face_path, 'wb') as fo:
            fo.write(response.content)

    def strat_time(self):
        return time.time()

    def count_time(self,start_time):
        cost_time = time.time() - start_time
        return str(round(cost_time,5))+"秒"


    def process_image(self, image):
        """Process image."""
        get_picture_start = time.time()
        self.get_picture()
        get_picture_costtime = self.count_time(get_picture_start)
        if int(self.resize) != 0:
            resize_picture_start = time.time()
            self.resize_picture(self.unknowns_face_path,int(self.resize))
            reszie_picture_costtime = self.count_time(resize_picture_start)
            convert_start = time.time()
            unknowns = self.get_file_content(self.resize_face_path)
            convert_costtime = self.count_time(convert_start)

        elif self.resize == '0':
            reszie_picture_costtime = '0秒'
            convert_start = time.time()
            unknowns = self.get_file_content(self.unknowns_face_path)
            convert_costtime = self.count_time(convert_start)

        recognition_time = time.time()
        found = []

        #request_url = "https://aip.baidubce.com/rest/2.0/face/v2/identify"
        #request_url = "https://aip.baidubce.com/rest/2.0/face/v2/multi-identify"
        
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/multi-search"

        # 参数images：图像base64编码
        img = base64.b64encode(unknowns)

        params = {'access_token': self.getAccessToken()}
        data = {
            "image": img,
            "image_type": "BASE64",
            "group_id_list": GROUP_ID,
            "max_face_num": self.detect_top_num
            }

        
        try:
            r = requests.post(url=request_url, params=params, data=data,timeout=5)
        except ReadTimeout:
            _LOGGER.error("百度人脸识别连接超时")
        except ConnectionError:
            _LOGGER.error("百度人脸识别连接错误")
        except RequestException:
            _LOGGER.error("百度人脸识别发生未知错误")

        print("识别结果",r.text)
        resultjson = json.loads(r.text)
        face_string = ''
        result_num = 0
        if 'error_code' in resultjson and resultjson['error_code'] != 0:
            recognition_costtime = resultjson['error_msg']
        elif not 'result' in resultjson or resultjson['result'] == None:
            found = []
            recognition_costtime = '未识别出人脸！'
            if 'error_msg' in resultjson:
                _LOGGER.info('BaiduFaceIdentify face not found!')
        elif 'result' in resultjson:
            result = resultjson['result']
            if 'face_num' in result:
                result_num = result['face_num']
                face_list = result['face_list']
            for i in range(len(face_list)):
                user_list = face_list[i]['user_list']
                for j in range(len(user_list)):
                    if user_list[j]['score'] < 80:
                        pass
                        recognition_costtime = '未识别出匹配数据库的人脸！'
                    elif user_list[j]['score'] > 80:
                        found.append({
                            ATTR_NAME: user_list[j]['user_info'],
                            ATTR_CONFIDENCE: user_list[j]['score']
                        })
                        face_string = face_string + user_list[j]['user_info'] + '、'
                        recognition_costtime = self.count_time(recognition_time)
                        
        total_costtime = self.count_time(get_picture_start)
        self._get_picture_costtime = get_picture_costtime
        self._reszie_picture_costtime = reszie_picture_costtime
        self._recognition_costtime = recognition_costtime
        self._total_costtime = total_costtime

        self._face_string = face_string
        self._total_matches = result_num
        self._matches = found
