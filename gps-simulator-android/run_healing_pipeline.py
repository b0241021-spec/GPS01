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
        brain_data = json.load(open(p_json, 'r', encoding='utf-8'))
        brain_content = json.dumps(brain_data, indent=2, ensure_ascii=False)
    except:
        brain_content = "{}"

    build_log = "（無日誌）"
    if os.path.exists('gradle_build.log'):
        build_log = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()[-8000:]

    report = f"# Gemini AI 運行狀況追蹤報告\n"
    report += f"產出時間: {datetime.datetime.now().isoformat()}\n"
    report += f"最終結果: {'🎉 成功通過' if success_cycle else '❌ 10輪皆失敗'}\n\n"
    report += f"## 📂 大腦目前記錄內容\n```json\n{brain_content}\n```\n\n"
    report += f"## 📝 最後一次 Gradle 編譯錯誤日誌\n```text\n{build_log}\n```\n"
    
    open(report_file, 'w', encoding='utf-8').write(report)
    print(f'✅ 報告已儲存至 {report_file}')

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

        if compile_status == 0:
            print(f'🎉 恭喜！第 {i} 輪專案編譯完美通過！')
            success = True
            save_detailed_report(success_cycle=i)
            break

        current_hash = get_file_hash(target_file)
        if current_hash:
            try:
                db = json.load(open(p_json, 'r', encoding='utf-8'))
                if current_hash not in db['failed_code_hashes']:
                    db['failed_code_hashes'].append(current_hash)
                    json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            except:
                pass

        print(f'🚨 第 {i} 輪編譯失敗！召喚 Gemini 進行自癒...')
        heal_code_with_ai(cycle=i, target_path=target_file)

    if not success:
        save_detailed_report(None)
        print('❌ 達到最大嘗試次數 10 次，編譯最終失敗。')
        sys.exit(1)

if __name__ == "__main__":
    main()
