# -*- coding: utf-8 -*-
import os
import json
import datetime
import hashlib

p_json = '../gemini_learning_context.json'

def get_content_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def mock_gemini_api_request(prompt_input, log_error, failed_hashes):
    analysis = "偵測到遺失懸浮窗必要 flag 或 UI 變數命名拼寫錯誤，進行安全降級與相容性補正。"
    mock_path = 'app/src/main/java/com/gpssimulator/MainActivity.kt'
    current_code = open(mock_path, 'r', encoding='utf-8', errors='ignore').read() if os.path.exists(mock_path) else ""
    
    suggested_code = current_code
    if "tvCustomCurrentGps" in log_error or "tvCustomCurrentGps" in current_code:
        suggested_code = suggested_code.replace("tvCustomCurrentGps", "tvCurrentGps")
    if "WindowManager.LayoutParams" in current_code and "FLAG_NOT_FOCUSABLE" not in current_code:
        suggested_code = suggested_code.replace(
            'WindowManager.LayoutParams(',
            'WindowManager.LayoutParams(\n            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,\n            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,\n            '
        )
    return analysis, suggested_code

def heal_code_with_ai(cycle, target_path):
    if not os.path.exists(target_path):
        return

    log_error = open('gradle_build.log', 'r', encoding='utf-8', errors='ignore').read()[-4000:]
    original_code = open(target_path, 'r', encoding='utf-8', errors='ignore').read()

    try:
        db = json.load(open(p_json, 'r', encoding='utf-8'))
    except:
        return

    analysis_result = ""
    final_suggested_code = ""
    prompt_sent_to_gemini = ""
    
    for attempt in range(1, 5):
        prompt_sent_to_gemini = f"=== 任務指引 ===\n請幫我修改編譯失敗的原始碼。不要犯以下錯誤：\n"
        prompt_sent_to_gemini += json.dumps(db.get('initial_knowledge'), indent=2, ensure_ascii=False)
        prompt_sent_to_gemini += f"\n\n=== 報錯日誌 ===\n{log_error}\n\n=== 原始碼 ===\n{original_code}"
        
        if attempt > 1:
            prompt_sent_to_gemini += f"\n⚠️ 警告：方案與歷史失敗版本重複，請重新思考給出新建議！"

        analysis_result, final_suggested_code = mock_gemini_api_request(
            prompt_sent_to_gemini, log_error, db.get('failed_code_hashes', [])
        )
        suggested_hash = get_content_hash(final_suggested_code)
        
        if suggested_hash not in db.get('failed_code_hashes', []):
            print(f'💡 [要求1通過] 成功得到全新修改方案（Attempt {attempt}）。')
            break
        else:
            print(f'⛔ [要求1攔截] 第 {cycle} 輪方案重複！拒絕採用，重寫中...')
    
    open(target_path, 'w', encoding='utf-8').write(final_suggested_code)

    run_log = {
        "cycle_attempt": cycle,
        "timestamp": datetime.datetime.now().isoformat(),
        "error_detected": log_error[-1000:],
        "prompt_fed_to_gemini": prompt_sent_to_gemini,
        "gemini_analysis": analysis_result,
        "gemini_suggested_code": final_suggested_code,
        "result": "FAILED_HEALED_AND_RETRIED"
    }
    db['auto_healing_runs'].append(run_log)
    
    new_hash = get_content_hash(final_suggested_code)
    if new_hash not in db['failed_code_hashes']:
        db['failed_code_hashes'].append(new_hash)

    with open(p_json, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
