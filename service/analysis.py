import re

# 文本删除函数
# def text_remove(text):
#     # 确保输入是字符串类型
#     if not isinstance(text, str):
#         text = str(text) # 将非字符串类型转换为字符串
#     # 删除回复 用户名: 格式的前缀
#     text = re.sub(r'回复.*?:\s', '', text)
#     # 删除@用户名的文本
#     text = re.sub(r'@(.*)(.*)(?= )|@(.*)', '', text)
#     # 删除全部标点符号,特殊符号和emoji
#     text = re.sub(r'[^\w\s]', '', text)
#     # 删除文本中的多余空格
#     text = re.sub(r'\s+', '', text.strip())
#     return text
# # 分析数据并保存到分析数据库
def text_remove(text):
    # 确保输入是字符串类型
    if not isinstance(text, str):
        text = str(text)
    # 删除文本中的多余空格
    text = re.sub(r'\s+', '', text.strip())
    return text