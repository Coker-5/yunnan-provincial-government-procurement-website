import io
import time
import uuid
from logging import currentframe

import matplotlib.pyplot as plt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import requests
import json

session = requests.Session()


# 1.模拟第一个请求（初始化cookie）
def get_list():
    global session
    # 获取xincaigou,route,JSESSIONID参数

    headers = {
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Origin": "http://www.ccgp-yunnan.gov.cn",
        "Pragma": "no-cache",
        "Referer": "http://www.ccgp-yunnan.gov.cn/page/procurement/procurementList.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    cookies = {
        "xincaigou": "49737.2924.1035.0000"
    }
    url = "http://www.ccgp-yunnan.gov.cn/api/common/otheruse.linklist.svc"
    response = session.post(url, headers=headers, cookies=cookies, verify=False)
    cookie_str = requests.utils.dict_from_cookiejar(response.cookies)
    cookie_str = "; ".join([f"{name}={value}" for name, value in cookie_str.items()]) + "^"

    print(f"{cookie_str}")
    return cookie_str


# 2.模拟第二个请求（获取验证码）
def get_captcha():
    # 生成clientuid
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    client_uid = f'point-{uuid_str}'
    url = "http://www.ccgp-yunnan.gov.cn/api/captcha/captcha.get.svc"

    data = {
        "captchaType": "clickWord",
        "clientUid": client_uid,
        "ts": int(time.time() * 1000)
    }
    data = json.dumps(data, separators=(',', ':'))
    response = session.post(url, data=data, verify=False).json()

    base_img = response["data"]["repData"]["originalImageBase64"]
    token = response["data"]["repData"]["token"]
    word_list = response["data"]["repData"]["wordList"]
    secret_key = response["data"]["repData"]["secretKey"]
    # 显示验证码
    image_data = base64.b64decode(base_img)
    # 创建一个BytesIO对象存放解码后的图像数据
    image_buffer = io.BytesIO(image_data)
    # 使用matplotlib的imread函数读取图像数据并显示
    image = plt.imread(image_buffer)
    plt.imshow(image)
    plt.axis('off')  # 可以选择关闭坐标轴显示
    # plt.show()
    plt.imsave("captcha.png", image)
    return token, word_list, secret_key, client_uid


# 3.输入验证码并生成 pointJson
def aes_encrypt(word, key_word):
    # 转换密钥为bytes类型
    key = key_word.encode('utf-8')
    # 序列化并编码待加密内容
    data = json.dumps(word, separators=(',', ':')).encode('utf-8')
    # 创建AES加密器（ECB模式自动处理填充）
    cipher = AES.new(key, AES.MODE_ECB)
    # 加密并返回Base64字符串
    return base64.b64encode(cipher.encrypt(pad(data, AES.block_size))).decode()


# 4.模拟第三个请求（验证）
def verify(pointJson, token, clientUid):
    global session
    url = "http://www.ccgp-yunnan.gov.cn/api/captcha/captcha.check.svc"
    data = {
        "captchaType": "clickWord",
        "pointJson": pointJson,
        "token": token,
        "clientUid": clientUid,
        "ts": int(time.time() * 1000)
    }

    # Send the POST request
    response = session.post(url, json=data, verify=False)
    # print(f"请求头:{session.headers}————{data}")

    # Print the response
    print(response.text)


#  5.生成captchaCheckFlag参数
def make_captcha_check_flag(_this:dict) -> str:
    # 构造待加密字符串
    plaintext = f'{_this["backToken"]}---{json.dumps(_this["checkPosArr"], separators=(",", ":"))}'
    """AES/ECB/PKCS7加密实现（兼容CryptoJS标准）"""
    key_bytes = _this["secretKey"].encode('utf-8')  # 确保与CryptoJS的UTF8.parse一致
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode('utf-8')


# 6.带参数请求最终数据
def fetch_procurement_data(captcha_check_flag, current=7, row_count=10, search_phrase=""):
    global session

    url = f"http://www.ccgp-yunnan.gov.cn/api/procurement/Procurement.gghtMoreList.svc?captchaCheckFlag={captcha_check_flag}&p=7"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://www.ccgp-yunnan.gov.cn",
        "Pragma": "no-cache",
        "Referer": "http://www.ccgp-yunnan.gov.cn/page/procurement/procurementList.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "current": str(current),
        "rowCount": str(row_count),
        "searchPhrase": search_phrase
    }

    response = session.post(url, headers=headers, data=data, verify=False)
    print(f"请求头：{session.headers}")
    return response.text # 如果返回JSON数据则自动解析





if __name__ == '__main__':
    # 1.初始化cookie
    get_list()
    # 2.获取验证码
    token, word_list, secret_key, client_uid = get_captcha()
    print(token, word_list, secret_key, client_uid)
    # 3.输入验证码
    point_input = json.loads(input("请输入结果："))   #[{"x": 244, "y": 62},{"x": 274, "y": 73},{"x": 257, "y": 90}]
    # 4.验证码结果加密
    vencrypted_result = aes_encrypt(point_input, secret_key)
    # 5.验证验证码
    verify(vencrypted_result, token,client_uid)
    # 6.生成captchaCheckFlag参数
    _this = {
            "secretKey": secret_key,
            "backToken": token,
            "checkPosArr": point_input
        }
    print(_this)
    captcha_verification = make_captcha_check_flag(_this)
    print(captcha_verification)
    current_page=2 #页码
    # 7.请求最终数据
    print(fetch_procurement_data(captcha_verification,current=current_page))
