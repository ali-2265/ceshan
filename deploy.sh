#!/bin/bash

echo "🚀 Starting deployment..."

# اضافه کردن همه فایل‌ها
git add .

# ثبت تغییرات
git commit -m "fix: remove cryptg and add runtime.txt"

# ارسال به گیت‌هاب
git push

echo "✅ Deployment completed!"
