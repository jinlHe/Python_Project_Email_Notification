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
from typing import List, Optional, Tuple
from datetime import datetime
import shlex

from send_email import EmailNotifier


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="运行程序并在完成后发送邮件通知",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s "python main.py"
  %(prog)s "python train.py --epochs 100" --name "模型训练"
  %(prog)s "pip install -r requirements.txt" --name "依赖安装"
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
    运行命令并返回结果
    
    Args:
        command: 要执行的命令列表
        timeout: 超时时间（秒）
        
    Returns:
        (退出码, 标准输出, 标准错误, 运行时间)
    """
    start_time = time.time()
    
    try:
        print(f"开始执行命令: {' '.join(command)}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # 使用 subprocess.run 执行命令
        result = subprocess.run(
            command,
            capture_output=False,  # 让输出实时显示
            text=True,
            timeout=timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 50)
        print(f"命令执行完成")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行时间: {duration:.2f} 秒")
        print(f"退出码: {result.returncode}")
        
        return result.returncode, "", "", duration
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        duration = end_time - start_time
        error_msg = f"命令执行超时（{timeout}秒）"
        print(f"错误: {error_msg}")
        return 124, "", error_msg, duration  # 124 是常见的超时退出码
        
    except FileNotFoundError:
        end_time = time.time()
        duration = end_time - start_time
        error_msg = f"找不到命令: {command[0]}"
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
            
            if exit_code == 0:
                # 成功
                extra_info = f"运行时间: {format_duration(duration)}"
                notifier.send_notification(program_name, "SUCCESS", extra_info)
                print("✅ 邮件通知发送成功")
            else:
                # 失败
                extra_info = f"退出码: {exit_code}\n运行时间: {format_duration(duration)}"
                if stderr:
                    extra_info += f"\n错误信息: {stderr}"
                notifier.send_notification(program_name, "FAILURE", extra_info)
                print("📧 邮件通知发送成功")
                
        except Exception as e:
            print(f"⚠️  邮件发送失败: {e}")
    
    # 退出程序，保持原始退出码
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
