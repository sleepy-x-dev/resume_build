# ATSBoost | Intelligent Heuristic Analysis & Resume Optimization

**ATSBoost** is a high-fidelity semantic engine designed to bridge the gap between human-professional narratives and **Applicant Tracking System (ATS)** deterministic parsers. By leveraging **Neural NLP pipelines**, the system deconstructs unstructured document hierarchies to maximize keyword alignment and structural integrity.

---

### System Architecture

* **Semantic Parser**: Utilizes **Spacy** and **NLP heuristics** for high-precision entity recognition and technical competency extraction.
* **Document Deconstruction**: Employs **PDFMiner** to extract metadata while preserving logical flow.
* **LaTeX Synthesis**: A dedicated engine that converts optimized data into high-parsability, industry-standard LaTeX templates.

---

### Environment Configuration

The system requires an automated handshake with external LLM APIs for advanced heuristic scoring.

1.  **Initialize Environment File**:
    ```bash
    cp .env.example .env
    ```
2.  **Configure Credentials**:
    Open the `.env` file and replace the placeholder with your authorized API key:
    ```env
    API_KEY=your_high_fidelity_api_key_here
    ```

---

### Execution Protocol

To maintain high-concurrency and process-level isolation, follow the deployment steps below.

#### Backend Intelligence (Flask)
The core logic resides in a micro-service architecture.
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
