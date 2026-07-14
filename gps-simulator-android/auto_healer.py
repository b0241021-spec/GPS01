# -*- coding: utf-8 -*-
# auto_healer.py
import os
import json
import datetime
import hashlib
import re

p_json = '../gemini_learning_context.json'

def get_content_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def mock_gemini_api_request(prompt_input, log_error):
    """
    這裡模擬 Gemini API 的真實決策與代碼輸出。
    """
    analysis = "偵測到 UI 變數命名 tvCustomCurrentGps 拼寫錯誤，將其修正為 tvCurrentGps，並追加 WindowManager 穿透 flag 以相容觸控監聽。"
    
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
    except Exception:
        return

    # 整理歷史上所有輪次的試錯記錄，這將會作為上下文餵給 Gemini
    history_context = ""
    if db.get('auto_healing_runs'):
        history_context = "\n=== 📚 前幾輪的試錯軌跡與失敗結果 (請勿重蹈覆轍) ===\n"
        for run in db['auto_healing_runs']:
            history_context += "【第 " + str(run.get('cycle_attempt', '?')) + " 輪】\n"
            history_context += " - 報錯內容: " + str(run.get('error_detected', '無')[:300]) + "...\n"
            history_context += " - AI 分析: " + str(run.get('gemini_analysis', '無')) + "\n"
            history_context += " - 結果: " + str(run.get('result', 'UNKNOWN')) + "\n"
            history_context += "---------------------------------------\n"

    analysis_result = ""
    final_suggested_code = ""
    prompt_sent_to_gemini = ""
    
    # 拉鋸重試迴圈：如果 Gemini 給的代碼跟「歷史上任何一次失敗版本」相同，直接打槍，要求重新設計
    for attempt in range(1, 5):
        prompt_sent_to_gemini = "=== 👑 任務指引 ===\n"
        prompt_sent_to_gemini += "你是一個具有增量學習能力的 Android 專家。請幫我修改當前編譯失敗的程式碼。\n"
        prompt_sent_to_gemini += "請仔細審視之前的初始知識與歷史上每一輪的失敗教訓，不要給出相同的程式碼！\n\n"
        
        prompt_sent_to_gemini += "=== 💡 初始經驗與地雷規則 ===\n"
        prompt_sent_to_gemini += json.dumps(db.get('initial_knowledge'), indent=2, ensure_ascii=False) + "\n"
        
        if history_context:
            prompt_sent_to_gemini += history_context
            
        prompt_sent_to_gemini += "\n=== 🚨 當前最新報錯日誌 ===\n" + str(log_error) + "\n"
        prompt_sent_to_gemini += "\n=== 📝 當前原始碼 ===\n" + str(original_code) + "\n"
        
        if attempt > 1:
            prompt_sent_to_gemini += "\n⚠️ [拒絕警報]：你剛剛給出的修改程式碼跟歷史失敗程式碼的 MD5 特徵完全重複！這意味著你的方案無效。請立刻給出完全不一樣的程式碼修改建議！"

        # 呼叫 Gemini 決策
        analysis_result, final_suggested_code = mock_gemini_api_request(prompt_sent_to_gemini, log_error)
        
        # 全局去重比對：檢查這個代碼的 Hash 是否存在於全局 failed_code_hashes 集合中
        suggested_hash = get_content_hash(final_suggested_code)
        
        if suggested_hash not in db.get('failed_code_hashes', []):
            print("💡 [要求1通過] 第 " + str(cycle) + " 輪：Gemini 給出了完全不重複的全新方案 (Attempt " + str(attempt) + ")。")
            break
        else:
            print("⛔ [要求1攔截] 第 " + str(cycle) + " 輪方案與歷史所有失敗代碼衝突！拒絕採用，重試中...")
    
    # 實體寫入通過全局重複性檢查的程式碼
    open(target_path, 'w', encoding='utf-8').write(final_suggested_code)

    # 確保每次修復時，都將「超詳細的軌跡」寫入大腦 JSON
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
    
    # 將當前寫入的程式碼特徵也追加到失敗候選清單中，防止未來重複
    new_hash = get_content_hash(final_suggested_code)
    if new_hash not in db['failed_code_hashes']:
        db['failed_code_hashes'].append(new_hash)

    with open(p_json, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
