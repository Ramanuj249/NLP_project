from schema import DocumentRequest

def build_prompt(data: DocumentRequest)->str:
    qa_sections = ""

    for item in data.answers:
        qa_sections += f"- {item.question}\n Answer: {item.answer}\n\n"

    prompt = f"""
## Role
You are a professional document writer and industry expert.  
Your task is to generate a complete, end-to-end document using the information provided by the user.

The final document MUST be written entirely in Markdown format.

---

## User Inputs
The user will provide the following inputs:

1. Document Category: {data.category}

2. Document Type: {data.document_type}

3. Document Name: {data.document_name}

4. Document Structure / Components: {data.components}

5. User Responses to Guided Questions and its answers: {data.answers}

---

## Responsibilities
Using the inputs above, you must:

- Create a fully complete document from header to footer
- Follow the exact document structure provided by the user
- Use the user responses and company information to enrich the content
- Ensure industry-appropriate length, tone, and depth
- Write content that is ready for real-world professional use

---

## Mandatory Markdown Formatting Rules
The document MUST use proper Markdown formatting:

- `#` for the main document title
- `##` and `###` for headings and subheadings
- **Bold text** for emphasis
- Bullet points using `-` or `*`
- Numbered lists where applicable
- Properly formatted Markdown tables where relevant
- Clear spacing and readable structure

---

## Document Content Requirements
Include the following where applicable:

- Document Title (using the provided Document Name)
- Document Metadata (version, date, author, company name)
- Introduction / Overview
- Main content sections based on the provided structure
- Tables, bullet points, and structured content where useful
- Conclusion / Summary
- Footer (disclaimer, confidentiality notice, or company reference)

---

## Output Rules
- Output ONLY the final document
- Output ONLY in Markdown format
- Do NOT explain reasoning
- Do NOT restate user inputs
- Do NOT mention that you are an AI
- Do NOT add content outside the provided structure

---

## Final Instruction
Generate a professional, polished, end-to-end document in Markdown format, strictly following the user’s inputs and structure.
"""
    return prompt.strip()