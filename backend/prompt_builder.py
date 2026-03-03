# from frountend.app import instruction
from schema import DocumentRequest, RefineSectionRequest

# Document Scale Map
DOCUMENT_SCALE_MAP = {
    "POLICY": {
        "pages": "4 to 8 pages",
        "tone": "formal, authoritative, and compliance-focused",
        "style": "structured prose with clear rules, obligations, and consequences",
    },
    "PROCEDURE": {
        "pages": "3 to 6 pages",
        "tone": "clear, instructional, and step-oriented",
        "style": "numbered steps, checklists, and role-based instructions",
    },
    "GUIDE": {
        "pages": "8 to 15 pages",
        "tone": "informative, educational, and practical",
        "style": "detailed explanations, examples, best practices, and visual structure",
    },
    "PLAN": {
        "pages": "4 to 8 pages",
        "tone": "strategic, goal-oriented, and actionable",
        "style": "structured sections with timelines, stakeholders, and measurable outcomes",
    },
    "AGREEMENT": {
        "pages": "2 to 4 pages",
        "tone": "precise, legally accurate, and neutral",
        "style": "concise clauses, defined terms, and legally standard language",
    },
    "RECORD": {
        "pages": "1 to 3 pages",
        "tone": "factual, objective, and concise",
        "style": "brief structured sections, no unnecessary elaboration",
    },
}
# Component Depth Map
COMPONENT_DEPTH_MAP = {
    # --- Shared / Common ---
    "Purpose": "Write 1 to 2 concise paragraphs. Clearly state why this document exists and what it achieves.",
    "Scope": "Write 1 to 2 paragraphs. Define who and what this document applies to. Use bullet points if listing multiple groups.",
    "Roles & Responsibilities": "Write in detail. Cover every relevant role. Use a table or clearly structured bullet list per role. Each role must have at least 3 to 5 responsibilities.",
    "Review & Updates": "Keep concise — 1 short paragraph. State the review frequency and who owns the review process.",
    "Exceptions": "Keep concise — 2 to 4 sentences or a short bullet list. Clearly state what exceptions exist and how they are handled.",
    "Compliance & Enforcement": "Write 2 to 3 paragraphs. Cover consequences of non-compliance, enforcement mechanisms, and escalation paths.",

    # --- Policy Specific ---
    "Policy Title": "Use as the main document title in the title block. Format as a heading with version, date, author, and company.",
    "Policy Statement": "Write 2 to 3 paragraphs. This is the core of the policy — state the rules, obligations, and organizational stance clearly and authoritatively.",
    "Approval & Effective Date": "Keep concise. State who approved the document, when it was approved, and its effective date.",

    # --- Procedure Specific ---
    "Basic Company Information": "Write 1 short paragraph. Include company name, industry, and any relevant operational context.",
    "Preconditions & Triggers": "Write a bullet list of 4 to 6 items. Clearly state what conditions or events trigger this procedure.",
    "Required Tools or Inputs": "Write a structured bullet list. List every tool, system, document, or input required before starting the procedure.",
    "Step-by-Step Procedure": "This is the core section — write in comprehensive numbered steps. Each step must be clearly described. Include substeps where needed. Do not summarize — write every action explicitly.",
    "Exceptions & Escalation": "Write 2 to 3 paragraphs or a structured list. Cover what happens when the standard procedure cannot be followed and who to escalate to.",
    "Review & Ownership": "Keep concise. State who owns this procedure, when it was last reviewed, and when the next review is due.",

    # --- Guide Specific ---
    "Document Header": "Use as the title block. Include document name, version, date, author, intended audience, and department.",
    "Purpose & Scope": "Write 2 to 3 paragraphs. Combine purpose and scope into a flowing section that clearly sets context for the reader.",
    "Intended Audience": "Write 1 short paragraph or a bullet list. Clearly identify who this guide is written for.",
    "Core Content": "This is the largest and most important section. Write extensively with subsections, examples, diagrams (described in text), and detailed explanations. This section should represent at least 40% of the total document.",
    "Tools, Resources & References": "Write a structured list with descriptions. Include every tool, platform, or reference the reader needs.",
    "Best Practices & Recommendations": "Write 6 to 10 detailed best practice points. Each point must be explained — not just listed.",
    "Compliance, Security & Legal Notes": "Write 2 to 3 paragraphs. Cover any legal, regulatory, or security considerations relevant to this guide.",
    "Change Log / Revision History": "Include a markdown table with columns: Version, Date, Author, Changes Made.",

    # --- Plan Specific ---
    "Document Title": "Use as the title block. Include plan name, version, date, author, and sponsoring department.",
    "Purpose / Objective": "Write 1 to 2 paragraphs. State the goal of this plan and what success looks like.",
    "Scope / Context": "Write 1 to 2 paragraphs. Define the boundaries of this plan — what is included and what is not.",
    "Key Stakeholders / Team": "Write a table with columns: Name/Role, Responsibility, Contact. List all key people involved.",
    "Approach / Strategy / Steps": "This is the core section. Write in detail — cover the strategy, methodology, and every major step or phase. Use numbered steps or subsections.",
    "Timeline / Schedule (if applicable)": "Include a markdown table with columns: Phase/Milestone, Start Date, End Date, Owner. Be specific.",
    "Risks / Challenges / Dependencies": "Write a table with columns: Risk/Challenge, Likelihood, Impact, Mitigation. Cover at least 5 to 8 items.",
    "Expected Outcomes / Success Metrics": "Write a bullet list of 5 to 8 measurable outcomes. Each must be specific and verifiable.",
    "Additional Notes / References": "Keep concise. Include any supplementary information, references, or links.",

    # --- Agreement Specific ---
    "Title & Parties": "Write the title block clearly. Identify all parties with full legal names, addresses, and roles (e.g. Client, Service Provider).",
    "Commercial Terms": "Write precisely. Cover payment amounts, schedules, invoicing terms, and penalties. Use a table if multiple items.",
    "Confidentiality & Data": "Write 2 to 3 tight paragraphs. Cover what is confidential, how it must be handled, and the duration of the obligation.",
    "Ownership & Rights": "Write 1 to 2 paragraphs. Clearly state who owns deliverables, IP, and any pre-existing materials.",
    "Term & Termination": "Write 1 to 2 paragraphs. State the duration of the agreement and conditions under which either party can terminate.",
    "Legal & General Terms": "Write standard legal boilerplate — governing law, dispute resolution, entire agreement clause, severability, and amendments.",
    "Scope & Obligations": "Write 2 to 3 paragraphs. Define exactly what each party is obligated to do. Be specific and unambiguous.",

    # --- Record Specific ---
    "Context": "Write 1 short paragraph. Provide background and the situation that led to this record.",
    "Main Content": "This is the core section. Write all relevant facts, findings, or information in structured prose or bullet points. Be factual and objective.",
    "Constraints & Considerations": "Write a bullet list of 3 to 5 items. State any limitations, assumptions, or special considerations.",
    "Outcome / Usage": "Write 1 short paragraph. State how this record will be used or what decisions it supports.",
    "Version & Updates": "Include a small table: Version, Date, Author, Summary of Changes.",
}


def build_prompt(data: DocumentRequest)->str:
    qa_sections = ""

    for item in data.answers:
        qa_sections += f"- {item.question}\n Answer: {item.answer}\n\n"

    # Get scale and depth guidance for this document type
    scale = DOCUMENT_SCALE_MAP.get(data.document_type, {})
    scale_guidance = f"""
    -Expected length : {scale.get('pages', 'appropriate length for the document type')}
    - Tone: {scale.get('tone', 'professional and formal')}
    - Writing Style: {scale.get('style', 'structured and clear')}
    """.strip()

    # components of the document type
    components_list = [c.strip() for c in data.components.strip("'[]").split(",")]
    component_guidance = ""
    for component in components_list:
        instruction = COMPONENT_DEPTH_MAP.get(component)
        if instruction:
            component_guidance += f"- **{component}**: {instruction}\n"
        else:
            component_guidance += f"- **{component}**: Write with professional depth appropriate to the document type. Do not leave this section thin.\n"

    prompt = f"""
    ## Role
    You are a senior professional document writer and industry domain expert.
    Your task is to generate a complete, comprehensive, publication-ready document
    using the user's inputs as a foundation — enriched with your own professional
    knowledge, industry best practices, and expert insights.
    
    ---
    
    ## User Inputs
    
    1. Document Category: {data.category}
    2. Document Type: {data.document_type}
    3. Document Name: {data.document_name}
    4. Document Structure / Components: {data.components}
    5. Guided Q&A Responses:
    {qa_sections}
    
    ---
    
    ## Document Scale & Tone
    
    This is a **{data.document_type}** document. You must write it to the following standard:
    
    {scale_guidance}
    
    Do NOT write a document that is shorter or thinner than this standard.
    Do NOT pad with filler — every word must earn its place.
    
    ---
    
    ## Per-Section Writing Instructions
    
    For each component below, follow the specific depth and style instruction provided.
    These are non-negotiable — they define the minimum quality bar for each section:
    
    {component_guidance}
    
    ---
    
    ## Your Two-Layer Writing Mandate
    
    ### Layer 1 — User-Driven Content (Personalized)
    For sections that require company-specific or user-specific details:
    - Use the Q&A responses and document structure to write accurate, tailored content
    - Infer company details (industry, scale, culture, goals) from the answers provided
    - Where details are implied but not stated, make reasonable, professional inferences
    
    ### Layer 2 — Expert-Augmented Content (Knowledge-Driven)
    You MUST independently contribute the following where applicable:
    
    - **Industry context**: Add relevant background, market standards, regulatory norms,
      or domain-specific frameworks that a professional in {data.category} would include
    - **Best practice sections**: If a component is a standalone concept that does not
      require company-specific data, write it fully from your expert knowledge
    - **Elaboration**: Expand every section with professional depth — definitions,
      rationale, implications, examples, and implementation guidance where relevant
    - **Missing but expected components**: If a standard document of this type
      ({data.document_type}) conventionally includes sections not listed by the user,
      ADD them with a note: `<!-- Expert Addition -->`. Do not omit content that a
      professional reader would expect to find
    
    ---
    
    ## Mandatory Markdown Formatting
    
    - `#` — Main document title
    - `##` / `###` — Section and subsection headings
    - **Bold** for key terms and emphasis
    - `-` or `*` for bullet points
    - Numbered lists for sequential steps or ranked items
    - Markdown tables for comparative or structured data
    - Horizontal rules (`---`) between major sections
    - Code blocks where technical content appears
    
    ---
    
    ## Document Structure Requirements
    
    Include ALL of the following:
    
    - **Title Block**: Document name, version, date, author, company (inferred or stated)
    - **Executive Summary / Overview**: High-level purpose and scope
    - **Main Sections**: Based on provided components — fully written and expert-enriched
    - **Standalone Sections**: Any industry-standard sections you add from your own knowledge
    - **Supporting Elements**: Tables, frameworks, checklists, or matrices where useful
    - **Conclusion / Recommendations**: Actionable takeaways
    - **Appendix** (if applicable): Glossary, references, or supplementary content
    - **Footer**: Confidentiality notice, disclaimer, or document control reference
    
    ---
    
    ## Autonomy Rules
    
    | Situation | Your Action |
    |---|---|
    | Section needs company data → provided | Write using the provided data |
    | Section needs company data → not provided | Infer from context or use professional placeholders |
    | Section is a standalone concept | Write fully from your expert knowledge |
    | Standard section missing from user's list | Add it with `<!-- Expert Addition -->` tag |
    | Content is thin or vague in inputs | Expand with industry depth and best practices |
    
    ---
    
    ## Output Rules
    
    - Output ONLY the final Markdown document
    - Do NOT explain your reasoning or process
    - Do NOT restate user inputs verbatim
    - Do NOT mention that you are an AI or reference this prompt
    - DO write as a credentialed human expert authoring a real deliverable
    
    ---
    
    ## Final Directive
    
    Generate an authoritative, end-to-end professional document in Markdown.
    Use the user's inputs as your foundation. Augment freely with your domain expertise.
    Every section must meet the depth standard defined above — detailed, purposeful,
    and ready for real-world professional use.
    """
    return prompt.strip()

def build_refine_section_prompt(data:RefineSectionRequest)->str:
    prompt = f"""
    You are a professional document editor.

    Your job is to improve the section below based on the user's instruction.

    **Section:**
    {data.section_text}

    **Instruction:**
    {data.instruction}

    **Rules:**
    - Only apply what the instruction asks
    - Do not add anything new on your own
    - Keep the same tone, style, and structure
    - Return only the improved section, nothing else
    """
    return prompt.strip()