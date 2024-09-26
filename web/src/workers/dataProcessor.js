self.onmessage = function(e) {
  if (e.data.type === 'process') {
    const { data, config } = e.data;
    
    // 模拟数据处理过程
    const totalItems = data.length;
    for (let i = 0; i < totalItems; i++) {
      // 处理每一项数据
      // ...

      // 更新进度
      const progress = Math.round((i + 1) / totalItems * 100);
      self.postMessage({ type: 'progress', value: progress });
    }

    // 发送处理结果
    self.postMessage({ type: 'result', value: data });
  }
}
