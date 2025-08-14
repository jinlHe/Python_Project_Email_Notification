# 邮件通知脚本使用说明

这是一个用于运行程序并在完成后发送邮件通知的工具集。

## 文件说明

- `run_with_notification.py` - 主要的运行脚本，支持命令行参数
- `send_email.py` - 邮件发送模块，可独立使用或作为模块导入
- `send_email.sh` - 原有的 shell 脚本（保持兼容性）
- `example_usage.py` - 使用示例脚本

## 环境准备

### 1. 设置环境变量

```bash
# Windows PowerShell
$env:EMAIL_APP_PASSWORD = "your_qq_mail_app_password"

# Windows CMD
set EMAIL_APP_PASSWORD=your_qq_mail_app_password

# Linux/Mac
export EMAIL_APP_PASSWORD=your_qq_mail_app_password
```

### 2. 修改邮箱配置（可选）

如需修改发送者或接收者邮箱，请编辑 `send_email.py` 中的默认值：

```python
notifier = EmailNotifier(
    sender_email="your_email@qq.com",
    recipient_email="recipient@example.com"
)
```

## 使用方法

### 方法一：使用新的 Python 脚本（推荐）

```bash
# 基本使用 - 运行 Python 脚本
python run_with_notification.py "python main.py"

# 带自定义名称
python run_with_notification.py "python train.py --epochs 100" --name "模型训练"

# 不使用引号的方式
python run_with_notification.py --command python main.py --name "主程序"

# 设置超时时间（60秒）
python run_with_notification.py "python long_running_script.py" --timeout 60

# 只运行程序，不发送邮件
python run_with_notification.py "python main.py" --no-email

# 运行其他类型的命令
python run_with_notification.py "pip install -r requirements.txt" --name "依赖安装"
python run_with_notification.py "jupyter notebook" --name "启动Jupyter"
```

### 方法二：直接使用邮件模块

```python
from send_email import EmailNotifier

# 创建通知器
notifier = EmailNotifier()

# 发送成功通知
notifier.send_notification("我的程序", "SUCCESS", "运行时间: 10分钟")

# 发送失败通知
notifier.send_notification("我的程序", "FAILURE", "错误码: 1\n内存不足")
```

### 方法三：命令行直接调用邮件脚本

```bash
python send_email.py "程序名称" "SUCCESS" "额外信息"
python send_email.py "程序名称" "FAILURE" "错误信息"
```

### 方法四：使用原有的 shell 脚本

修改 `send_email.sh` 中的 `MAIN_PROGRAM_CMD` 变量，然后运行：

```bash
bash send_email.sh
```

## 使用示例

### 示例 1：运行训练脚本

```bash
# 设置环境变量
export EMAIL_APP_PASSWORD='your_app_password'

# 运行训练脚本并在完成后发送邮件
python run_with_notification.py "python train_model.py --epochs 50 --batch-size 32" --name "深度学习模型训练"
```

### 示例 2：运行数据处理任务

```bash
python run_with_notification.py "python process_data.py --input data.csv --output results.csv" --name "数据处理任务"
```

### 示例 3：测试成功和失败的情况

```bash
# 测试成功情况
python run_with_notification.py "python example_usage.py" --name "测试程序-成功"

# 测试失败情况
python run_with_notification.py "python example_usage.py fail" --name "测试程序-失败"
```

## 功能特性

### ✨ 新脚本的优势

1. **灵活的命令输入**：支持引号包围的完整命令或分割的参数列表
2. **自定义程序名称**：可以为邮件标题指定更友好的名称
3. **超时控制**：可以设置程序运行的最大时间
4. **实时输出**：程序的输出会实时显示在终端
5. **详细的时间统计**：自动计算并报告程序运行时间
6. **美化的邮件格式**：使用表情符号和结构化的邮件内容
7. **模块化设计**：可以作为模块导入到其他 Python 项目中

### 📧 邮件内容

成功邮件示例：
```
主题: ✅ 程序 模型训练 运行完成

程序 '模型训练' 已成功运行结束。

📊 运行信息:
运行时间: 2 小时 15 分 30.5 秒

🖥️ 系统信息:
运行时间: 2024-01-15 14:30:45
主机名称: DESKTOP-ABC123

此邮件由自动化脚本发送。
```

失败邮件示例：
```
主题: ❌ 程序 模型训练 运行失败

程序 '模型训练' 在运行时发生错误。

❌ 错误信息:
退出码: 1
运行时间: 5 分 12.3 秒
错误信息: CUDA out of memory

🖥️ 系统信息:
运行时间: 2024-01-15 14:30:45
主机名称: DESKTOP-ABC123

请检查程序日志以获取更多详细信息。

此邮件由自动化脚本发送。
```

## 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查 `EMAIL_APP_PASSWORD` 环境变量是否正确设置
   - 确认QQ邮箱已开启SMTP服务并获取了应用密码
   - 检查网络连接

2. **命令解析失败**
   - 使用引号包围包含空格的命令
   - 或者使用 `--command` 参数避免解析问题

3. **权限问题**
   - 确保Python脚本有执行权限
   - Windows用户可能需要使用 `python` 而不是 `python3`

### 调试技巧

```bash
# 使用 --no-email 参数测试程序运行
python run_with_notification.py "python your_script.py" --no-email

# 查看详细的错误信息
python run_with_notification.py "python your_script.py" --name "测试" 2>&1 | tee log.txt
```

## 自定义配置

如需修改邮箱配置，可以创建自定义的通知器：

```python
from send_email import EmailNotifier

# 使用自定义配置
custom_notifier = EmailNotifier(
    sender_email="your_custom_email@gmail.com",
    recipient_email="recipient@example.com",
    smtp_server="smtp.gmail.com",
    smtp_port=587  # Gmail 使用 587 端口
)

custom_notifier.send_notification("自定义任务", "SUCCESS", "任务完成")
```
