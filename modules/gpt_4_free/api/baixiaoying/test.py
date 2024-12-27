import execjs

# 读取crypto-js库文件和你的JavaScript代码
with open('./crypto-js.min.js', 'r', encoding='utf-8') as file:
    crypto_js_code = file.read()


with open('./encryption.js', 'r', encoding='utf-8') as file:
    script_code = file.read()

# 整合JavaScript代码
js_code = crypto_js_code + "\n" + script_code

# 编译JavaScript代码
ctx = execjs.compile(js_code)

# 执行JavaScript代码并获取结果
result = ctx.call("runs_sign")

# 输出结果
print(result)
