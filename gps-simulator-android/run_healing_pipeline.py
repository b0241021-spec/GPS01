# -*- coding: utf-8 -*-
# run_healing_pipeline.py
import os
import sys
import json
import datetime
import subprocess
import base64
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

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.kt.bak') or file.endswith('.tmp'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

# 📝 生成 10 次失敗時的極詳細診斷報告（透過 Base64 避開一切 Python 引號地獄）
def generate_failure_report():
    print('📝 [自癒失敗] 正在產生詳細失敗診斷報告以供分析...')
    
    build_log_content = "（無日誌內容）"
    if os.path.exists('gradle_build.log'):
        try:
            build_log_content = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()
        except Exception as e:
            build_log_content = f"讀取日誌失敗: {e}"

    brain_content = "（大腦 JSON 檔案不存在）"
    if os.path.exists(p_json):
        try:
            brain_data = json.load(open(p_json, 'r', encoding='utf-8'))
            brain_content = json.dumps(brain_data, indent=2, ensure_ascii=False)
        except Exception as e:
            brain_content = f"讀取大腦 JSON 失敗: {e}"

    # 👑 透過 Base64 加密儲存 Markdown 範本，免除任何引號、換行符號、特殊符號對 Python 解析器的干擾
    # 原始文字為之前的 Markdown 報告結構
    template_b64 = (
        'IyA7AgR2VtaW5pIEFJIEF1dG8tSGVhbGluZyBGYWlsdXJlIERpYWdub3N0aWMgUmVwb3J0CgogR2VuZXJhdGVkIG'
        'F0OiBAVElNRUAKCmhSMi4g8J+SlCDorqvZgspl56GN6Yiq5YWnIChCcmFpbiBDb250ZXh0IE1lbW9yeSkK6YmZ6b'
        'Wk5piv55uu5YmN5oyB6Zq續57at6K2w6YCB6YgZ55qE5a2457+S5aSn6IWv5YWnIChgZ2VtaW5pX2xlYXJuaW5nX2'
        'NvbnRleHQuanNvbmApIDoKYGBganNvbgpAcgJSQUlOQApgYGBKCmgyLiDwn7SmIOorqvZgsl06YgZ55qE編eorque'
        'orueWnotWFreKkhCAoTGFzdCBHcmFkbGUgQnVpbGQgTG9nKQorZmWm5piv5pyA5b6M5LiA5qyhIChsdGggMTDmrY'
        'gpIOWYpS6YgZ編eorqueorueZqEmsZSBzZWN0aW9uIDoKYGBndGV4dApAcgJMT0dACmBgYgpoMi4g8J+aoCDonY'
        'bntbYgR2VtaW5pIOWgkeS4iWbiiWbCrfmmrOekvSAoUHJvbXB0IElucHV0IE1vZGVsKQorZmW自576O566h566h'
        '6L6mOgotICoq5b+D6Zqm5LiK5LiL5paHKiogOiAn6Zqm5LiK55qEIGBncmFkbGVfYnVpbGQubG9nYCDlYbnpoSgK'
        'LSAqKOWkp+iFr+efpeatp+imi+aZhSoqIDogJyDlhYjliY3nu6p次5bCd6Kmm5rKJ5reA5LiL5L6m55qEIGBhdXRv'
        'X2hlYWxpbmdfcnVuc2BgCi0gKirnm67mqmXpobXnm67npZ6vKiogOiAnIOatpOatp+Wfailb6ZSm6KGp55qE57mG'
        '6auU5rqQ6bmoCgpoMi4g4oqj5Y2U5piv6Ieq5b6M6Ieq5bCd6Kmm6KKp5Y6m55qE6KGM6YuV6K2w6YCBIChBY3Rp'
        'b25zIFRha2VuKQorZmZp6K6p6Z閱5LiK5paH4oCcMS4g6K6u2YLJZeehmem6uFfni6bCmsat6K2w6YCB4oCd76yM'
        'YGN5Y2xlX2F0dGVtcHRgIDEg6IezIDEwIOVpdiBgYWN0aW9uc190YWtlbmAg6Zia5Yid4oCC'
    )
    
    try:
        # 解碼範本
        template = base64.b64decode(template_b64).decode('utf-8', errors='ignore')
    except Exception:
        # 萬一解碼失敗的極限 Fallback 方案
        template = "# Diagnostic Report\nTime: @TIME@\n\n## Brain\n@BRAIN@\n\n## Log\n@LOG@"

    log_tail = build_log_content[-10000:] if len(build_log_content) > 10000 else build_log_content
    
    # 進行安全替換
    report_markdown = template.replace("@TIME@", datetime.datetime.now().isoformat())\
                              .replace("@BRAIN@", brain_content)\
                              .replace("@LOG@", log_tail)
    
    try:
        open(report_file, 'w', encoding='utf-8').write(report_markdown)
        print(f'✅ [診斷報告] 失敗診斷報告已寫出至: {report_file}')
    except Exception as e:
        print(f'❌ [診斷報告] 寫出失敗: {e}')


def main():
    print('=== 🧠 啟動全環節 AI 自癒與編譯主控管線 ===')
    
    # ---------------- 環節 1: 環境健全度自我修復 ----------------
    print('⚙️ [環節 1] 執行環境健全度自我修復...')
    try:
        if os.path.exists('gradlew'):
            os.system('sed -i "s/\\r$//" gradlew')
            os.system('chmod +x gradlew')
        if not os.path.exists(p_json):
            with open(p_json, 'w', encoding='utf-8') as f:
                json.dump({"auto_healing_runs": []}, f, indent=2)
        print('✅ [環節 1] 環境健全度就緒！')
    except Exception as e:
        print(f'🚨 [環節 1 失敗] 環境修正發生異常: {e}')

    # ---------------- 環節 2: 大腦讀寫主動防禦測試 ----------------
    print('🧠 [環節 2] 驗證大腦記憶體 CRUD 生命週期...')
    try:
        if os.path.exists(p_json):
            db = json.load(open(p_json, 'r', encoding='utf-8'))
            db['last_health_check'] = datetime.datetime.now().isoformat()
            json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            print('✅ [環節 2] 大腦讀寫防禦測試通過！')
        else:
            raise FileNotFoundError("Gemini 大腦記憶庫遺失，嘗試在下一步重新喚醒。")
    except Exception as e:
        print(f'🚨 [環節 2 警報] 大腦存取異常，嘗試呼叫自癒修復: {e}')
        heal_code(0)

    # ---------------- 環節 3: 核心 10 次自癒編譯迴圈 ----------------
    success = False
    for i in range(1, 11):
        print(f'\n==================================================')
        print(f'🔄 [環節 3]
