#!/usr/bin/env python3
"""
运行程序并发送邮件通知脚本

使用方法:
    python run_with_notification.py "python main.py"
    python run_with_notification.py "python train.py --epochs 100"
    python run_with_notification.py "pip install -r requirements.txt"
    
环境变量:
    EMAIL_APP_PASSWORD: QQ邮箱的应用密码
"""

import subprocess
import sys
import os
import time
import argparse
import platform
import threading
from typing import List, Optional, Tuple, Union
from datetime import datetime
import shlex
from queue import Queue, Empty

from send_email import EmailNotifier


def detect_command_type(command: List[str]) -> str:
    """
    检测命令类型
    
    Args:
        command: 命令列表
        
    Returns:
        命令类型: 'python', 'shell', 'system'
    """
    if not command:
        return 'shell'
    
    first_cmd = command[0].lower()
    
    # Python相关命令
    python_commands = {
        'python', 'python3', 'python2', 'py',
        'pip', 'pip3', 'pip2',
        'conda', 'poetry', 'pipenv',
        'jupyter', 'ipython',
        'pytest', 'python-m'
    }
    
    if first_cmd in python_commands:
        return 'python'
    
    # 系统命令
    system_commands = {
        'ls', 'dir', 'cd', 'mkdir', 'rmdir', 'rm', 'del',
        'cp', 'copy', 'mv', 'move', 'chmod', 'chown',
        'ps', 'top', 'htop', 'kill', 'killall',
        'wget', 'curl', 'git', 'docker', 'docker-compose',
        'npm', 'yarn', 'node', 'make', 'cmake',
        'gcc', 'g++', 'javac', 'java',
        'tar', 'zip', 'unzip', 'gzip', 'gunzip'
    }
    
    if first_cmd in system_commands:
        return 'system'
    
    # 默认为shell命令
    return 'shell'


def get_shell_command(command: List[str]) -> List[str]:
    """
    根据操作系统获取适当的shell命令
    
    Args:
        command: 原始命令列表
        
    Returns:
        适配shell的命令列表
    """
    system = platform.system().lower()
    
    # 检查是否是复杂的shell命令（包含管道、重定向等）
    command_str = ' '.join(command)
    has_shell_operators = any(op in command_str for op in ['|', '>', '<', '&&', '||', ';', '&'])
    
    if has_shell_operators:
        if system == 'windows':
            return ['cmd', '/c', command_str]
        else:
            return ['bash', '-c', command_str]
    
    return command


def stream_output(pipe, queue: Queue, prefix: str):
    """
    实时读取进程输出并加入队列
    
    Args:
        pipe: 进程的stdout或stderr管道
        queue: 输出队列
        prefix: 输出前缀（用于区分stdout和stderr）
    """
    try:
        for line in iter(pipe.readline, ''):
            if line:
                queue.put((prefix, line.rstrip()))
        pipe.close()
    except Exception as e:
        queue.put((prefix, f"读取输出时出错: {e}"))


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="运行程序并在完成后发送邮件通知",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  Python 程序:
    %(prog)s "python main.py"
    %(prog)s "python train.py --epochs 100" --name "模型训练"
    %(prog)s "pip install -r requirements.txt" --name "依赖安装"
    
  Linux/系统命令:
    %(prog)s "ls -la" --name "文件列表"
    %(prog)s "git clone https://github.com/user/repo.git" --name "代码克隆"
    %(prog)s "docker build -t myapp ." --name "Docker构建"
    %(prog)s "make && make install" --name "编译安装"
    %(prog)s "curl -O https://example.com/file.zip" --name "文件下载"
    
  Hugging Face 相关:
    %(prog)s "huggingface-cli upload dataset" --name "HF数据集上传"
    %(prog)s "transformers-cli download bert-base-uncased" --name "模型下载"
    
  其他用法:
    %(prog)s --command python main.py --name "主程序"
        """
    )
    
    # 支持两种输入方式
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'command_string', 
        nargs='?',
        help='要执行的完整命令（用引号包围）'
    )
    group.add_argument(
        '--command',
        nargs='+',
        help='要执行的命令（可以不用引号）'
    )
    
    parser.add_argument(
        '--name', '-n',
        default=None,
        help='程序名称（用于邮件标题，默认使用命令本身）'
    )
    
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='不发送邮件通知，只运行程序'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=None,
        help='程序运行超时时间（秒）'
    )
    
    return parser.parse_args()


def run_command(
    command: List[str], 
    timeout: Optional[int] = None
) -> Tuple[int, str, str, float]:
    """
    运行命令并返回结果，支持实时输出显示和完整输出捕获
    
    Args:
        command: 要执行的命令列表
        timeout: 超时时间（秒）
        
    Returns:
        (退出码, 标准输出, 标准错误, 运行时间)
    """
    start_time = time.time()
    
    # 检测命令类型并适配shell环境
    cmd_type = detect_command_type(command)
    exec_command = get_shell_command(command)
    
    try:
        print(f"开始执行{cmd_type}命令: {' '.join(command)}")
        if exec_command != command:
            print(f"实际执行命令: {' '.join(exec_command)}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"操作系统: {platform.system()}")
        print("-" * 50)
        
        # 创建进程，同时捕获输出和显示实时输出
        process = subprocess.Popen(
            exec_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )
        
        # 创建输出队列和线程
        output_queue = Queue()
        stdout_lines = []
        stderr_lines = []
        
        # 启动输出读取线程
        stdout_thread = threading.Thread(
            target=stream_output, 
            args=(process.stdout, output_queue, 'STDOUT')
        )
        stderr_thread = threading.Thread(
            target=stream_output, 
            args=(process.stderr, output_queue, 'STDERR')
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # 实时显示输出并收集完整输出
        while True:
            try:
                # 非阻塞获取输出
                source, line = output_queue.get(timeout=0.1)
                if source == 'STDOUT':
                    print(line)
                    stdout_lines.append(line)
                elif source == 'STDERR':
                    print(f"[stderr] {line}", file=sys.stderr)
                    stderr_lines.append(line)
            except Empty:
                # 检查进程是否还在运行
                if process.poll() is not None:
                    break
                    
                # 检查超时
                if timeout and (time.time() - start_time) > timeout:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    error_msg = f"命令执行超时（{timeout}秒）"
                    print(f"\n错误: {error_msg}")
                    return 124, '\n'.join(stdout_lines), error_msg, duration
        
        # 等待线程完成
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        
        # 获取剩余输出
        while not output_queue.empty():
            try:
                source, line = output_queue.get_nowait()
                if source == 'STDOUT':
                    stdout_lines.append(line)
                elif source == 'STDERR':
                    stderr_lines.append(line)
            except Empty:
                break
        
        # 等待进程完成
        process.wait()
        
        end_time = time.time()
        duration = end_time - start_time
        
        stdout_output = '\n'.join(stdout_lines)
        stderr_output = '\n'.join(stderr_lines)
        
        print("-" * 50)
        print(f"命令执行完成")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行时间: {duration:.2f} 秒")
        print(f"退出码: {process.returncode}")
        
        if stderr_output:
            print(f"错误输出长度: {len(stderr_output)} 字符")
        if stdout_output:
            print(f"标准输出长度: {len(stdout_output)} 字符")
        
        return process.returncode, stdout_output, stderr_output, duration
        
    except FileNotFoundError:
        end_time = time.time()
        duration = end_time - start_time
        error_msg = f"找不到命令: {exec_command[0] if exec_command else 'unknown'}"
        print(f"错误: {error_msg}")
        return 127, "", error_msg, duration  # 127 是命令未找到的退出码
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        error_msg = f"执行命令时发生错误: {str(e)}"
        print(f"错误: {error_msg}")
        return 1, "", error_msg, duration


def format_duration(seconds: float) -> str:
    """格式化运行时间"""
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes} 分 {remaining_seconds:.1f} 秒"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours} 小时 {remaining_minutes} 分 {remaining_seconds:.1f} 秒"


def main():
    """主函数"""
    args = parse_arguments()
    
    # 确定要执行的命令
    if args.command_string:
        # 解析字符串形式的命令
        try:
            command = shlex.split(args.command_string)
        except ValueError as e:
            print(f"错误: 无法解析命令字符串: {e}")
            sys.exit(1)
    else:
        # 使用列表形式的命令
        command = args.command
    
    # 确定程序名称
    program_name = args.name if args.name else ' '.join(command)
    
    # 检查环境变量
    if not args.no_email:
        email_password = os.environ.get('EMAIL_APP_PASSWORD')
        if not email_password:
            print("警告: 未设置 EMAIL_APP_PASSWORD 环境变量，将不发送邮件通知")
            print("请设置环境变量或使用 --no-email 参数")
            args.no_email = True
    
    # 运行命令
    exit_code, stdout, stderr, duration = run_command(command, args.timeout)
    
    # 发送邮件通知
    if not args.no_email:
        try:
            notifier = EmailNotifier()
            
            # 检测命令类型，用于更好的邮件标题
            cmd_type = detect_command_type(command)
            cmd_type_cn = {
                'python': 'Python程序',
                'system': '系统命令',
                'shell': 'Shell命令'
            }.get(cmd_type, '程序')
            
            if exit_code == 0:
                # 成功
                extra_info = f"命令类型: {cmd_type_cn}\n运行时间: {format_duration(duration)}"
                
                # 如果有输出，添加输出摘要
                if stdout:
                    output_lines = stdout.strip().split('\n')
                    if len(output_lines) <= 10:
                        extra_info += f"\n\n输出内容:\n{stdout.strip()}"
                    else:
                        extra_info += f"\n\n输出摘要 (前5行):\n" + '\n'.join(output_lines[:5])
                        extra_info += f"\n... (共 {len(output_lines)} 行输出)"
                
                notifier.send_notification(program_name, "SUCCESS", extra_info)
                print("✅ 邮件通知发送成功")
            else:
                # 失败
                extra_info = f"命令类型: {cmd_type_cn}\n退出码: {exit_code}\n运行时间: {format_duration(duration)}"
                
                # 添加错误信息
                if stderr:
                    stderr_lines = stderr.strip().split('\n')
                    if len(stderr_lines) <= 5:
                        extra_info += f"\n\n错误输出:\n{stderr.strip()}"
                    else:
                        extra_info += f"\n\n错误输出 (最后5行):\n" + '\n'.join(stderr_lines[-5:])
                
                # 如果有标准输出，也包含一些
                if stdout:
                    stdout_lines = stdout.strip().split('\n')
                    if len(stdout_lines) <= 3:
                        extra_info += f"\n\n标准输出:\n{stdout.strip()}"
                    else:
                        extra_info += f"\n\n标准输出 (最后3行):\n" + '\n'.join(stdout_lines[-3:])
                
                notifier.send_notification(program_name, "FAILURE", extra_info)
                print("邮件通知发送成功")
                
        except Exception as e:
            print(f"⚠️  邮件发送失败: {e}")
    
    # 退出程序，保持原始退出码
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
