import numpy as np  # 科学计算工具
import pandas as pd  # 数据分析工具
from sqlalchemy import inspect
from flask import request, jsonify  # Flask框架相关
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