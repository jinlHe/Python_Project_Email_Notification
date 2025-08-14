# 邮件通知脚本使用说明

这是一个用于运行程序并在完成后发送邮件通知的工具集，包括python、linux命令行都可以通知。

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

### 2. 修改邮箱配置\

修改发送者和接收者邮箱，直接编辑 `send_email.py` 中的默认值：

```python
class EmailNotifier:
    """邮件通知器类"""
    
    def __init__(
        self, 
        sender_email: str = "xxxxx@qq.com",
        recipient_email: str = "xxxxx@std.uestc.edu.cn",
        smtp_server: str = "smtp.qq.com",
        smtp_port: int = 465
    ):
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

# Linux/系统命令
python run_with_notification.py "ls -la" --name "文件列表"
python run_with_notification.py "git clone https://github.com/user/repo.git" --name "代码克隆"
python run_with_notification.py "docker build -t myapp ." --name "Docker构建"
python run_with_notification.py "make && make install" --name "编译安装"

# Hugging Face 相关命令
python run_with_notification.py "huggingface-cli upload dataset" --name "HF数据集上传"
python run_with_notification.py "transformers-cli download bert-base-uncased" --name "模型下载"
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

## Linux/系统命令支持

### 🚀 新功能亮点

从此版本开始，`run_with_notification.py` 不仅支持Python程序，还全面支持Linux系统命令、shell脚本和其他可执行程序！

### 🔧 支持的命令类型

1. **Python 相关命令**
   - `python`, `pip`, `conda`, `poetry`, `pytest` 等

2. **系统管理命令**
   - `ls`, `cp`, `mv`, `chmod`, `ps`, `top` 等

3. **开发工具命令**
   - `git`, `docker`, `make`, `gcc`, `npm`, `yarn` 等

4. **网络工具命令**
   - `wget`, `curl`, `ping` 等

5. **复杂Shell命令**
   - 支持管道 `|`、重定向 `>`、命令链 `&&`、`||` 等

### 💡 Linux命令使用示例

#### 基础系统命令
```bash
# 查看文件列表
python run_with_notification.py "ls -la /home/user/" --name "文件列表"

# 查看系统信息
python run_with_notification.py "uname -a" --name "系统信息"

# 查看磁盘使用情况
python run_with_notification.py "df -h" --name "磁盘空间"

# 查看进程
python run_with_notification.py "ps aux | head -20" --name "进程列表"
```

#### Git 操作
```bash
# 克隆仓库
python run_with_notification.py "git clone https://github.com/user/repo.git" --name "代码克隆"

# 拉取更新
python run_with_notification.py "git pull origin main" --name "代码更新"

# 推送代码
python run_with_notification.py "git push origin feature-branch" --name "代码推送"
```

#### Docker 操作
```bash
# 构建镜像
python run_with_notification.py "docker build -t myapp:latest ." --name "Docker构建"

# 运行容器
python run_with_notification.py "docker run -d --name myapp-container myapp:latest" --name "容器启动"

# 清理无用镜像
python run_with_notification.py "docker system prune -f" --name "Docker清理"
```

#### 编译和构建
```bash
# Make 构建
python run_with_notification.py "make clean && make all" --name "项目编译"

# 安装软件包
python run_with_notification.py "sudo apt update && sudo apt install -y htop" --name "软件安装"

# 配置和编译
python run_with_notification.py "./configure && make && make install" --name "源码安装"
```

#### 数据处理和下载
```bash
# 下载文件
python run_with_notification.py "wget https://example.com/large-file.zip" --name "文件下载"

# 解压文件
python run_with_notification.py "tar -xzf archive.tar.gz" --name "文件解压"

# 数据同步
python run_with_notification.py "rsync -av /source/ /destination/" --name "数据同步"
```

#### Hugging Face 相关
```bash
# 上传数据集
python run_with_notification.py "huggingface-cli upload dataset-name ./data" --name "HF数据集上传"

# 下载模型
python run_with_notification.py "git lfs clone https://huggingface.co/model-name" --name "HF模型下载"

# 推送模型
python run_with_notification.py "git lfs push origin main" --name "HF模型推送"
```

### 🔀 跨平台支持

该脚本自动检测操作系统并适配相应的shell环境：

- **Linux/Mac**: 使用 `bash` 执行复杂命令
- **Windows**: 使用 `cmd` 执行复杂命令
- **自动检测**: 无需手动配置，自动适配

### ⚡ 高级功能

#### 实时输出监控
```bash
# 长时间运行的命令会实时显示输出
python run_with_notification.py "docker build -t large-image ." --name "大镜像构建"
```

#### 超时控制
```bash
# 设置5分钟超时
python run_with_notification.py "long-running-process" --timeout 300 --name "长进程"
```

#### 错误处理
```bash
# 即使命令失败也会发送通知，包含错误信息
python run_with_notification.py "make test" --name "运行测试"
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

### 示例 3：运行Linux系统命令

```bash
# 系统管理
python run_with_notification.py "df -h && free -h" --name "系统资源检查"

# Git操作
python run_with_notification.py "git pull && git status" --name "代码同步"

# 文件操作
python run_with_notification.py "find . -name '*.py' | wc -l" --name "Python文件统计"
```

### 示例 4：测试成功和失败的情况

```bash
# 测试成功情况
python run_with_notification.py "python example_usage.py" --name "测试程序-成功"

# 测试失败情况
python run_with_notification.py "python example_usage.py fail" --name "测试程序-失败"

# 测试Linux命令
python run_with_notification.py "echo 'Hello Linux!'" --name "Linux命令测试"
```

## 功能特性

### ✨ 新脚本的优势

1. **全面的命令支持**：支持Python程序、Linux系统命令、Shell脚本等
2. **智能命令识别**：自动检测命令类型（Python/系统/Shell）
3. **跨平台兼容**：自动适配Windows、Linux、Mac操作系统
4. **复杂命令支持**：支持管道、重定向、命令链等复杂Shell操作
5. **实时输出监控**：同时提供实时显示和完整输出捕获
6. **灵活的命令输入**：支持引号包围的完整命令或分割的参数列表
7. **自定义程序名称**：可以为邮件标题指定更友好的名称
8. **超时控制**：可以设置程序运行的最大时间
9. **详细的时间统计**：自动计算并报告程序运行时间
10. **智能邮件内容**：根据命令类型和输出自动生成结构化邮件
11. **错误信息包含**：失败时自动包含错误输出和诊断信息
12. **模块化设计**：可以作为模块导入到其他 Python 项目中

### 📧 邮件内容

成功邮件示例（Python程序）：
```
主题: ✅ 程序 模型训练 运行完成

程序 '模型训练' 已成功运行结束。

📊 运行信息:
命令类型: Python程序
运行时间: 2 小时 15 分 30.5 秒

输出摘要 (前5行):
Epoch 1/100: loss=0.856, accuracy=0.623
Epoch 2/100: loss=0.743, accuracy=0.689
...
Model saved to checkpoint.pth
Training completed successfully!

🖥️ 系统信息:
运行时间: 2024-01-15 14:30:45
主机名称: DESKTOP-ABC123

此邮件由自动化脚本发送。
```

成功邮件示例（Linux命令）：
```
主题: ✅ 程序 Docker构建 运行完成

程序 'Docker构建' 已成功运行结束。

📊 运行信息:
命令类型: 系统命令
运行时间: 3 分 42.1 秒

输出内容:
Successfully built abc123def456
Successfully tagged myapp:latest
Image size: 1.2GB

🖥️ 系统信息:
运行时间: 2024-01-15 14:30:45
主机名称: ubuntu-server

此邮件由自动化脚本发送。
```

失败邮件示例：
```
主题: ❌ 程序 模型训练 运行失败

程序 '模型训练' 在运行时发生错误。

❌ 错误信息:
命令类型: Python程序
退出码: 1
运行时间: 5 分 12.3 秒

错误输出 (最后5行):
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
  File "train.py", line 45, in forward
    output = self.model(input_data)
Process finished with exit code 1

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
## 注
该代码99.9%都由AI生成，因为其功能较为实用（至少对我本人），因此发布出来，希望能帮到部分人群（至少节省一点Prompt自己编写的时间）

