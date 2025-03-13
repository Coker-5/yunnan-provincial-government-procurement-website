import ddddocr
from PIL import Image, ImageDraw
from io import BytesIO

def ocr_captcha():
    # 初始化OCR和目标检测器
    detector = ddddocr.DdddOcr(det=True,beta=True)

    # 读取图片
    image_path = "captcha.png"
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    bboxes = detector.detection(image_bytes)

    # 初始化文字识别OCR
    ocr = ddddocr.DdddOcr()

    # 用PIL打开图片并转换到RGB模式
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    output_result = {}  # 存储最终结果的字典

    for bbox in bboxes:
        x1, y1, x2, y2 = bbox

        # 裁剪出检测区域
        cropped = image.crop((x1, y1, x2, y2))

        # 将裁剪的图片转换为合法的字节流
        img_byte_arr = BytesIO()
        cropped.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # 识别文字
        text = ocr.classification(img_byte_arr)

        # 计算中心坐标
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # 绘制红色矩形框和文字标签
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1 + 5, y1 - 25), text, fill="red")

        # 将结果存入字典
        output_result[text] = {"x": center_x, "y": center_y}

    image.show()

    # 输出格式化结果
    print(f"识别结果：{output_result}")
    return output_result

