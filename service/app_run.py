
# 导入所需的模块
import re
import logging
from sqlalchemy import create_engine
from config import DevelopmentConfig # 导入数据库配置
from flask import Flask, request, jsonify  # Flask框架相关
from flask_cors import CORS  # 解决跨域资源共享问题
from analysis import text_remove # 导入text_remove函数
from data import save_to_mysql, get_data, get_data_common

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__) # 创建Flask应用实例
app.config.from_object(DevelopmentConfig) # 加载配置文件中的配置
CORS(app)  # 允许跨域请求

# 数据库引擎设置
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# 全局变量存储正则表达式列表
analysis_config = {
    'regex_list': [],
    'synonyms': [],
    'stopwords': []
}
    
def clean_data(df, text_column):
    df = df.dropna(subset=[text_column])
    return df.drop_duplicates()

# 正则处理
def apply_regex(text, regex_list):
    for regex in regex_list:
        text = re.sub(regex['regex'], '', text) # 使用re.sub函数将匹配到的文本替换为空字符串
    return text

# 同义词替换
def replace_synonyms(words, synonyms):
    return [synonyms.get(word, word) for word in words]
# 停用词
def filter_stopwords(words, stopwords):
    return [word for word in words if word not in stopwords and len(word) > 1]

# 定义文本匹配函数
def process_text(df, text_column, config):
    def process_entry(text):
        if not isinstance(text, str): # 确保传入为字符串类型
            text = str(text)
        text = text_remove(text) # 文本清理
        text = apply_regex(text, config['regex_list'])
        words = text.split()
        words = replace_synonyms(words, config['synonyms'])
        words = filter_stopwords(words, config['stopwords'])
        # 重新组合文本
        processed_text = " ".join(words)
        return text, processed_text

    df['源文本'], df[text_column] = zip(*df[text_column].apply(process_entry))
    df = df[df[text_column].str.strip() != '']
    return df

def update_config(config_data): # 更新全局配置
    global analysis_config
    analysis_config['regex_list'] = config_data['regexList']
    analysis_config['synonyms'] = {word: group['replacement'] 
                                   for group in config_data['synonyms'] 
                                   for word in group['words']}
    analysis_config['stopwords'] = set(config_data['stopwords'])

def log_config(): #记录更新后的配置
    logger.info(f"正则数据: {analysis_config['regex_list']}")
    logger.info(f"同义词数据: {analysis_config['synonyms']}")
    logger.info(f"停用词数据: {analysis_config['stopwords']}")

def process_and_save_data(): #处理数据并保存到数据库
    source_data = get_data('excel_data', -1, db_engine)
    source_data = clean_data(source_data, '评论内容')
    processed_data = process_text(source_data, '评论内容', analysis_config)
    save_to_mysql(processed_data, 'analyzed_data', db_engine)

# 获取分析前的数据
@app.route('/get_source_data', methods=['GET'])
def get_source_data():
    return get_data_common('excel_data', db_engine)

# 获取分析后的数据
@app.route('/get_analyzed_data', methods=['GET'])
def get_analyzed_data():
    return get_data_common('analyzed_data', db_engine)

# 处理分析数据
@app.route('/update_analysis_config', methods=['POST'])
def update_analysis_config():
    try:
        config_data = request.json
        update_config(config_data)
        # log_config()
        process_and_save_data()
        return jsonify({'success': True, 'message': '数据已处理并保存到分析数据库'}), 200
    except Exception as e:
        logger.error(f"Error in update_analysis_config: {str(e)}")
        return jsonify({'error': '数据分析过程中发生错误', 'details': str(e)}), 500


# 如果该脚本作为主程序运行，则启动Flask应用
if __name__ == '__main__':
    # 启动应用，并开启调试模式
    app.run(debug=app.config['DEBUG'])