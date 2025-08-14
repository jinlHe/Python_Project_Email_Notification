#!/bin/bash

MAIN_PROGRAM_CMD="python test.py"


NOTIFY_SCRIPT_PATH="send_email.py"
PROGRAM_NAME="模型训练/测试结束"
export EMAIL_APP_PASSWORD='xxxxxxxxxx'
echo "开始时间: $(date)"
$MAIN_PROGRAM_CMD
EXIT_CODE=$?
echo "程序运行结束，退出码: $EXIT_CODE"
echo "结束时间: $(date)"

if [ $EXIT_CODE -eq 0 ]; then
  echo "程序成功，发送通知邮件..."
  python3 "$NOTIFY_SCRIPT_PATH" "$PROGRAM_NAME" "SUCCESS"
else
  echo "程序失败，发送通知邮件..."
  python3 "$NOTIFY_SCRIPT_PATH" "$PROGRAM_NAME" "FAILURE" "退出码: $EXIT_CODE"
fi

unset EMAIL_APP_PASSWORD
