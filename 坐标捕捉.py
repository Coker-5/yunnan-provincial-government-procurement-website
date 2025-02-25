import json
from tkinter import Tk, Canvas, NW
from PIL import ImageTk, Image

# 初始化窗口
root = Tk()
root.title("点击坐标捕捉器 (2025.02.24)")

# 加载图片（替换为你的验证码图片路径）
image_path = "captcha.png"
img = Image.open(image_path)
photo = ImageTk.PhotoImage(img)

# 创建画布并显示图片
canvas = Canvas(root, width=img.width, height=img.height)
canvas.pack()
canvas.create_image(0, 0, anchor=NW, image=photo)

# 初始化坐标存储列表
coordinates = []

li=[]

def save_position(event):
    """记录点击坐标并在画布上标记位置"""
    x, y = event.x, event.y
    coordinates.append((x, y))

    # 创建红色标记点
    marker = canvas.create_oval(
        x - 3, y - 3, x + 3, y + 3,
        fill='red', outline='black'
    )

    # 显示坐标文本（2秒后消失）
    text = canvas.create_text(
        x + 10, y - 10,
        text=f"({x}, {y})",
        fill="red", font=("Arial", 10)
    )
    canvas.after(2000, canvas.delete, text)

    li.append({"x": x, "y": y})
    print(json.dumps(li))


# 绑定鼠标左键点击事件
canvas.bind("<Button-1>", save_position)

# 添加操作提示
canvas.create_text(
    20, 20,
    fill="blue", anchor=NW,
    font=("Arial", 12, "bold")
)

root.mainloop()