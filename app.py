from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/games_over_time.html')
def serve_plot():
    # Serve the already saved Plotly HTML from the static directory
    return send_from_directory('static', 'games_over_time.html')

if __name__ == '__main__':
    app.run(debug=True)