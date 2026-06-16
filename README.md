# Telegram Helper Tool

Telegram 辅助工具，支持群发消息、自动回复、群成员扫描和多账号管理。

## 功能

- **多账号管理**: 添加和管理多个 Telegram 账号
- **群发消息**: 向多个用户批量发送消息
- **自动回复**: 根据关键词自动回复消息
- **群成员扫描**: 扫描群组成员并导出 CSV

## 安装

```bash
conda create -n tel-helper python=3.12
conda activate tel-helper
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件：

```
SECRET_KEY=your-secret-key
API_ID=your-api-id
API_HASH=your-api-hash
```

获取 API ID 和 Hash: https://my.telegram.org

## 运行

```bash
python app.py
```

访问 http://localhost:5000

## 测试

```bash
pytest tests/ -v
```
