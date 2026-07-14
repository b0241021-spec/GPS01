# -*- coding: utf-8 -*-
# run_healing_pipeline.py
import os
import sys
import json
import datetime
import subprocess
import hashlib
from auto_healer import heal_code_with_ai

p_json = '../gemini_learning_context.json'
report_file = '../auto_heal_failure_report.md'

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return ""
    try:
        content = open(filepath, 'r', encoding='utf-8', errors='ignore').read()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except Exception:
        return ""

# 🧹 整理與淨化大腦歷史記錄
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

# 📝 生成 10 次失敗時的極詳細診斷報告 (100% 安全單行字串陣列拼接，徹底避免折行 SyntaxError)
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
            brain_data = {}
    else:
        brain_data = {}

    lines = []
    lines.append("# 🚨 Gemini AI Auto-Healing Failure Diagnostic Report")
    lines.append("Generated at: " + str(datetime.datetime.now().isoformat()))
    lines.append("Status: ❌ FAILED (All 10 cycles failed)")
    lines.append("")
    lines.append("## 🧠 1. 核心去重資料庫 (Failed Code Hashes)")
    lines.append("為了防止鬼打牆，以下是編譯失敗過的程式碼特徵 MD5 集合：")
    lines.append("```json")
    lines.append(json.dumps(brain_data.get('failed_code_hashes', []), indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## 🔄 2. 歷史 10 次自癒完整軌跡 (Detailed Run Logs)")
    lines.append("下方展開各輪次的詳細報錯、Prompt、與 Gemini 給出的程式碼：")
    lines.append("")

    runs = brain_data.get('auto_healing_runs', [])
    for run in runs:
        cycle = str(run.get('cycle_attempt', '?'))
        result_str = str(run.get('result', 'UNKNOWN'))
        
        lines.append("### 📍 第 " + cycle + " 輪嘗試 (結果: " + result_str + ")")
        lines.append("<details>")
        lines.append("<summary>🔍 展開查看第 " + cycle + " 輪的詳細分析與代碼</summary>")
        lines.append("")
        lines.append("#### ❌ 讀取到的錯誤內容")
        lines.append("```text")
        lines.append(str(run.get('error_detected', '無')[-1500:]))
        lines.append("```")
        lines.append("")
        lines.append("#### 🧠 餵給 Gemini 的 Prompt 內容")
        lines.append("```text")
        lines.append(str(run.get('prompt_fed_to_gemini', '無')))
        lines.append("```")
        lines.append("")
        lines.append("#### ✍️ Gemini 的修改分析")
        lines.append("> " + str(run.get('gemini_analysis', '無')))
        lines.append("")
        lines.append("#### 💻 Gemini 給出的程式碼")
        lines.append("```kotlin")
        lines.append(str(run.get('gemini_suggested_code', '無')))
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## 📝 3. 最後一次 Gradle 編譯錯誤完整日誌")
    lines.append("```text")
    lines.append(build_log_content[-8000:])
    lines.append("```")

    report_markdown = "\n".join(lines)
    
    try:
        open(report_file, 'w', encoding='utf-8').write(report_markdown)
        print('✅ [診斷報告] 失敗診斷報告已寫出至: ' + report_file)
    except Exception as e:
        print('❌ [診斷報告] 寫出失敗: ' + str(e))

def init_clean_brain():
    print('🧹 [第一步] 徹底清空大腦記憶體...')
    initial_brain = {
        "initial_knowledge": {
            "failed_experiences": [
                "Redeclaration: SimulationState.kt 重複定義",
                "Unresolved reference: TIRAMISU / POST_NOTIFICATIONS 報錯",
                "Unresolved reference: tvCustomCurrentGps 拼寫錯誤",
                "Type mismatch: inferred type is String but Editable! was expected",
                "Unresolved reference: setTargetLocation 缺失",
                "Unresolved reference: AlertDialog 漏導包",
                "Coroutines FlowCollector Lambda 語意衝突",
                "Conflicting import 重複引入"
            ],
            "buggy_experiences": [
                "WindowManager.LayoutParams 懸浮窗未設定 FLAG_NOT_FOCUSABLE 會導致全螢幕觸控被攔截(Touch Blocked)"
            ]
        },
        "auto_healing_runs": [],
        "failed_code_hashes": []
    }
    with open(p_json, 'w', encoding='utf-8') as f:
        json.dump(initial_brain, f, indent=2, ensure_ascii=False)
    print('✅ [第二步] 初始經驗注入完畢！')

def save_detailed_report(success_cycle=None):
    generate_failure_report()

def main():
    print('=== 🧠 啟動全環節 AI 自癒與編譯主控管線 ===')
    
    # ---------------- 環節 1: 環境健全度自我修復 ----------------
    print('⚙️ [環節 1] 執行環境健全度自我修復...')
    try:
        if os.path.exists('gradlew'):
            os.system('sed -i "s/\\r$//" gradlew')
            os.system('chmod +x gradlew')
        if not os.path.exists(p_json):
            init_clean_brain()
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
        # 環節 2 失敗時，自動呼叫自癒引擎修復
        heal_code_with_ai(0, 'app/src/main/java/com/gpssimulator/MainActivity.kt', 'Brain Access Check Failed')

    # ---------------- 環節 3: 核心 10 次自癒編譯迴圈 ----------------
    success = False
    target_file = 'app/src/main/java/com/gpssimulator/MainActivity.kt'
    
    for i in range(1, 11):
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

        # 讀取本次編譯日誌
        log_error = ""
        if os.path.exists('gradle_build.log'):
            try:
                log_error = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()[-4000:]
            except Exception:
                pass

        if compile_status == 0:
            print('🎉 恭喜！第 ' + str(i) + ' 次嘗試：專案編譯完美通過！')
            if os.path.exists(p_json):
                try:
                    db = json.load(open(p_json, 'r', encoding='utf-8'))
                    run_log = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'cycle_attempt': i,
                        'status': 'SUCCESS',
                        'error_detected': 'None (Succeeded)',
                        'prompt_fed_to_gemini': 'None (Skipped)',
                        'gemini_analysis': 'None (Succeeded)',
                        'gemini_suggested_code': open(target_file, 'r', encoding='utf-8', errors='ignore').read(),
                        'result': 'COMPILATION_PASSED'
                    }
                    db['auto_healing_runs'].append(run_log)
                    json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
                except Exception:
                    pass
            success = True
            break

        # 記錄本次失敗代碼 Hash
        if os.path.exists(target_file):
            try:
                content = open(target_file, 'r', encoding='utf-8', errors='ignore').read()
                current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                db = json.load(open(p_json, 'r', encoding='utf-8'))
                if current_hash not in db.get('failed_code_hashes', []):
                    db.setdefault('failed_code_hashes', []).append(current_hash)
                    json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            except Exception:
                pass

        print('🚨 [第 ' + str(i) + ' 次嘗試] 編譯失敗！呼叫自癒大腦進行修復...')
        heal_code_with_ai(i, target_file, log_error)

    # 🧽 整理與歸檔大腦
    cleanup_brain()

    if not success:
        generate_failure_report()
        print('❌ 達到最大嘗試次數 10 次，編譯最終失敗。')
        sys.exit(1)

if __name__ == "__main__":
    main()
