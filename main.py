import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

# 密文字符集
CIPHER_MAP = {
    '0': '切',
    '1': '卟',
    '2': '叮',
    '3': '咧',
    '4': '哔',
    '5': '唎',
    '6': '啪',
    '7': '啰',
    '8': '啵',
    '9': '嘭',
    'A': '噜',
    'B': '噼',
    'C': '巴',
    'D': '拉',
    'E': '蹦',
    'F': '铃'
}
REVERSE_CIPHER_MAP = {v: k for k, v in CIPHER_MAP.items()}

@register("切噜", "切噜", "切噜", "1.0.0")
class SongSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

class RepeatAfterMePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("切噜")
    async def repeat_after_me(self, event: AstrMessageEvent):
        """提取并返回用户输入的内容"""
        # 获取用户输入的完整消息
        message_str = event.message_str.strip()
        
        # 使用正则表达式提取“切噜”后面的内容
        match = re.search(r'切噜\s*([\s\S]*)', message_str)
        if match:
            # 提取匹配到的内容
            user_input = match.group(1).strip()
            if user_input:
                # 将用户输入的内容转换为GB18030编码
                try:
                    # 分离文本和标点符号
                    text_parts = re.findall(r'[\w\u4e00-\u9fff]+|[^\\w\u4e00-\u9fff]', user_input)
                    encoded_parts = []
                    cipher_text_parts = []

                    for part in text_parts:
                        # 对汉字/字母部分进行编码转换
                        if re.match(r'[\w\u4e00-\u9fff]+', part):
                            gb18030_encoded = part.encode('gb18030')
                            # 将字节转换为十六进制字符串表示
                            hex_gb18030_encoded = ''.join(f'{byte:02x}' for byte in gb18030_encoded)
                            # 将每位的顺序颠倒
                            reversed_hex = ''.join([f'{byte[1]}{byte[0]}' for byte in [hex_gb18030_encoded[i:i+2] for i in range(0, len(hex_gb18030_encoded), 2)]])
                            # 映射到密文字符集
                            cipher_part = ''.join([CIPHER_MAP.get(reversed_hex[i:i+1].upper(), '') for i in range(len(reversed_hex))])
                            encoded_parts.append(hex_gb18030_encoded)
                            cipher_text_parts.append(cipher_part)
                        else:
                            # 保留标点符号
                            encoded_parts.append(part)
                            cipher_text_parts.append(part)

                    # 构建最终的编码结果和密文结果
                    hex_gb18030_encoded = ' '.join(encoded_parts)
                    cipher_text = ''.join(cipher_text_parts)

                    # 返回结果
                    yield event.plain_result(f"切噜～♪切{cipher_text}")
                except Exception as e:
                    yield event.plain_result(f"切噜失败：{e}")
            else:
                yield event.plain_result("切噜～♪切哔巴咧蹦咧巴噼噼咧拉切拉噼巴唎噼噼噼切噼铃拉啰铃")
        else:
            yield event.plain_result("切噜～♪切巴巴拉铃叮噼噼噼啪噼蹦噜铃拉啰铃")

    @filter.command("cheru")
    async def reverse_translate(self, event: AstrMessageEvent):
        """逆向翻译密文映射结果"""
        # 获取用户输入的完整消息
        message_str = event.message_str.strip()
        
        # 使用正则表达式提取“逆翻译”后面的内容
        match = re.search(r'cheru\s*([\s\S]*)', message_str)
        if match:
            # 提取匹配到的内容
            cipher_text = match.group(1).strip()
            if cipher_text:
                # 删除句首的“切噜～♪切”
                if cipher_text.startswith("切噜～♪切"):
                    cipher_text = cipher_text[5:]  # 删除前5个字符

                try:
                    # 将密文转换回十六进制
                    reversed_hex = ''.join([REVERSE_CIPHER_MAP.get(char, '') for char in cipher_text])

                    # 将每位的顺序颠倒回来
                    original_hex = ''.join([f'{byte[1]}{byte[0]}' for byte in [reversed_hex[i:i+2] for i in range(0, len(reversed_hex), 2)]])

                    # 将十六进制转换回字节
                    original_bytes = bytes.fromhex(original_hex)

                    # 将字节解码为原始字符串
                    original_text = original_bytes.decode('gb18030')

                    yield event.plain_result(f"这句话的意思是：{original_text}")
                except Exception as e:
                    yield event.plain_result(f"翻译失败：{e}")
            else:
                yield event.plain_result("切噜～♪切噼巴唎噼噼噼切噼铃拉啰铃")
        else:
            yield event.plain_result("开头不是‘cheru’听不懂喵")