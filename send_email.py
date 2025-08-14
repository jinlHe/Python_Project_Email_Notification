#!/usr/bin/env python3
"""
邮件通知模块

提供程序运行完成或失败时的邮件通知功能。
支持成功和失败两种状态的邮件发送。

使用方法:
    # 命令行使用
    python send_email.py "程序名称" "SUCCESS" "额外信息"
    python send_email.py "程序名称" "FAILURE" "错误信息"
    
    # 作为模块导入
    from send_email import EmailNotifier
    notifier = EmailNotifier()
    notifier.send_notification("程序名称", "SUCCESS", "运行时间: 10分钟")
"""

import smtplib
import os
import sys
import socket
from datetime import datetime
from email.message import EmailMessage
from typing import Optional


class EmailNotifier:
    """邮件通知器类"""
    
    def __init__(
        self, 
        sender_email: str = "xxxx@qq.com",
        recipient_email: str = "xxxxx@std.uestc.edu.cn",
        smtp_server: str = "smtp.qq.com",
        smtp_port: int = 465
    ):
        """
        初始化邮件通知器
        
        Args:
            sender_email: 发送者邮箱
            recipient_email: 接收者邮箱
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
        """
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_password = os.environ.get('EMAIL_APP_PASSWORD')
        
        if not self.sender_password:
            raise ValueError("环境变量 EMAIL_APP_PASSWORD 未设置")
    
    def _get_system_info(self) -> dict:
        """获取系统信息"""
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "未知主机"
            
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'hostname': hostname,
            'current_time': current_time
        }
    
    def _create_email_content(
        self, 
        program_name: str, 
        status: str, 
        extra_info: str = ""
    ) -> tuple[str, str]:
        """
        创建邮件内容
        
        Args:
            program_name: 程序名称
            status: 运行状态 (SUCCESS/FAILURE)
            extra_info: 额外信息
            
        Returns:
            (邮件主题, 邮件正文)
        """
        system_info = self._get_system_info()
        
        if status.upper() == 'SUCCESS':
            subject = f"✅ 程序 {program_name} 运行完成"
            body = f"""程序 '{program_name}' 已成功运行结束。

📊 运行信息:
{extra_info}

🖥️  系统信息:
运行时间: {system_info['current_time']}
主机名称: {system_info['hostname']}

此邮件由自动化脚本发送。"""
        else:
            subject = f"❌ 程序 {program_name} 运行失败"
            body = f"""程序 '{program_name}' 在运行时发生错误。

❌ 错误信息:
{extra_info}

🖥️  系统信息:
运行时间: {system_info['current_time']}
主机名称: {system_info['hostname']}

请检查程序日志以获取更多详细信息。

此邮件由自动化脚本发送。"""
        
        return subject, body
    
    def send_notification(
        self, 
        program_name: str, 
        status: str, 
        extra_info: str = ""
    ) -> bool:
        """
        发送邮件通知
        
        Args:
            program_name: 程序名称
            status: 运行状态 (SUCCESS/FAILURE)
            extra_info: 额外信息
            
        Returns:
            发送成功返回 True，失败返回 False
            
        Raises:
            Exception: 邮件发送失败时抛出异常
        """
        try:
            # 创建邮件内容
            subject, body = self._create_email_content(program_name, status, extra_info)
            
            # 创建邮件对象
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg.set_content(body)
            
            # 发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp_server:
                smtp_server.login(self.sender_email, self.sender_password)
                result = smtp_server.send_message(msg)
                
                # 检查发送结果 - 空字典表示所有收件人都成功
                if not result:
                    return True
                else:
                    raise Exception(f"部分收件人发送失败: {result}")
                    
        except smtplib.SMTPResponseException as e:
            # 检查是否是QUIT阶段的错误（邮件已发送成功）
            if e.smtp_code == -1 and hasattr(e, 'smtp_error') and b'\x00\x00\x00' in e.smtp_error:
                return True  # 忽略QUIT阶段的连接关闭错误
            else:
                raise Exception(f"SMTP错误: {e}")
        except Exception as e:
            raise Exception(f"邮件发送失败: {e}")


def main():
    """主函数 - 用于命令行调用"""
    if len(sys.argv) < 3:
        print("使用方法: python send_email.py <程序名称> <状态> [额外信息]")
        print("状态: SUCCESS 或 FAILURE")
        sys.exit(1)
    
    program_name = sys.argv[1]
    status = sys.argv[2].upper()
    extra_info = sys.argv[3] if len(sys.argv) > 3 else ""
    
    try:
        notifier = EmailNotifier()
        success = notifier.send_notification(program_name, status, extra_info)
        
        if success:
            print("邮件发送成功！")
        else:
            print("邮件发送失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"邮件发送失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
