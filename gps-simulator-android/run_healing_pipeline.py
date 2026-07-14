# -*- coding: utf-8 -*-
# run_healing_pipeline.py
import os
import sys
import json
import datetime
import subprocess
from auto_healer import heal_code

p_json = '../gemini_learning_context.json'

# 👑 整理大腦
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

def main():
    print('=== 🚀 啟動自癒與編譯整合管線 ===')
    success = False

    for i in range(1, 11):
        print(f'\n==================================================')
        print(f'🔄 [第 {i} / 10 次嘗試] 開始編譯與自癒管線...')
        print(f'==================================================')

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
            print(f'❌ 執行 Gradle 失敗: {e}')
            compile_status = 1

        if compile_status == 0:
            print(f'🎉 恭喜！第 {i} 次嘗試：專案編譯完美通過！')
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

        print(f'🚨 [第 {i} / 10 次嘗試] 編譯失敗！呼叫自癒大腦進行修復...')
        heal_code(i)

    # 執行重整
    cleanup_brain()

    if not success:
        print('❌ 達到最大嘗試次數 10 次，編譯最終失敗。')
        sys.exit(1)

if __name__ == "__main__":
    main()
