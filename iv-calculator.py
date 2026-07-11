import math
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 前端網頁 HTML 範本（已更新標題、免責聲明、創作者資訊）
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>護理臨床點滴滴數計算工具</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            background-color: #f0f4f8; 
            padding: 20px; 
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .card { 
            background: white; 
            padding: 30px; 
            border-radius: 12px; 
            width: 100%;
            max-width: 480px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.06); 
        }
        h2 { 
            color: #2c3e50; 
            text-align: center; 
            margin-bottom: 25px;
            font-size: 22px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #34495e; }
        input, select { 
            width: 100%; 
            padding: 12px; 
            box-sizing: border-box; 
            border: 1px solid #cbd5e1; 
            border-radius: 6px; 
            font-size: 16px;
            background-color: #f8fafc;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #3498db;
            background-color: #ffffff;
        }
        button { 
            width: 100%; 
            padding: 14px; 
            background-color: #3498db; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            font-size: 18px; 
            font-weight: bold;
            cursor: pointer; 
            margin-top: 10px; 
            transition: background 0.2s;
        }
        button:hover { background-color: #2980b9; }
        .result-zone { 
            margin-top: 25px; 
            padding-top: 20px; 
            border-top: 2px dashed #e2e8f0; 
        }
        .result-item { 
            font-size: 16px; 
            margin-bottom: 15px; 
            color: #475569; 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .highlight { 
            font-weight: bold; 
            color: #e74c3c; 
            font-size: 24px; 
        }
        .unit { font-size: 14px; color: #64748b; font-weight: normal; margin-left: 5px; }
        
        /* 免責聲明樣式 */
        .notice {
            background-color: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            font-size: 13px;
            color: #78350f;
            border-radius: 4px;
            margin-top: 20px;
            line-height: 1.5;
        }
        
        /* 創作者資訊樣式 */
        .creator-info {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 12px;
            font-size: 12px;
            color: #475569;
            border-radius: 6px;
            margin-top: 15px;
            line-height: 1.6;
        }
        .creator-info a {
            color: #3498db;
            text-decoration: none;
        }
        .creator-info a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>護理臨床點滴滴數計算工具</h2>
    
    <div class="form-group">
        <label for="volume">點滴總量 (mL):</label>
        <input type="number" id="volume" placeholder="例如: 500" value="500" min="1">
    </div>
    
    <div class="form-group">
        <label for="hours">預計滴注時間 (小時):</label>
        <input type="number" id="hours" placeholder="例如: 8" value="8" step="0.5" min="0.1">
    </div>
    
    <div class="form-group">
        <label for="factor">點滴套管係數 (gtt/mL):</label>
        <select id="factor">
            <option value="20" selected>20 滴/mL (一般成人用)</option>
            <option value="15">15 滴/mL (常規大滴套管)</option>
            <option value="10">10 滴/mL (血品輸血用)</option>
            <option value="60">60 滴/mL (微滴/小兒科/ICU用)</option>
        </select>
    </div>
    
    <button onclick="sendCalculation()">立即計算滴數</button>
    
    <div class="result-zone">
        <div class="result-item">
            <span>每小時流速：</span>
            <span><span id="res_flow" class="highlight">0</span><span class="unit">mL/hr</span></span>
        </div>
        <div class="result-item">
            <span>每分鐘滴數：</span>
            <span><span id="res_gtt" class="highlight">0</span><span class="unit">gtt/min</span></span>
        </div>
        <div class="result-item">
            <span>現場調校輔助：</span>
            <span>約 <span id="res_sec" class="highlight">0</span> <span class="unit">秒滴 1 滴</span></span>
        </div>
    </div>
    
    <!-- 免責聲明 -->
    <div class="notice">
        <strong>免責聲明：</strong>本計算工具僅作為教學輔助使用，計算結果則務必依據病人狀況及醫院標準流程執行，相關臨床疑問請諮詢您的臨床指導教師或臨床護理人員。
    </div>

    <!-- 創作者資訊 -->
    <div class="creator-info">
        <strong>創作者資訊：</strong><br>
        本網頁由 和科技大學護理系學生 魏啟軒，使用Python程式語言開發製作及維護管理。如有任何疑問或建議，歡迎來信 <a>href="mailto:t41301106@go.meiho.edu.tw">t41301106@go.meiho.edu.tw</a> 。
    </div>
</div>

<script>
function sendCalculation() {
    const payload = {
        total_volume: document.getElementById('volume').value,
        total_hours: document.getElementById('hours').value,
        drop_factor: document.getElementById('factor').value
    };

    fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            document.getElementById('res_flow').innerText = data.flow_rate_ml_hr;
            document.getElementById('res_gtt').innerText = data.gtt_per_min;
            document.getElementById('res_sec').innerText = data.seconds_per_drop;
        } else {
            alert("計算失敗: " + data.error);
        }
    })
    .catch(err => {
        console.error("Error:", err);
        alert("無法連線到後端伺服器，請確認 VS Code 中的 Flask 是否正在運行。");
    });
}
</script>

</body>
</html>
"""

# ==========================================
# 後端 Python 路由與核心計算邏輯
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        total_volume = float(data.get('total_volume', 0))
        total_hours = float(data.get('total_hours', 0))
        drop_factor = int(data.get('drop_factor', 20))
        if drop_factor not in [10, 15, 20, 60]:
            return jsonify({'success': False, 'error':'無效的點滴套管係數，請選擇 10、15、20、60之一'}),400
        
        if total_volume <= 0 or total_hours <= 0:
            return jsonify({
                "success": False,
                "error":"點滴總量及輸注時間必須大於零，請重新輸入"
            }),400

        flow_rate_ml_hr = round(total_volume / total_hours, 1)
        
        total_minutes = total_hours * 60
        raw_gtt_per_min = (total_volume * drop_factor) / total_minutes
        gtt_per_min = math.floor(raw_gtt_per_min + 0.5)
        
        if gtt_per_min > 0:
            seconds_per_drop = round(60 / gtt_per_min, 1)
        else:
            seconds_per_drop = 0.0

        return jsonify({
            "success": True,
            "flow_rate_ml_hr": flow_rate_ml_hr,
            "gtt_per_min": gtt_per_min,
            "seconds_per_drop": seconds_per_drop
        })

    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "欄位格式輸入錯誤，請輸入數字"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run()