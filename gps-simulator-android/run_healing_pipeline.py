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
    except:
        return ""

def init_clean_brain():
    print('🧹 [第一步] 徹底清空大腦記憶體...')
    # 第二步：注入最開始的初始經驗（失敗模式 + 成功但有問題的懸浮窗模式）
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
        "auto_healing_runs": [], # 存放本輪 10 次循環的超詳細軌跡
        "failed_code_hashes": [] # 存放所有編譯失敗過的代碼特徵，防止鬼打牆
    }
    with open(p_json, 'w', encoding='utf-8') as f:
        json.dump(initial_brain, f, indent=2, ensure_ascii=False)
    print('✅ [第二步] 初始經驗（失敗+懸浮窗問題）注入完畢！')

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

    report = f"""# 📊 Gemini AI 運行狀況追蹤報告
產出時間: {datetime.datetime.now().isoformat()}
最終結果: {"🎉 成功通過 (第 " + str(success_cycle) + " 輪)" if success_cycle else "❌ 10輪皆失敗"}

## 📂 大腦目前記錄內容
```json
{brain_content}
