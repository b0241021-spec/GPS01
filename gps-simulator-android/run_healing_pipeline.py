# -*- coding: utf-8 -*-
# run_healing_pipeline.py
import os
import sys
import json
import datetime
import subprocess
from auto_healer import heal_code

p_json = '../gemini_learning_context.json'
report_file = '../auto_heal_failure_report.md'

# 🧹 整理大腦
def cleanup_brain():
    print('🧹 [整理大腦] 啟動學習庫去重整理...')
    if os.path.exists(p_json):
        try:
            db = json.load(open(p_json, 'r', encoding='utf-8'))
            if 'auto_healing_runs' in db:
                seen_timestamps = set()
                unique_runs = []
                for run in db['auto_healing_runs']:
                    ts = run.get('timestamp')
                    if ts not in seen_timestamps:
                        seen_timestamps.add(ts)
                        unique_runs.append(run)
                db['auto_healing_runs'] = unique_runs
                json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
                print('✅ [整理大腦] JSON 學習資料庫完成重整與去重！')
        except Exception as e:
            print(f'⚠️ [整理大腦] JSON 整理失敗: {e}')

    # 清理多餘暫存檔
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.kt.bak') or file.endswith('.tmp'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

# 📝 生成 10 次失敗時的極詳細診斷報告
def generate_failure_report():
    print('📝 [自癒失敗] 正在產生詳細失敗診斷報告以供分析...')
    
    # 1. 讀取最後一次編譯的實際錯誤內容 (gradle_build.log)
    build_log_content = "（無日誌內容）"
    if os.path.exists('gradle_build.log'):
        try:
            build_log_content = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()
        except Exception as e:
            build_log_content = f"讀取日誌失敗: {e}"

    # 2. 讀取寫進大腦的內容 (gemini_learning_context.json)
    brain_content = "（大腦 JSON 檔案不存在）"
    if os.path.exists(p_json):
        try:
            brain_data = json.load(open(p_json, 'r', encoding='utf-8'))
            brain_content = json.dumps(brain_data, indent=2, ensure_ascii=False)
        except Exception as e:
            brain_content = f"讀取大腦 JSON 失敗: {e}"

    # 3. 組合報告
    report_markdown = f"""# 🚨 Gemini AI Auto-Healing Failure Diagnostic Report
Generated at: {datetime.datetime.now().isoformat()}

## 1. 📂 寫進大腦的內容 (Brain Context Memory)
這是目前持續維護並記錄的學習大腦內容 (`gemini_learning_context.json`)：
```json
{brain_content}
