# -*- coding: utf-8 -*-
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
    except:
        return ""

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
    print('📝 正在輸出最終運作狀況分析報告...')
    try:
        with open(p_json, 'r', encoding='utf-8') as f:
            brain_data = json.load(f)
    except Exception:
        brain_data = {}

    build_log = "（無日誌）"
    if os.path.exists('gradle_build.log'):
        try:
            build_log = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()[-8000:]
        except Exception:
            pass

    # 建立結構化 Markdown
    report = f"# 📊 Gemini AI Auto-Healing Diagnostic Report\n"
    report += f"Generated At: {datetime.datetime.now().isoformat()}\n"
    report += f"Status: {'🎉 SUCCESS (Cycle ' + str(success_cycle) + ')' if success_cycle else '❌ FAILED (All 10 cycles)'}\n\n"
    
    report += "## 🧠 1. 核心去重資料庫 (Failed Code Hashes)\n"
    report += "為了防止鬼打牆，以下是編譯失敗過的程式碼特徵 MD5 集合：\n"
    report += f"```json\n{json.dumps(brain_data.get('failed_code_hashes', []), indent=2)}\n```\n\n"

    report += "## 🔄 2. 歷史 10 次自癒完整軌跡 (Detailed Run Logs)\n"
    report += "點擊下方展開各輪次的詳細報錯、Prompt、與 Gemini 給出的程式碼：\n\n"

    runs = brain_data.get('auto_healing_runs', [])
    for run in runs:
        cycle = run.get('cycle_attempt', '?')
        result_str = run.get('result', 'UNKNOWN')
        
        report += f"### 📍 第 {cycle} 輪嘗試 (結果: {result_str})\n"
        report += "<details>\n<summary>🔍 展開查看第 " + str(cycle) + " 輪的詳細分析與代碼</summary>\n\n"
        
        report += "#### ❌ 讀取到的錯誤內容\n"
        report += f"
http://googleusercontent.com/immersive_entry_chip/0

---

### 🎯 接下來你可以這樣做：
1. **直接將程式碼推送到 GitHub。**
2. 當自癒失敗、Workflow 結束並自動 Commit 提交後，在你的 GitHub 項目根目錄會出現 `auto_heal_failure_report.md`。
3. **不用複製它！** 直接把該檔案在瀏覽器上的網址（例如：`https://github.com/你的用戶名/你的倉庫/blob/main/auto_heal_failure_report.md`）複製並**直接貼給我**。
4. 我會直接讀取該網頁中的 Markdown，為你進行極致深度的自癒瓶頸分析！

def main():
    print('=== 🚀 啟動全新記憶反思型自癒管線 ===')
    init_clean_brain()
    target_file = 'app/src/main/java/com/gpssimulator/MainActivity.kt'
    success = False

    for i in range(1, 11):
        print('\n' + '='*50)
        print(f'🔄 [環節 3][第 {i} / 10 輪] 開始編譯...')
        print('='*50)

        if os.path.exists('gradle_build.log'): 
            os.remove('gradle_build.log')
        
        try:
            with open('gradle_build.log', 'w', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    ['./gradlew', 'assembleDebug', '--no-daemon', '--no-build-cache'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore'
                )
                for line in process.stdout:
                    sys.stdout.write(line)
                    log_file.write(line)
                process.wait()
                compile_status = process.returncode
        except Exception:
            compile_status = 1

        log_error = ""
        if os.path.exists('gradle_build.log'):
            log_error = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()[-4000:]

        if compile_status == 0:
            print(f'🎉 恭喜！第 {i} 輪專案編譯完美通過！')
            success = True
            
            try:
                db = json.load(open(p_json, 'r', encoding='utf-8'))
                run_log = {
                    "cycle_attempt": i,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error_detected": "None (Compilation Succeeded!)",
                    "prompt_fed_to_gemini": "None (Skipped, build passed)",
                    "gemini_analysis": "None (Succeeded)",
                    "gemini_suggested_code": open(target_file, 'r', encoding='utf-8', errors='ignore').read(),
                    "result": "COMPILATION_PASSED"
                }
                db['auto_healing_runs'].append(run_log)
                with open(p_json, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
            except:
                pass
                
            save_detailed_report(success_cycle=i)
            break

        current_hash = get_file_hash(target_file)
        if current_hash:
            try:
                db = json.load(open(p_json, 'r', encoding='utf-8'))
                if current_hash not in db['failed_code_hashes']:
                    db['failed_code_hashes'].append(current_hash)
                    with open(p_json, 'w', encoding='utf-8') as f:
                        json.dump(db, f, indent=2, ensure_ascii=False)
            except:
                pass

        print(f'🚨 第 {i} 輪編譯失敗！召喚 Gemini 進行自癒...')
        heal_code_with_ai(cycle=i, target_path=target_file, log_error=log_error)

    if not success:
        save_detailed_report(None)
        print('❌ 達到最大嘗試次數 10 次，編譯最終失敗。')
        sys.exit(1)

if __name__ == "__main__":
    main()
