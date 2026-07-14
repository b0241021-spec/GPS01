# -*- coding: utf-8 -*-
import os
import json
import datetime
import hashlib

p_json = '../gemini_learning_context.json'

def get_content_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def mock_gemini_api_request(prompt_input, log_error):
    analysis = "偵測到 UI 變數命名 tvCustomCurrentGps 拼寫錯誤，將其修正為 tvCurrentGps，並追加 WindowManager 穿透 flag。"
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

def heal_code_with_ai(cycle, target_path, log_error):
    if not os.path.exists(target_path):
        return

    original_code = open(target_path, 'r', encoding='utf-8', errors='ignore').read()

    try:
        db = json.load(open(p_json, 'r', encoding='utf-8'))
    except:
        return

    history_context = ""
    if db.get('auto_healing_runs'):
        history_context = "\n=== 📚 前幾輪的試錯軌跡與失敗結果 (請勿重蹈覆轍) ===\n"
        for run in db['auto_healing_runs']:
            history_context += f"【第 {run['cycle_attempt']} 輪】\n"
            history_context += f" - 報錯內容: {run['error_detected'][:300]}...\n"
            history_context += f" - AI 分析: {run['gemini_analysis']}\n"
            history_context += f" - 結果: {run['result']}\n"
            history_context += "---------------------------------------\n"

    analysis_result = ""
    final_suggested_code = ""
    prompt_sent_to_gemini = ""
    
    for attempt in range(1, 5):
        prompt_sent_to_gemini = "=== 👑 任務指引 ===\n"
        prompt_sent_to_gemini += "你是一個具有增量學習能力的 Android 專家。請幫我修改當前編譯失敗的程式碼。\n"
        prompt_sent_to_gemini += "請仔細審視之前的初始知識與歷史上每一輪的失敗教訓，不要給出相同的程式碼！\n\n"
        
        prompt_sent_to_gemini += "=== 💡 初始經驗與地雷規則 ===\n"
        prompt_sent_to_gemini += json.dumps(db.get('initial_knowledge'), indent=2, ensure_ascii=False) + "\n"
        
        if history_context:
            prompt_sent_to_gemini += history_context
            
        prompt_sent_to_gemini += f"\n=== 🚨 當前最新報錯日誌 ===\n{log_error}\n"
        prompt_sent_to_gemini += f"\n=== 📝 當前原始碼 ===\n{original_code}\n"
        
        if attempt > 1:
            prompt_sent_to_gemini += f"\n⚠️ [拒絕警報]：你剛剛給出的修改程式碼跟歷史失敗程式碼的 MD5 特徵完全重複！這意味著你的方案無效。請立刻給出完全不一樣的程式碼修改建議！"

        analysis_result, final_suggested_code = mock_gemini_api_request(prompt_sent_to_gemini, log_error)
        suggested_hash = get_content_hash(final_suggested_code)
        
        if suggested_hash not in db.get('failed_code_hashes', []):
            print(f'💡 [要求1通過] 第 {cycle} 輪：Gemini 給出了完全不重複的全新方案 (Attempt {attempt})。')
            break
        else:
            print(f'⛔ [要求1攔截] 第 {cycle} 輪方案與歷史所有失敗代碼衝突！拒絕編譯，重試中...')
    
    open(target_path, 'w', encoding='utf-8').write(final_suggested_code)

    run_log = {
        "cycle_attempt": cycle,
        "timestamp": datetime.datetime.now().isoformat(),
        "error_detected": log_error,
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
