#!/usr/bin/env python3
"""LINE 機器人配置"""

# LINE Webhook 配置
LINE_WEBHOOK_URL = "https://api.line.me/v2/bot/message/push"
LINE_CHANNEL_ID = "your_channel_id"  # 從 LINE Developer Console 取得
LINE_CHANNEL_SECRET = "your_channel_secret"  # 從 LINE Developer Console 取得

# 驗證 Token
VERIFICATION_TOKEN = "your_verification_token"  # 從 LINE Developer Console 取得

# 認證端點
LINE_AUTH_URL = "https://api.line.me/oauth2/v2.1/token"

# 社區用戶資料
COMMUNITY_USERS = {
    "resident_001": {
        "name": "張媽媽",
        "line_id": "UXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "unit": "101",
        "notification": "all"
    },
    "resident_002": {
        "name": "李伯伯",
        "line_id": "UXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "unit": "205",
        "notification": "all"
    },
    "resident_003": {
        "name": "王阿姨",
        "line_id": "UXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "unit": "308",
        "notification": "emergency"
    }
}

# 通知模板
NOTIFICATION_TEMPLATES = {
    "meeting_notification": {
        "type": "text",
        "template": {
            "altText": "社區會議通知",
            "contents": {
                "text": "📋 社區會議通知\n\n📅 日期：{date}\n🕐 時間：{time}\n📍 地點：社區活动中心\n👥 主持人：{host}\n\n請準時出席！"
            }
        }
    },
    "meeting_summary": {
        "type": "text",
        "template": {
            "altText": "會議記錄通知",
            "contents": {
                "text": "📝 會議記錄已生成\n\n📋 {meeting_id}\n📅 {date}\n\n會議記錄已存檔"
            }
        }
    },
    "emergency_alert": {
        "type": "text",
        "template": {
            "altText": "緊急通知",
            "contents": {
                "text": "🚨 緊急通知\n\n{title}\n\n{content}\n\n請立即處理！"
            }
        }
    },
    "maintenance_notification": {
        "type": "text",
        "template": {
            "altText": "維修通知",
            "contents": {
                "text": "🔧 維修通知\n\n📝 項目：{item}\n🕐 時間：{time}\n📍 地點：{location}\n\n請配合施工！"
            }
        }
    },
    "announcement": {
        "type": "text",
        "template": {
            "altText": "社區公告",
            "contents": {
                "text": "📢 社區公告\n\n{title}\n\n{content}\n\n請留意相關事項！"
            }
        }
    }
}

# 用戶管理
class UserManager:
    """用戶管理"""
    
    @staticmethod
    def get_user(sender_id):
        """獲取用戶資料"""
        return COMMUNITY_USERS.get(sender_id)
    
    @staticmethod
    def is_registered(sender_id):
        """檢查用戶是否已註冊"""
        return sender_id in COMMUNITY_USERS
    
    @staticmethod
    def get_notification_type(user):
        """獲取用戶通知類型"""
        if user:
            return user.get('notification', 'all')
        return 'all'
    
    @staticmethod
    def get_all_users():
        """獲取所有用戶"""
        return COMMUNITY_USERS.copy()
