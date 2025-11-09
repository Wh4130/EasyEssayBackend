from flask import Flask, jsonify, request

app = Flask("document_summarizer")

@app.route("/summarize", methods=["POST"])
def summarize_document():
    data = request.get_json()
    document = data.get("document", "")
    
    # Simple summarization logic (for demonstration purposes)
    summary = document[:75] + "..." if len(document) > 75 else document
    
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)