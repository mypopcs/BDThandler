# 基础配置类
class Config:
    """基础配置类，定义所有环境共有的配置项。"""
    
    # Flask应用的密钥，用于安全签名，如会话cookie
    SECRET_KEY = 'a_very_secret_key'
    
    # 是否开启调试模式，开发时设置为True，生产环境设置为False
    DEBUG = True
    
    # 文件上传后保存的目录
    UPLOAD_FOLDER = 'uploads'
    
    # 允许上传的文件扩展名集合
    ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

# 数据库配置（所有环境通用）
DATABASE_CONFIG = {
    'user': 'root',       # 数据库用户名
    'password': '123456',  # 数据库密码
    'host': 'localhost',   # 数据库主机地址
    'port': '3306',        # 数据库端口
    'db': 'fenxi',         # 数据库名称
}

# 构建数据库URI的函数
def get_database_url(config):
    """
    根据配置信息构建数据库连接URI。
    返回格式为: mysql+pymysql://user:password@host:port/db
    """
    return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db']}"

# 开发环境配置
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = get_database_url(DATABASE_CONFIG)  # 源数据数据库连接URI

# 测试环境配置
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = get_database_url(DATABASE_CONFIG)  # 源数据数据库连接URI

# 生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = get_database_url(DATABASE_CONFIG)  # 源数据数据库连接URI

# 您可以在Flask应用中使用配置
# 示例：app.config.from_object('config.DevelopmentConfig')