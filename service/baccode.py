# 上传正则
# @app.route('/update_regex', methods=['POST'])
# def update_regex():
#     regex_list = request.json
#     if not regex_list:
#         return jsonify({'error': '未提供正则表达式模式'}), 400

#     try:
#         app.logger.info("开始更新正则表达式处理")
#         source_df = get_data('excel_data', -1, source_engine)
#         app.logger.info(f"获取源数据,形状: {source_df.shape}")

#         def process_text(text):
#             if not isinstance(text, str):
#                 text = str(text)
#             for regex in regex_list:
#                 text = re.sub(regex['pattern'], '', text)
#             return text_remove(text)

#         app.logger.info("开始应用文本处理")
#         for column in source_df.columns:
#             if source_df[column].dtype == 'object':
#                 app.logger.debug(f"处理列: {column}")
#                 source_df[column] = source_df[column].apply(process_text)

#         app.logger.info("保存处理后的数据到分析数据库")
#         save_to_mysql(source_df, 'analyzed_data', analyzed_engine)

#         return jsonify({
#             'success': True,
#             'message': '数据已处理并保存到分析数据库'
#         }), 200
#     except Exception as e:
#         app.logger.error(f"数据分析过程中发生错误: {str(e)}")
#         app.logger.error(traceback.format_exc())
#         return jsonify({'error': '数据分析过程中发生错误', 'details': str(e)}), 500
# def get_data(table_name, limit, conTyle):
#     # 根据limit值构造查询语句
#     if limit == -1:  # -1表示获取所有数据
#         query = f"SELECT * FROM {table_name}"
#     else:
#         query = f"SELECT * FROM {table_name} LIMIT {limit}"
#     df = pd.read_sql_query(query, con=conTyle)
#     return df









    # from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# from sqlalchemy import create_engine
# import numpy as np
# from werkzeug.utils import secure_filename
# import os

# app = Flask(__name__)
# CORS(app)

# app.config['UPLOAD_FOLDER'] = 'uploads'
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# # 数据库配置
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '123456',
#     'db': 'fenxi'
# }

# # 创建 SQLAlchemy 引擎
# engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['db']}")

# # 将DataFrame保存到MySQL
# def save_to_mysql(df, table_name):
#     df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file:
#         try:
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             return jsonify({'upload_success': True, 'file_path': file_path}), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#     else:
#         return jsonify({'error': 'File upload failed'}), 500

# @app.route('/process', methods=['POST'])
# def process_file():
#     file_path = request.json.get('file_path')
#     if not file_path:
#         return jsonify({'error': 'No file path provided'}), 400
    
#     try:
#         df = pd.read_excel(file_path)
#         table_name = 'excel_data'
#         save_to_mysql(df, table_name)
#         os.remove(file_path)
#         return jsonify({'parse_success': True, 'message': 'File successfully parsed and saved to MySQL'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/get-data', methods=['GET'])
# def get_data():
#     try:
#         limit = request.args.get('limit', 500, type=int)
#         table_name = 'excel_data'
        
#         if limit == -1:  # -1 represents all data
#             query = f"SELECT * FROM {table_name}"
#         else:
#             query = f"SELECT * FROM {table_name} LIMIT {limit}"
        
#         df = pd.read_sql_query(query, con=engine)

#         for col in df.select_dtypes(include=[np.int64]).columns:
#             df[col] = df[col].astype(int)

#         data = df.to_dict(orient='records')
        
#         total = len(data)  # Use the actual number of returned rows
#         columns = df.columns.tolist()

#         return jsonify({
#             'data': data,
#             'total': total,
#             'columns': columns
#         })
#     except Exception as e:
#         app.logger.error(f"Unexpected error: {str(e)}")
#         return jsonify({'error': 'An unexpected error occurred'}), 500



# if __name__ == '__main__':
#     app.run(debug=True)
# app_run.py

# 从源数据库获取DataFrame
# def get_data(table_name, limit, conTyle):
#     try:
#         app.logger.info(f"尝试查询表 {table_name},限制为 {limit}")
#         if limit == -1:
#             query = f"SELECT * FROM {table_name}"
#         else:
#             query = f"SELECT * FROM {table_name} LIMIT {limit}"
#         app.logger.debug(f"执行SQL查询: {query}")
#         df = pd.read_sql_query(query, con=conTyle)
#         app.logger.info(f"查询成功,返回 {len(df)} 行")
#         return df
#     except Exception as e:
#         app.logger.error(f"get_data 函数中发生错误: {str(e)}")
#         app.logger.error(traceback.format_exc())
#         raise