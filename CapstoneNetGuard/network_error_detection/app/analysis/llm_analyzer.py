
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class LLMAnalyzer:
    def __init__(self):
        model_name = "google/flan-t5-small"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def _llm_label(self, endpoint_name, result):
        prompt = f"""
You are a network monitoring classifier.

Choose exactly one label from this list:
NORMAL
HIGH_LATENCY
OUTAGE
REQUEST_FAILURE

Monitoring result:
Endpoint: {endpoint_name}
Status: {result.status}
Latency: {result.latency_ms}
HTTP Status: {result.http_status}
Error Type: {result.error_type}
Error Message: {result.error_message}

Answer with only one label.
"""

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=10,
            do_sample=False
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip().upper()

    def analyze_result(self, endpoint_name, result):
        raw_label = self._llm_label(endpoint_name, result)

        # Guardrails so obviously wrong answers get corrected
        if result.status == "OK" and result.http_status == 200:
            if result.latency_ms is not None and result.latency_ms >= 300:
                label = "HIGH_LATENCY"
                explanation = "The endpoint is reachable, but response time is higher than expected."
            else:
                label = "NORMAL"
                explanation = "The endpoint appears to be operating normally."
        elif result.status == "ERROR":
            if result.error_type in ["TIMEOUT", "REQUEST_ERROR"]:
                label = "OUTAGE"
                explanation = "The endpoint appears unreachable and may be experiencing an outage."
            else:
                label = "REQUEST_FAILURE"
                explanation = "The endpoint returned an error and may be experiencing a request failure."
        else:
            # fallback to LLM label if state is unclear
            if "HIGH_LATENCY" in raw_label:
                label = "HIGH_LATENCY"
                explanation = "The endpoint is reachable, but response time is higher than expected."
            elif "OUTAGE" in raw_label:
                label = "OUTAGE"
                explanation = "The endpoint appears unreachable and may be experiencing an outage."
            elif "REQUEST_FAILURE" in raw_label:
                label = "REQUEST_FAILURE"
                explanation = "The endpoint returned an error and may be experiencing a request failure."
            else:
                label = "NORMAL"
                explanation = "The endpoint appears to be operating normally."

        return raw_label, label, explanation
