#!/usr/bin/env python3
"""
使用示例脚本

演示如何使用 run_with_notification.py 来运行程序并发送邮件通知
"""

import time
import sys
import random

def main():
    """模拟一个需要运行的程序"""
    print("程序开始运行...")
    
    # 模拟一些工作
    for i in range(5):
        print(f"处理步骤 {i+1}/5...")
        time.sleep(1)  # 模拟耗时操作
    
    # 随机决定成功或失败（用于测试）
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        print("模拟程序失败...")
        raise RuntimeError("这是一个模拟的错误")
    
    print("程序成功完成！")

if __name__ == "__main__":
    main()
