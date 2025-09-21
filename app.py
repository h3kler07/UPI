from flask import Flask, render_template, request, jsonify
import urllib.parse, re, datetime

app = Flask(__name__)
PASSWORD = "1234"

# ---------- Helper: Parse UPI String ----------
def parse_upi_string(data: str) -> dict:
    result = {}
    if not data:
        return result
    if data.startswith("upi://") or data.startswith("UPI://"):
        parsed = urllib.parse.urlparse(data)
        qs = urllib.parse.parse_qs(parsed.query)
        for k, v in qs.items():
            if v:
                result[k] = v[0]
        return result
    if "upi://" in data.lower():
        m = re.search(r"upi://[^\s\']+", data, flags=re.IGNORECASE)
        if m:
            return parse_upi_string(m.group(0))
    pairs = re.findall(r"([a-zA-Z]{1,3})=([^&\s]+)", data)
    if pairs:
        for k, v in pairs:
            result[k] = urllib.parse.unquote_plus(v)
        if any(k.lower() in ("pa", "pn", "am") for k in result.keys()):
            return result
    try:
        decoded = urllib.parse.unquote_plus(data)
        if decoded != data:
            return parse_upi_string(decoded)
    except:
        pass
    m = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)", data)
    if m:
        result.setdefault('pa', m.group(1))
    return result

@app.route("/")
def index():
    return render_template("index.html")
amount = 0
@app.route("/process_qr", methods=["POST"])
def process_qr():
    data = request.json.get("data")
    parsed = parse_upi_string(data)
    return jsonify(parsed)

@app.route("/verify_password", methods=["POST"])
def verify_password():
    password = request.json.get("password")
    amount = request.json.get("amount")
    payee = request.json.get("payee")
    if password == PASSWORD:
        return jsonify({
            "status": "success",
            "timestamp": datetime.datetime.now().strftime("%d %B %Y at %I:%M %p"),
            "amount": amount,
            "payee": payee
        })
    else:
        return jsonify({"status": "error", "message": "Incorrect password"}), 401

if __name__ == "__main__":
    app.run(debug=True)
