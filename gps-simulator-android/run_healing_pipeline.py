# -*- coding: utf-8 -*-
# run_healing_pipeline.py
import os
import sys
import json
import datetime
import subprocess
import base64
from auto_healer import heal_code_with_ai

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
            print('⚠️ [整理大腦] JSON 整理失敗: ' + str(e))

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.kt.bak') or file.endswith('.tmp'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

# 📝 生成 10 次失敗時的極詳細診斷報告（100% 禁用 f-string，改用安全字串拼接）
def generate_failure_report():
    print('📝 [自癒失敗] 正在產生詳細失敗診斷報告以供分析...')
    
    build_log_content = "（無日誌內容）"
    if os.path.exists('gradle_build.log'):
        try:
            build_log_content = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()
        except Exception as e:
            build_log_content = "讀取日誌失敗: " + str(e)

    brain_content = "（大腦 JSON 檔案不存在）"
    if os.path.exists(p_json):
        try:
            brain_data = json.load(open(p_json, 'r', encoding='utf-8'))
            brain_content = json.dumps(brain_data, indent=2, ensure_ascii=False)
        except Exception as e:
            brain_content = "讀取大腦 JSON 失敗: " + str(e)

    # 透過 Base64 安全解碼載入 Markdown 範本，繞過任何特殊字元對 Python 編譯的干擾
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
        template = base64.b64decode(template_b64).decode('utf-8', errors='ignore')
    except Exception:
        template = "# Diagnostic Report\nTime: @TIME@\n\n## Brain\n@BRAIN@\n\n## Log\n@LOG@"

    # 100% 採用純字串相加重構 save_detailed_report，徹底消滅 syntax error
    report = "# 📊 Gemini AI Auto-Healing Diagnostic Report\n"
    report += "Generated At: " + str(datetime.datetime.now().isoformat()) + "\n"
    report += "Status: ❌ FAILED (All 10 cycles failed)\n\n"
    
    # 讀取 failed code hashes
    try:
        brain_data = json.load(open(p_json, 'r', encoding='utf-8'))
        failed_hashes = brain_data.get('failed_code_hashes', [])
    except Exception:
        failed_hashes = []
        brain_data = {}

    report += "## 🧠 1. 核心去重資料庫 (Failed Code Hashes)\n"
    report += "為了防止鬼打牆，以下是編譯失敗過的程式碼特徵 MD5 集合：\n"
    report += "```json\n" + json.dumps(failed_hashes, indent=2) + "\n```\n\n"

    report += "## 🔄 2. 歷史 10 次自癒完整軌跡 (Detailed Run Logs)\n"
    report += "點擊下方展開各輪次的詳細報錯、Prompt、與 Gemini 給出的程式碼：\n\n"

    runs = brain_data.get('auto_healing_runs', [])
    for run in runs:
        cycle = run.get('cycle_attempt', '?')
        result_str = run.get('result', 'UNKNOWN')
        
        report += "### 📍 第 " + str(cycle) + " 輪嘗試 (結果: " + str(result_str) + ")\n"
        report += "<details>\n<summary>🔍 展開查看第 " + str(cycle) + " 輪的詳細分析與代碼</summary>\n\n"
        
        report += "#### ❌ 讀取到的錯誤內容\n"
        report += "
