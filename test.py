from cryptography.fernet import Fernet
from urllib.parse import urlencode, quote_plus, unquote_plus

# Fernetキーの生成
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# パラメータの作成
params = {"user_id": "123", "role": "admin"}
original_param_string = urlencode(params)

# パラメータの暗号化
cipher_text = cipher_suite.encrypt("org_id=100713166408778476".encode())

# 暗号化されたパラメータをURLに追加
encrypted_param_string = quote_plus(cipher_text.decode())
url_with_encrypted_param = f"https://example.com/api?data={encrypted_param_string}"


print(encrypted_param_string)
