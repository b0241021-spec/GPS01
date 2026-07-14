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
            print('⚠️ [整理大腦] JSON 整理失敗: ' + str(e))

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

    log_tail = build_log_content[-10000:] if len(build_log_content) > 10000 else build_log_content
    
    report_markdown = template.replace("@TIME@", datetime.datetime.now().isoformat())\
                              .replace("@BRAIN@", brain_content)\
                              .replace("@LOG@", log_tail)
    
    try:
        open(report_file, 'w', encoding='utf-8').write(report_markdown)
        print('✅ [診斷報告] 失敗診斷報告已寫出。')
    except Exception as e:
        print('❌ [診斷報告] 寫出失敗: ' + str(e))


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
        print('🚨 [環節 1 失敗] 環境修正發生異常: ' + str(e))

    # ---------------- 環節 2: 大腦讀寫主動防禦測試 ----------------
    print('🧠 [環節 2] 驗證大腦記憶體 CRUD 生命週期...')
    try:
        if os.path.exists(p_json):
            db = json.load(open(p_json, 'r', encoding='utf-8'))
            db['last_health_check'] = datetime.datetime.now().isoformat()
            json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            print('✅ [環節 2] 大腦讀寫防禦測試通過！')
        else:
            raise FileNotFoundError("Gemini 大腦記憶庫遺失。")
    except Exception as e:
        print('🚨 [環節 2 警報] 大腦存取異常: ' + str(e))
        heal_code(0)

    # ---------------- 環節 3: 核心 10 次自癒編譯迴圈 ----------------
    success = False
    for i in range(1, 11):
        # 👑 徹底移除這行的 f-string 與 \n，改用最純粹的安全文字拼接，消滅 L134 錯誤
        print('')
        print('==================================================')
        print('🔄 [環節 3][第 ' + str(i) + ' / 10 次嘗試] 開始編譯與自癒流程...')
        print('==================================================')

        if os.path.exists('gradle_build.log'):
            os.remove('gradle_build.log')

        try:
            with open('gradle_build.log', 'w', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    ['./gradlew', 'assembleDebug', '--no-daemon', '--no-build-cache'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                for line in process.stdout:
                    sys.stdout.write(line)
                    log_file.write(line)
                process.wait()
                compile_status = process.returncode
        except Exception as e:
            print('❌ 執行 Gradle 失敗: ' + str(e))
            compile_status = 1

        if compile_status == 0:
            print('🎉 恭喜！第 ' + str(i) + ' 次嘗試：專案編譯完美通過！')
            if os.path.exists(p_json):
                try:
                    db = json.load(open(p_json, 'r', encoding='utf-8'))
                    run_log = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'cycle_attempt': i,
                        'status': 'SUCCESS',
                        'actions_taken': ['Compilation passed successfully. Final APK is ready.']
                    }
                    db['auto_healing_runs'].append(run_log)
                    json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
                except Exception:
                    pass
            success = True
            break

        print('🚨 [第 ' + str(i) + ' 次嘗試] 編譯失敗！呼叫自癒大腦進行修復...')
        heal_code(i)

    cleanup_brain()

    if not success:
        generate_failure_report()
        print('❌ 達到最大嘗試次數 10 次，編譯最終失敗。')
        sys.exit(1)

if __name__ == "__main__":
    main()
