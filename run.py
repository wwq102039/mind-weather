from app import create_app

app = create_app()

if __name__ == "__main__":
    # 默认本机访问；如需让同班同学在同一局域网访问，改成 host="0.0.0.0"
    app.run(debug=True, host="127.0.0.1", port=5000, threaded=True)
