import os
from dotenv import load_dotenv
from ollama_python.endpoints import GenerateAPI

load_dotenv(".env")
OLLAMA_URL = os.environ.get('OLLAMA_URL')

def analyze_pr_diff(code: bytes):
    """
    Analyze a GitHub PR diff for code style, bugs, performance, and best practices.

    Parameters:
    - code (str): The GitHub PR diff code

    Returns:
    - dict: Analysis results in the specified output format
    """

    # Define the prompt template for the analysis
    full_prompt = (
        "Analyze the following GitHub PR diff and identify issues including: "
        "1. Code style and formatting issues. "
        "2. Potential bugs or errors. "
        "3. Performance improvements. "
        "4. Best practices violations. "
        "Output your findings in JSON format with the structure:\n"
        "{{\"files\": [{{\"name\": <filename>,\"issues\": [{{\"type\": <style|bug|performance|best_practice>,\"line\": <line_number>,\"description\": <description>, \"suggestion\": <suggestion>}}]}}],\"summary\": {{\"total_files\": <int>,\"total_issues\": <int>,\"critical_issues\": <int>}}}}.\n"
        f"\n\nCode Diff:\n{code}"
    )

    # Generate response from Llama3.2
    api = GenerateAPI(base_url=OLLAMA_URL, model="llama3.2")
    result = api.generate(prompt=full_prompt, format="json")

    return result.response

# Example usage
if __name__ == "__main__":
    code_diff = b"""diff --git a/main.py b/main.py
index 83db48f..bf9f3ad 100644
--- a/main.py
+++ b/main.py
@@ -13,6 +13,7 @@ def process_data(data):
     # Process the data
     result = None
     if data is not None:
+        print(data)
         result = data * 2
     return result

@@ -22,6 +23,7 @@ def main():
     data = None
     process_data(data)
"""
    result = analyze_pr_diff(code_diff)
    print(result)
