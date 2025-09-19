from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os

pomodoro_bp = Blueprint('pomodoro', __name__)

# 番茄钟数据存储文件
POMODORO_DATA_FILE = 'pomodoro_data.json'

class PomodoroManager:
    def __init__(self):
        self.data_file = POMODORO_DATA_FILE
        self.load_data()
    
    def load_data(self):
        """加载番茄钟数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    'sessions': [],
                    'settings': {
                        'work_duration': 25,
                        'short_break': 5,
                        'long_break': 15,
                        'sessions_until_long_break': 4,
                        'auto_start_breaks': False,
                        'auto_start_work': False,
                        'sound_enabled': True
                    },
                    'statistics': {
                        'total_sessions': 0,
                        'total_work_time': 0,
                        'total_break_time': 0,
                        'daily_stats': {}
                    }
                }
        except Exception as e:
            print(f"加载番茄钟数据错误: {e}")
            self.data = {
                'sessions': [],
                'settings': {
                    'work_duration': 25,
                    'short_break': 5,
                    'long_break': 15,
                    'sessions_until_long_break': 4,
                    'auto_start_breaks': False,
                    'auto_start_work': False,
                    'sound_enabled': True
                },
                'statistics': {
                    'total_sessions': 0,
                    'total_work_time': 0,
                    'total_break_time': 0,
                    'daily_stats': {}
                }
            }
    
    def save_data(self):
        """保存番茄钟数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存番茄钟数据错误: {e}")
    
    def add_session(self, session_type, duration, completed=True):
        """添加番茄钟会话记录"""
        session = {
            'id': len(self.data['sessions']) + 1,
            'type': session_type,  # 'work', 'short_break', 'long_break'
            'duration': duration,  # 分钟
            'completed': completed,
            'start_time': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['sessions'].append(session)
        
        # 更新统计数据
        self.update_statistics(session)
        
        self.save_data()
        return session
    
    def update_statistics(self, session):
        """更新统计数据"""
        stats = self.data['statistics']
        date = session['date']
        
        if session['completed']:
            if session['type'] == 'work':
                stats['total_sessions'] += 1
                stats['total_work_time'] += session['duration']
            else:
                stats['total_break_time'] += session['duration']
        
        # 更新每日统计
        if date not in stats['daily_stats']:
            stats['daily_stats'][date] = {
                'work_sessions': 0,
                'work_time': 0,
                'break_time': 0
            }
        
        daily = stats['daily_stats'][date]
        if session['completed']:
            if session['type'] == 'work':
                daily['work_sessions'] += 1
                daily['work_time'] += session['duration']
            else:
                daily['break_time'] += session['duration']
    
    def get_settings(self):
        """获取设置"""
        return self.data['settings']
    
    def update_settings(self, new_settings):
        """更新设置"""
        self.data['settings'].update(new_settings)
        self.save_data()
        return self.data['settings']
    
    def get_statistics(self, days=7):
        """获取统计数据"""
        stats = self.data['statistics'].copy()
        
        # 获取最近几天的数据
        today = datetime.now().date()
        recent_days = []
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_stats = stats['daily_stats'].get(date, {
                'work_sessions': 0,
                'work_time': 0,
                'break_time': 0
            })
            recent_days.append({
                'date': date,
                **day_stats
            })
        
        stats['recent_days'] = list(reversed(recent_days))
        
        # 计算平均值
        if len(recent_days) > 0:
            total_work_sessions = sum(day['work_sessions'] for day in recent_days)
            total_work_time = sum(day['work_time'] for day in recent_days)
            
            stats['average_daily_sessions'] = total_work_sessions / len(recent_days)
            stats['average_daily_work_time'] = total_work_time / len(recent_days)
        else:
            stats['average_daily_sessions'] = 0
            stats['average_daily_work_time'] = 0
        
        return stats
    
    def get_today_sessions(self):
        """获取今天的会话记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_sessions = [s for s in self.data['sessions'] if s['date'] == today]
        return today_sessions

pomodoro_manager = PomodoroManager()

@pomodoro_bp.route('/settings', methods=['GET'])
def get_settings():
    """获取番茄钟设置"""
    try:
        settings = pomodoro_manager.get_settings()
        return jsonify({
            'settings': settings
        })
    except Exception as e:
        print(f"获取设置错误: {e}")
        return jsonify({'error': '获取设置失败'}), 500

@pomodoro_bp.route('/settings', methods=['POST'])
def update_settings():
    """更新番茄钟设置"""
    try:
        data = request.get_json()
        settings = pomodoro_manager.update_settings(data)
        return jsonify({
            'settings': settings,
            'message': '设置已更新'
        })
    except Exception as e:
        print(f"更新设置错误: {e}")
        return jsonify({'error': '更新设置失败'}), 500

@pomodoro_bp.route('/session', methods=['POST'])
def add_session():
    """添加番茄钟会话记录"""
    try:
        data = request.get_json()
        session_type = data.get('type')  # 'work', 'short_break', 'long_break'
        duration = data.get('duration', 25)
        completed = data.get('completed', True)
        
        if not session_type:
            return jsonify({'error': '会话类型不能为空'}), 400
        
        session = pomodoro_manager.add_session(session_type, duration, completed)
        
        return jsonify({
            'session': session,
            'message': '会话记录已添加'
        })
        
    except Exception as e:
        print(f"添加会话记录错误: {e}")
        return jsonify({'error': '添加会话记录失败'}), 500

@pomodoro_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        days = request.args.get('days', 7, type=int)
        statistics = pomodoro_manager.get_statistics(days)
        
        return jsonify({
            'statistics': statistics
        })
        
    except Exception as e:
        print(f"获取统计数据错误: {e}")
        return jsonify({'error': '获取统计数据失败'}), 500

@pomodoro_bp.route('/today', methods=['GET'])
def get_today_sessions():
    """获取今天的会话记录"""
    try:
        sessions = pomodoro_manager.get_today_sessions()
        
        # 计算今天的统计
        work_sessions = len([s for s in sessions if s['type'] == 'work' and s['completed']])
        total_work_time = sum(s['duration'] for s in sessions if s['type'] == 'work' and s['completed'])
        total_break_time = sum(s['duration'] for s in sessions if s['type'] != 'work' and s['completed'])
        
        return jsonify({
            'sessions': sessions,
            'summary': {
                'work_sessions': work_sessions,
                'total_work_time': total_work_time,
                'total_break_time': total_break_time,
                'total_sessions': len(sessions)
            }
        })
        
    except Exception as e:
        print(f"获取今日会话错误: {e}")
        return jsonify({'error': '获取今日会话失败'}), 500

@pomodoro_bp.route('/reset', methods=['POST'])
def reset_data():
    """重置番茄钟数据（谨慎使用）"""
    try:
        # 只重置会话记录，保留设置
        pomodoro_manager.data['sessions'] = []
        pomodoro_manager.data['statistics'] = {
            'total_sessions': 0,
            'total_work_time': 0,
            'total_break_time': 0,
            'daily_stats': {}
        }
        pomodoro_manager.save_data()
        
        return jsonify({
            'message': '数据已重置'
        })
        
    except Exception as e:
        print(f"重置数据错误: {e}")
        return jsonify({'error': '重置数据失败'}), 500