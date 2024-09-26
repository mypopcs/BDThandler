
# 导入所需的模块
import re
import logging
import numpy as np  # 科学计算工具
import pandas as pd  # 数据分析工具
from sqlalchemy import create_engine, inspect
from config import DevelopmentConfig # 导入数据库配置
from flask import Flask, request, jsonify, Response  # Flask框架相关
from flask_cors import CORS  # 解决跨域资源共享问题
from analysis import text_remove # 导入text_remove函数

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__) # 创建Flask应用实例
app.config.from_object(DevelopmentConfig) # 加载配置文件中的配置
CORS(app)  # 允许跨域请求

# 数据库引擎设置
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# 全局变量存储正则表达式列表
# regex_list = []
analysis_config = {
    'regex_list': [],
    'synonyms': [],
    'stopwords': []
}

# 保存数据至数据库
def save_to_mysql(df, table_name, conTyle):
    df.to_sql(table_name, con=conTyle, if_exists='replace', index=False) # 保存数据至数据库，如果指定的表已存在，则删除旧表并创建新表

# 获取数据函数
def get_data(table_name, limit, conTyle): # conTyle参数是有效的数据库连接对象
    try:
        inspector = inspect(conTyle) # inspect用于检查数据库连接对象的源数据，例如检查表是否存在
        if not inspector.has_table(table_name):
            return pd.DataFrame() # 如果表不存在，函数返回一个空的DataFrame
        # 根据传入limit查询字符串，-1为所有记录
        query = f"SELECT * FROM {table_name}" if limit == -1 else f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql_query(query, con=conTyle) # 使用read_sql_query函数查询，将结果作为DataFrame返回
        return df
    except Exception as e:
        return pd.DataFrame() # 捕获任何异常，返回一个空的DataFrame
# 获取数据
def get_data_common(query_type, engine):
    try:
        limit = request.args.get('limit', default=500, type=int) # 获取请求中的limit参数，默认值为500
        engine.connect() # 测试数据库连接
        df = get_data(query_type, limit, engine) # 执行查询
        if df.empty:
            return jsonify({
                'data': [],
                'total': 0,
                'columns': []
            }),200
        # 数据处理
        for col in df.select_dtypes(include=[np.int64]).columns: 
            df[col] = df[col].astype(int) # 将int64类型的数据转换为int类型，以便JSON序列化
        data = df.to_dict(orient='records') # 将DataFrame转换为字典列表
        total = len(data) # 获取数据总行数，使用实际返回行数
        columns = df.columns.tolist() # 获取列名列表
        return jsonify({
            'data': data,
            'total': total,
            'columns': columns
        })
    except Exception as e:
        return jsonify({'error': '获取{query_type}数据时发生错误', 'details': str(e)}), 500
    
def clean_data(df, text_column):
    df = df.dropna(subset=[text_column])
    return df.drop_duplicates()

# 定义文本匹配函数
def process_text(df, text_column, config):
    def process_entry(text):
        if not isinstance(text, str): # 确保传入为字符串类型
            text = str(text)
        text = text_remove(text) # 文本清理
        # 遍历regex_list中的每个正则表达式 
        for regex in config['regex_list']:
            text = re.sub(regex['regex'], '', text) # 使用re.sub函数将匹配到的文本替换为空字符串
        words = text.split()
        # 同义词替换
        words = [config['synonyms'].get(word, word) for word in words]
        # 停用词过滤
        words = [word for word in words if word not in config['stopwords'] and len(word) > 1]
        # 重新组合文本
        processed_text = " ".join(words)
        return text, processed_text

    df['源文本'], df[text_column] = zip(*df[text_column].apply(process_entry))
    df = df[df[text_column].str.strip() != '']
    return df

# 获取分析前的数据
@app.route('/get_source_data', methods=['GET'])
def get_source_data():
    return get_data_common('excel_data', db_engine)

# 获取分析后的数据
@app.route('/get_analyzed_data', methods=['GET'])
def get_analyzed_data():
    return get_data_common('analyzed_data', db_engine)

# 处理正则表达式
@app.route('/update_analysis_config', methods=['POST'])
def update_analysis_config():
    global analysis_config
    config_data = request.json
    # 更新正则表达式列表
    analysis_config['regex_list'] = config_data['regexList']
    # 更新同义词字典
    analysis_config['synonyms'] = {word: group['replacement'] for group in config_data['synonyms'] for word in group['words']}
    # 更新停用词列表
    analysis_config['stopwords'] = set(config_data['stopwords'])
    logger.info(f"接收到的数据: {config_data}")
    logger.info(f"正则数据: {analysis_config['regex_list']}")
    logger.info(f"同义词数据: {analysis_config['synonyms']}")
    logger.info(f"停用词数据数据: {analysis_config['stopwords']}")
    # 执行函数
    try:
        source_data = get_data('excel_data', -1, db_engine) # 获取待分析的所有数据
        source_data = clean_data(source_data, '评论内容')  # 假设文本列名为'text_column'
        processed_data = process_text(source_data, '评论内容', analysis_config)
        save_to_mysql(processed_data, 'analyzed_data', db_engine)
        return jsonify({
            'success': True,
            'message': '数据已处理并保存到分析数据库'
        }), 200
    except Exception as e:
        logger.error(f"Error in update_analysis_config: {str(e)}")
        return jsonify({'error': '数据分析过程中发生错误', 'details': str(e)}), 500


# 如果该脚本作为主程序运行，则启动Flask应用
if __name__ == '__main__':
    # 启动应用，并开启调试模式
    app.run(debug=app.config['DEBUG'])