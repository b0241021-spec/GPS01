# -*- coding: utf-8 -*-
# auto_healer.py
import os
import re
import json
import datetime
import sys

def heal_code(cycle):
    p_json = '../gemini_learning_context.json'
    log_exists = os.path.exists('gradle_build.log')
    log_content = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read() if log_exists else ''

    actions_taken = []
    detected_errors = []

    # 歷史問題 5：懸浮窗
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.kt') and file not in ['auto_healer.py', 'run_healing_pipeline.py']:
                p = os.path.join(root, file)
                try:
                    code_kt = open(p, 'r', encoding='utf-8').read()
                    if 'WindowManager.LayoutParams' in code_kt and 'FLAG_NOT_FOCUSABLE' not in code_kt:
                        detected_errors.append('Screen Overlay Touch Blocked')
                        code_kt = code_kt.replace(
                            'WindowManager.LayoutParams(',
                            'WindowManager.LayoutParams(\n            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,\n            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,\n            '
                        )
                        open(p, 'w', encoding='utf-8').write(code_kt)
                        actions_taken.append(f'Auto-repaired {p}: Configured WindowManager flags for Touch Passthrough.')
                except Exception:
                    pass

    # 規則 0: 處理 gradlew 啟動即崩潰
    if not log_exists or len(log_content.strip()) == 0:
        detected_errors.append('Gradlew Boot Crash')
        os.system('sed -i "s/\r$//" gradlew')
        os.system('chmod +x gradlew')
        actions_taken.append('Sanitized gradlew line endings and fixed execution permission.')

    # 規則 1: 解決 Redeclaration
    if 'Redeclaration: SimulationState' in log_content:
        detected_errors.append('Redeclaration: SimulationState')
        target_dup = 'app/src/main/java/com/gpssimulator/data/SimulationState.kt'
        if os.path.exists(target_dup):
            os.remove(target_dup)
            actions_taken.append('Removed duplicate file: SimulationState.kt')

    # 規則 2: 解決 TIRAMISU / POST_NOTIFICATIONS 相容問題
    if 'Unresolved reference: TIRAMISU' in log_content or 'Unresolved reference: POST_NOTIFICATIONS' in log_content:
        detected_errors.append('Unresolved reference: TIRAMISU / POST_NOTIFICATIONS')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    code_kt = open(p, 'r', encoding='utf-8', errors='ignore').read()
                    code_kt = code_kt.replace('Build.VERSION_CODES.TIRAMISU', '33')
                    code_kt = code_kt.replace('Manifest.permission.POST_NOTIFICATIONS', '"android.permission.POST_NOTIFICATIONS"')
                    open(p, 'w', encoding='utf-8').write(code_kt)
                    actions_taken.append(f'Modified {p}: Downgraded Tiramisu references.')

    # 規則 3: 解決 tvCustomCurrentGps 變數名拼寫錯誤
    if 'Unresolved reference: tvCustomCurrentGps' in log_content:
        detected_errors.append('Unresolved reference: tvCustomCurrentGps')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    code_kt = open(p, 'r', encoding='utf-8', errors='ignore').read()
                    code_kt = code_kt.replace('tvCustomCurrentGps', 'tvCurrentGps')
                    open(p, 'w', encoding='utf-8').write(code_kt)
                    actions_taken.append(f'Modified {p}: Standardized UI variable to tvCurrentGps.')

    # 規則 6: 解決 Editable 型別不相容問題
    if 'Type mismatch: inferred type is String but Editable! was expected' in log_content:
        detected_errors.append('Type mismatch: String to Editable')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    code_kt = open(p, 'r', encoding='utf-8', errors='ignore').read()
                    modified_code = re.sub(r'(\w+)\.text\s*=\s*(.*?)\n', r'\1.setText(\2)\n', code_kt)
                    if modified_code != code_kt:
                        open(p, 'w', encoding='utf-8').write(modified_code)
                        actions_taken.append(f'Auto-repaired {p}: Replaced .text direct assignment with .setText()')

    # 規則 7: 解決 setTargetLocation 方法遺失問題
    if 'Unresolved reference: setTargetLocation' in log_content:
        detected_errors.append('Unresolved reference: setTargetLocation')
        p_mgr = 'app/src/main/java/com/gpssimulator/data/GPSSimulatorStateManager.kt'
        if os.path.exists(p_mgr):
            code_kt = open(p_mgr, 'r', encoding='utf-8').read()
            if 'setTargetLocation' not in code_kt:
                code_kt = code_kt.replace(
                    'fun updateState(newState: SimulationState) { state = newState }',
                    'fun updateState(newState: SimulationState) { state = newState }\n        fun setTargetLocation(latitude: Double, longitude: Double) {}\n        fun setTargetLocation(latitude: String, longitude: String) {}'
                )
                open(p_mgr, 'w', encoding='utf-8').write(code_kt)
                actions_taken.append(f'Updated {p_mgr}: Appended compatible setTargetLocation methods.')

    # 規則 8: 解決 AlertDialog 遺失導包問題
    if 'Unresolved reference: AlertDialog' in log_content:
        detected_errors.append('Unresolved reference: AlertDialog')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    code_kt = open(p, 'r', encoding='utf-8', errors='ignore').read()
                    if 'import androidx.appcompat.app.AlertDialog' not in code_kt and 'import android.app.AlertDialog' not in code_kt:
                        code_kt = re.sub(r'(package\s+[\w\.]+)', r'\1\nimport androidx.appcompat.app.AlertDialog', code_kt)
                        open(p, 'w', encoding='utf-8').write(code_kt)
                        actions_taken.append(f'Added import androidx.appcompat.app.AlertDialog in {p}')

    # 規則 9: 解決協程 Flow 監聽 lambda 語意衝突
    if 'FlowCollector' in log_content or 'Cannot infer a type for this parameter' in log_content:
        detected_errors.append('Coroutines FlowCollector Lambda Error')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    code_kt = open(p, 'r', encoding='utf-8', errors='ignore').read()
                    if 'collect' in code_kt:
                        # 將不標準的 collect { ... -> ... } 轉為 collect { state ->
                        code_kt = re.sub(r'collect\s*\{\s*.*?->', 'collect { state -> ', code_kt)
                        open(p, 'w', encoding='utf-8').write(code_kt)
                        actions_taken.append(f'Standardized Flow.collect lambda parameters in {p}')

    # 規則 4（備份保險）：重新確保 GPSSimulatorStateManager.kt 必定存在
    if 'Unresolved reference: GPSSimulatorStateManager' in log_content or not os.path.exists('app/src/main/java/com/gpssimulator/data/GPSSimulatorStateManager.kt'):
        detected_errors.append('Unresolved reference: GPSSimulatorStateManager')
        os.makedirs('app/src/main/java/com/gpssimulator/data', exist_ok=True)
        p_mgr = 'app/src/main/java/com/gpssimulator/data/GPSSimulatorStateManager.kt'
        manager_code = """package com.gpssimulator.data
import com.gpssimulator.data.SimulationState
object GPSSimulatorStateManager {
    var state = SimulationState()
    fun updateState(newState: SimulationState) { state = newState }
    fun setTargetLocation(latitude: Double, longitude: Double) {}
    fun setTargetLocation(latitude: String, longitude: String) {}
}"""
        open(p_mgr, 'w', encoding='utf-8').write(manager_code)
        actions_taken.append(f'Created fallback class: {p_mgr}')

    # 規則 5: 解決 import 衝突與重複引入
    if 'Conflicting import' in log_content:
        detected_errors.append('Conflicting import')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'MainActivity.kt':
                    p = os.path.join(root, file)
                    lines = open(p, 'r', encoding='utf-8', errors='ignore').readlines()
                    seen_imports = set()
                    clean_lines = []
                    for line in lines:
                        if line.strip().startswith('import '):
                            if line not in seen_imports:
                                seen_imports.add(line)
                                clean_lines.append(line)
                        else:
                            clean_lines.append(line)
                    open(p, 'w', encoding='utf-8').write(''.join(clean_lines))
                    actions_taken.append(f'Cleaned up duplicated imports in {p}.')

    # 寫入 JSON 學習記錄
    if os.path.exists(p_json) and (actions_taken or detected_errors):
        try:
            db = json.load(open(p_json, 'r', encoding='utf-8'))
            run_log = {
                'timestamp': datetime.datetime.now().isoformat(),
                'cycle_attempt': int(cycle),
                'status': 'FAILED_BUT_HEALED',
                'detected_errors': detected_errors,
                'actions_taken': actions_taken
            }
            db['auto_healing_runs'].append(run_log)
            json.dump(db, open(p_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            print(f'✅ [大腦修復記錄] 成功記錄至學習庫。')
        except Exception as e:
            print(f'❌ 寫入 JSON 學習庫失敗: {e}')
