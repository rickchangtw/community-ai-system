#!/usr/bin/env python3
"""
Phase 8: Redis Caching Strategy
================================================================================
"""
import redis
import json
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional

# ============================================================================
# Redis Connection
# ============================================================================

class RedisCache:
    """Redis 快取實例"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def get(self, key: str) -> Optional[str]:
        """獲取快取值"""
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        """設定快取值"""
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """檢查快取是否存在"""
        return self.client.exists(key)
    
    def expire(self, key: str, seconds: int) -> bool:
        """設定快取過期時間"""
        return self.client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """獲取快取剩餘時間"""
        return self.client.ttl(key)
    
    def hset(self, name: str, key: str, value: str) -> bool:
        """設定 Hash 值"""
        return self.client.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """獲取 Hash 值"""
        return self.client.hget(name, key)
    
    def hgetall(self, name: str) -> Dict[str, str]:
        """獲取整個 Hash"""
        return self.client.hgetall(name)
    
    def hdel(self, name: str, key: str) -> int:
        """刪除 Hash 值"""
        return self.client.hdel(name, key)
    
    def sadd(self, name: str, *values: str) -> int:
        """添加 Set 值"""
        return self.client.sadd(name, *values)
    
    def srem(self, name: str, *values: str) -> int:
        """刪除 Set 值"""
        return self.client.srem(name, name, *values)
    
    def smembers(self, name: str) -> set:
        """獲取 Set 所有值"""
        return self.client.smembers(name)
    
    def lpush(self, name: str, *values: str) -> int:
        """添加到 List 前端"""
        return self.client.lpush(name, *values)
    
    def rpush(self, name: str, *values: str) -> int:
        """添加到 List 尾部"""
        return self.client.rpush(name, *values)
    
    def llen(self, name: str) -> int:
        """獲取 List 長度"""
        return self.client.llen(name)
    
    def lpop(self, name: str) -> Optional[str]:
        """從 List 前端移除"""
        return self.client.lpop(name)
    
    def keys(self, pattern: str) -> list:
        """匹配模式"""
        return self.client.keys(pattern)
    
    def flushdb(self) -> bool:
        """清空當前資料庫"""
        return self.client.flushdb()
    
    def ping(self) -> bool:
        """檢查 Redis 是否運行"""
        return self.client.ping()
    
    def info(self) -> Dict[str, Any]:
        """獲取 Redis 資訊"""
        return self.client.info()


# ============================================================================
# Caching Decorators
# ============================================================================

def cached(timeout: int = 300):
    """快取裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__module__}:{func.__name__}:{json.dumps(args, default=str)}"
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            result = func(*args, **kwargs)
            redis_client.set(cache_key, json.dumps(result, default=str), ex=timeout)
            
            return result
        return wrapper
    return decorator


# ============================================================================
# Cache Strategies
# ============================================================================

class TTLStrategy:
    """快取 TTL 策略"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
    
    def set_with_ttl(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """設定帶 TTL 的快取"""
        if ttl is None:
            ttl = self.default_ttl
        return redis_client.set(key, value, ex=ttl)
    
    def get_with_ttl(self, key: str) -> Optional[str]:
        """獲取帶 TTL 的快取"""
        data = redis_client.get(key)
        if data:
            ttl = redis_client.ttl(key)
            return {
                'data': data,
                'ttl': ttl
            }
        return None


class LRUCache:
    """LRU 快取"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
    
    def get(self, key: str) -> Optional[str]:
        """獲取快取值"""
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        return None
    
    def put(self, key: str, value: str) -> bool:
        """設定快取值"""
        if len(self.cache) >= self.max_size:
            # 刪除最舊的項目
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value
        return True
    
    def remove(self, key: str) -> bool:
        """刪除快取值"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def __len__(self) -> int:
        return len(self.cache)


# ============================================================================
# Agent Communication Cache
# ============================================================================

class AgentCommunicationCache:
    """Agent 通訊快取"""
    
    def __init__(self, redis_client: RedisCache):
        self.redis = redis_client
    
    def cache_agent_heartbeat(self, agent_id: str, status: str, timestamp: str = None) -> bool:
        """快取 Agent 心跳"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        key = f"agent:{agent_id}:heartbeat"
        return self.redis.set(key, json.dumps({
            'agent_id': agent_id,
            'status': status,
            'timestamp': timestamp
        }), ex=60)
    
    def get_agent_heartbeat(self, agent_id: str) -> Optional[Dict]:
        """獲取 Agent 心跳"""
        key = f"agent:{agent_id}:heartbeat"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def cache_event_notification(self, event_id: str, event_data: Dict) -> bool:
        """快取事件通知"""
        key = f"event:{event_id}:notification"
        return self.redis.set(key, json.dumps(event_data), ex=300)
    
    def get_event_notification(self, event_id: str) -> Optional[Dict]:
        """獲取事件通知"""
        key = f"event:{event_id}:notification"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def cache_notice_delivery(self, notice_id: str, delivery_data: Dict) -> bool:
        """快取通知送達"""
        key = f"notice:{notice_id}:delivery"
        return self.redis.set(key, json.dumps(delivery_data), ex=600)
    
    def get_notice_delivery(self, notice_id: str) -> Optional[Dict]:
        """獲取通知送達"""
        key = f"notice:{notice_id}:delivery"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None


# ============================================================================
# Community Data Cache
# ============================================================================

class CommunityDataCache:
    """社區資料快取"""
    
    def __init__(self, redis_client: RedisCache):
        self.redis = redis_client
    
    def cache_community_info(self, community_id: str, community_data: Dict) -> bool:
        """快取社區資訊"""
        key = f"community:{community_id}:info"
        return self.redis.set(key, json.dumps(community_data), ex=3600)
    
    def get_community_info(self, community_id: str) -> Optional[Dict]:
        """獲取社區資訊"""
        key = f"community:{community_id}:info"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def cache_building_info(self, building_id: str, building_data: Dict) -> bool:
        """快取大樓資訊"""
        key = f"building:{building_id}:info"
        return self.redis.set(key, json.dumps(building_data), ex=1800)
    
    def get_building_info(self, building_id: str) -> Optional[Dict]:
        """獲取大樓資訊"""
        key = f"building:{building_id}:info"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def cache_resident_info(self, resident_id: str, resident_data: Dict) -> bool:
        """快取住戶資訊"""
        key = f"resident:{resident_id}:info"
        return self.redis.set(key, json.dumps(resident_data), ex=3600)
    
    def get_resident_info(self, resident_id: str) -> Optional[Dict]:
        """獲取住戶資訊"""
        key = f"resident:{resident_id}:info"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None


# ============================================================================
# Performance Monitoring
# ============================================================================

class PerformanceMonitor:
    """性能監控"""
    
    def __init__(self, redis_client: RedisCache):
        self.redis = redis_client
    
    def record_query_time(self, query_name: str, time_ms: float) -> bool:
        """記錄查詢時間"""
        key = f"perf:query:{query_name}"
        pipe = self.redis.client.pipeline()
        pipe.hset(key, 'count', self.redis.client.hget(key, 'count') or '0')
        pipe.hincrby(key, 'total_time', time_ms)
        pipe.hset(key, 'last_time', str(time_ms))
        pipe.hset(key, 'avg_time', str((self.redis.client.hget(key, 'total_time') or '0') + time_ms))
        pipe.execute()
        return True
    
    def get_query_stats(self, query_name: str) -> Optional[Dict]:
        """獲取查詢統計"""
        key = f"perf:query:{query_name}"
        data = self.redis.hgetall(key)
        if data and data.get('count'):
            return {
                'count': int(data['count']),
                'total_time': float(data['total_time']),
                'avg_time': float(data['avg_time']),
                'last_time': float(data['last_time'])
            }
        return None


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    # 測試 Redis 連接
    print("=" * 60)
    print("Phase 8: Redis Caching Strategy")
    print("=" * 60)
    
    redis_client = RedisCache()
    
    if redis_client.ping():
        print("\n✅ Redis 連接成功")
    else:
        print("\n❌ Redis 連接失敗")
        exit(1)
    
    # 測試快取操作
    print("\n--- 快取操作測試 ---")
    redis_client.set("test:key", "test_value", ex=60)
    print(f"  ✅ 設定快取: {redis_client.get('test:key')}")
    
    redis_client.delete("test:key")
    print(f"  ✅ 刪除快取: {redis_client.get('test:key')}")
    
    # 測試 TTL 策略
    print("\n--- TTL 策略測試 ---")
    ttl_strategy = TTLStrategy(default_ttl=300)
    ttl_strategy.set_with_ttl("test:ttl", "ttl_value")
    ttl_data = ttl_strategy.get_with_ttl("test:ttl")
    print(f"  ✅ TTL 快取: {ttl_data['data']}, TTL: {ttl_data['ttl']}")
    
    # 測試 LRU 快取
    print("\n--- LRU 快取測試 ---")
    lru_cache = LRUCache(max_size=3)
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")
    lru_cache.put("key3", "value3")
    print(f"  ✅ LRU 快取大小: {len(lru_cache)}")
    
    # 測試 Agent 通訊快取
    print("\n--- Agent 通訊快取測試 ---")
    agent_cache = AgentCommunicationCache(redis_client)
    agent_cache.cache_agent_heartbeat("agent1", "active")
    agent_data = agent_cache.get_agent_heartbeat("agent1")
    print(f"  ✅ Agent 心跳: {agent_data}")
    
    # 測試社區資料快取
    print("\n--- 社區資料快取測試 ---")
    community_cache = CommunityDataCache(redis_client)
    community_cache.cache_community_info("community1", {"name": "明華社區", "address": "台北市"})
    community_data = community_cache.get_community_info("community1")
    print(f"  ✅ 社區資訊: {community_data}")
    
    print("\n" + "=" * 60)
    print("Redis 快取策略測試完成")
    print("=" * 60)
