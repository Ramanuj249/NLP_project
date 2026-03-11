from schema import DocumentRequest, RefineSectionRequest

# Document Scale Map
DOCUMENT_SCALE_MAP = {
    "POLICY": {
        "pages": "8 to 16 pages",
        "tone": "formal, authoritative, and compliance-focused",
        "style": "structured prose with clear rules, obligations, and consequences. Every section must be exhaustive and leave no ambiguity.",
    },
    "PROCEDURE": {
        "pages": "6 to 12 pages",
        "tone": "clear, instructional, and step-oriented",
        "style": "numbered steps, checklists, and role-based instructions. Every step must be broken down to the smallest actionable detail.",
    },
    "GUIDE": {
        "pages": "15 to 30 pages",
        "tone": "informative, educational, and practical",
        "style": "detailed explanations, examples, best practices, and visual structure. Include real world examples, case studies, and detailed walkthroughs.",
    },
    "PLAN": {
        "pages": "8 to 16 pages",
        "tone": "strategic, goal-oriented, and actionable",
        "style": "structured sections with timelines, stakeholders, and measurable outcomes. Every phase must be detailed with clear ownership and measurable outcomes.",
    },
    "AGREEMENT": {
        "pages": "4 to 8 pages",
        "tone": "precise, legally accurate, and neutral",
        "style": "concise clauses, defined terms, and legally standard language. Every clause must be comprehensive and legally thorough.",
    },
    "RECORD": {
        "pages": "3 to 6 pages",
        "tone": "factual, objective, and concise",
        "style": "brief structured sections, no unnecessary elaboration. Every fact must be supported with context and evidence.",
    },
}


# Component Depth Map
COMPONENT_DEPTH_MAP = {

    # ─────────────────────────────────────────────
    # Shared / Common
    # ─────────────────────────────────────────────
    "Purpose": "Write 1 to 2 concise paragraphs. Clearly state why this document exists and what it achieves. Be specific to the UCaaS industry context.",
    "Scope": "Write 1 to 2 paragraphs. Define who and what this document applies to. Use bullet points if listing multiple groups. Include UCaaS specific roles and teams where relevant.",
    "Roles & Responsibilities": "Write in detail. Cover every relevant role. Use a table or clearly structured bullet list per role. Each role MUST have at least 3 to 5 responsibilities. Do NOT leave any role with a single line.",
    "Review & Updates": "Keep concise — 1 short paragraph. State the review frequency and who owns the review process.",
    "Exceptions": "Keep concise — 2 to 4 sentences or a short bullet list. Clearly state what exceptions exist and how they are handled.",
    "Compliance & Enforcement": "Write 2 to 3 paragraphs. Cover consequences of non-compliance, enforcement mechanisms, and escalation paths. Reference UCaaS industry regulatory standards where applicable.",
    "Introduction": "Write 2 to 3 paragraphs. Provide a comprehensive introduction to the document — background, context, and why this document is important for the organization and UCaaS industry.",
    "Definitions & Terminology": "Write a structured glossary table with columns: Term, Definition. Include at least 10 to 15 UCaaS specific terms relevant to this document.",
    "Governing Principles": "Write 4 to 6 detailed principles that guide this document. Each principle must have a title and 2 to 3 sentences of explanation.",
    "Implementation Guidelines": "Write a comprehensive section covering how this document should be implemented across the organization. Include phases, timelines, and ownership.",
    "Monitoring & Reporting": "Write 2 to 3 paragraphs. Cover how compliance or progress will be monitored, what metrics will be tracked, and how results will be reported.",
    "Training & Awareness": "Write 2 to 3 paragraphs. Cover what training is required, who needs it, how it will be delivered, and how completion will be tracked.",
    "Document Control": "Write a structured section covering document ownership, review cycle, version control, and distribution list.",

    # ─────────────────────────────────────────────
    # Policy Specific
    # ─────────────────────────────────────────────
    "Policy Title": "Use as the main document title in the title block. Format as a heading with version, date, author, and company.",
    "Executive Summary": "Write 2 to 3 paragraphs. Summarize the entire policy — why it exists, who it applies to, and what it mandates. A reader should understand the full policy from this section alone.",
    "Policy Statement": "Write 2 to 3 paragraphs. This is the core of the policy — state the rules, obligations, and organizational stance clearly and authoritatively. Be direct and unambiguous. Include specific rules for every scenario — what is allowed, what is prohibited, and what requires approval.",
    "Approval & Effective Date": "Keep concise. State who approved the document, when it was approved, and its effective date.",
    "Exceptions & Special Cases": "Write 3 to 5 bullet points. Each exception must be clearly defined with conditions and approval requirements.",
    "Related Policies & References": "Write a structured list. Reference all related internal policies, industry standards, and regulatory frameworks relevant to this policy.",
    "Policy Objectives": "Write 4 to 6 specific, measurable objectives this policy aims to achieve. Each objective must be tied to a business or compliance outcome.",
    "Legal & Regulatory Framework": "Write 2 to 3 paragraphs. Reference all applicable laws, regulations, and industry standards that this policy is built upon. Include UCaaS specific regulations.",
    "Communication & Rollout Plan": "Write a structured section. Cover how this policy will be communicated to all stakeholders, training requirements, and acknowledgment process.",
    "Non-Compliance Matrix": "Write a detailed table with columns: Violation Type, Example, Consequence, Escalation Path. Cover at least 6 to 8 violation scenarios.",

    # ─────────────────────────────────────────────
    # Procedure Specific
    # ─────────────────────────────────────────────
    "Basic Company Information": "Write 1 short paragraph. Include company name, UCaaS industry context, and relevant operational background.",
    "Preconditions & Triggers": "Write a bullet list of 4 to 6 items. Clearly state what conditions or events trigger this procedure.",
    "Required Tools or Inputs": "Write a structured bullet list. List every tool, system, document, or input required before starting the procedure. Include UCaaS specific platforms and tools.",
    "Health & Safety Considerations": "Write 2 to 3 bullet points. Cover any health, safety, or compliance considerations relevant to this procedure.",
    "Step-by-Step Procedure": "THIS IS THE MOST CRITICAL SECTION. Write comprehensive numbered steps. Every single action must be explicitly described — do NOT summarize or skip steps. Include substeps where needed. Each step must include: the action, who performs it, what tool or system is used, and what the expected outcome is.",
    "Quality Checks & Verification": "Write 3 to 5 verification points. State exactly what must be checked and how to confirm each step was done correctly.",
    "Exceptions & Escalation": "Write 2 to 3 paragraphs or a structured list. Cover what happens when the standard procedure cannot be followed and who to escalate to.",
    "Related Documents & References": "Write a structured list. Reference all related procedures, templates, and documents.",
    "Review & Ownership": "Keep concise. State who owns this procedure, when it was last reviewed, and when the next review is due.",
    "Process Overview": "Write a high level summary of the entire procedure in 1 to 2 paragraphs. Include a process flow description — start to finish.",
    "Risk & Controls": "Write a table with columns: Step, Risk, Control Measure. Cover every major step in the procedure.",
    "Performance Metrics": "Write 3 to 5 measurable metrics that indicate this procedure is being followed correctly and efficiently.",
    "Continuous Improvement": "Write 1 to 2 paragraphs. Cover how this procedure will be reviewed, improved, and updated based on feedback and performance data.",

    # ─────────────────────────────────────────────
    # Guide Specific
    # ─────────────────────────────────────────────
    "Document Header": "Use as the title block. Include document name, version, date, author, intended audience, and department.",
    "Purpose & Scope": "Write 2 to 3 paragraphs. Combine purpose and scope into a flowing section that clearly sets context for the reader.",
    "Intended Audience": "Write 1 short paragraph or a bullet list. Clearly identify who this guide is written for including UCaaS specific roles.",
    "Prerequisites & Assumptions": "Write a bullet list of 4 to 6 items. State everything the reader must know or have before using this guide.",
    "Core Content": "THIS IS THE MOST CRITICAL SECTION. Write extensively with minimum 5 subsections, each with its own ### heading. Include real world examples, detailed explanations, and step by step guidance. This section MUST represent at least 40% of the total document. Do NOT write thin content here.",
    "Step-by-Step Instructions": "Write comprehensive numbered steps. Every action must be explicitly stated. Include screenshots described in text, tips, and warnings where relevant.",
    "Tools, Resources & References": "Write a structured list with descriptions. Include every tool, platform, or reference the reader needs including UCaaS specific platforms.",
    "Troubleshooting & FAQs": "Write at least 5 to 8 common problems with their solutions. Format as Question → Answer pairs.",
    "Best Practices & Recommendations": "Write 6 to 10 detailed best practice points. Each point MUST be explained with rationale — not just listed as a headline.",
    "Compliance, Security & Legal Notes": "Write 2 to 3 paragraphs. Cover legal, regulatory, and security considerations specific to UCaaS industry.",
    "Change Log / Revision History": "Include a markdown table with columns: Version, Date, Author, Changes Made.",
    "Key Concepts & Background": "Write 3 to 5 paragraphs. Explain all foundational concepts the reader needs to understand before using this guide. Include UCaaS industry context.",
    "Common Mistakes & How to Avoid Them": "Write 5 to 8 common mistakes with detailed explanations of why they happen and how to avoid them.",
    "Use Cases & Examples": "Write 3 to 5 real world use cases relevant to UCaaS. Each use case must have a scenario, challenge, and solution.",
    "Quick Reference Summary": "Write a structured summary table or checklist that the reader can use as a quick reference after reading the full guide.",

    # ─────────────────────────────────────────────
    # Plan Specific
    # ─────────────────────────────────────────────
    "Document Title": "Use as the title block. Include plan name, version, date, author, and sponsoring department.",
    "Purpose / Objective": "Write 1 to 2 paragraphs. State the goal of this plan and what success looks like. Be specific and measurable.",
    "Scope / Context": "Write 1 to 2 paragraphs. Define the boundaries of this plan — what is included and what is explicitly excluded.",
    "Assumptions & Constraints": "Write a bullet list of 4 to 6 items. State every assumption made and every constraint that affects this plan.",
    "Key Stakeholders / Team": "Write a table with columns: Name/Role, Responsibility, Contact. List ALL key people involved.",
    "Approach / Strategy / Steps": "THIS IS THE MOST CRITICAL SECTION. Write minimum 5 phases in comprehensive detail. Each phase must have objectives, activities, deliverables, and success criteria. Use numbered steps or subsections. Do NOT leave this section thin.",
    "Timeline / Schedule (if applicable)": "Include a markdown table with columns: Phase/Milestone, Start Date, End Date, Owner. Be specific and realistic.",
    "Budget & Resources": "Write a structured section covering all required resources — people, tools, budget, and infrastructure.",
    "Risks / Challenges / Dependencies": "Write a table with columns: Risk/Challenge, Likelihood, Impact, Mitigation. Cover at least 5 to 8 items.",
    "Contingency Plan": "Write 2 to 3 paragraphs. State what happens if key risks materialize and how the plan adapts.",
    "Expected Outcomes / Success Metrics": "Write a bullet list of 5 to 8 measurable outcomes. Each MUST be specific, verifiable, and time-bound.",
    "Communication Plan": "Write a structured section covering who gets updated, how often, and through what channels.",
    "Additional Notes / References": "Keep concise. Include any supplementary information, references, or links.",
    "Current State Assessment": "Write 2 to 3 paragraphs. Describe the current situation, pain points, and gaps that this plan addresses.",
    "Resource Plan": "Write a detailed table with columns: Resource Type, Description, Quantity, Cost Estimate, Owner.",
    "Change Management Plan": "Write 2 to 3 paragraphs. Cover how changes will be managed, communicated, and adopted across the organization.",
    "Post Implementation Review": "Write 1 to 2 paragraphs. Cover how the plan's success will be evaluated after implementation.",

    # ─────────────────────────────────────────────
    # Agreement Specific
    # ─────────────────────────────────────────────
    "Title & Parties": "Write the title block clearly. Identify all parties with full legal names, addresses, and roles (e.g. Client, Service Provider).",
    "Recitals & Background": "Write 2 to 3 short paragraphs. Provide context for why this agreement is being entered into.",
    "Scope & Obligations": "Write 2 to 3 paragraphs. Define exactly what each party is obligated to do. Be specific and unambiguous. Use a table to clearly map each obligation to the responsible party and timeline.",
    "Representations & Warranties": "Write a structured list. State all representations and warranties made by each party.",
    "Commercial Terms": "Write precisely. Cover payment amounts, schedules, invoicing terms, and penalties. Use a table if multiple items.",
    "Payment Terms & Invoicing": "Write a structured section. Cover invoice frequency, payment due dates, late payment penalties, and accepted payment methods.",
    "Confidentiality & Data Protection": "Write 2 to 3 tight paragraphs. Cover what is confidential, how it must be handled, duration of obligation, and UCaaS data compliance requirements.",
    "Ownership & Intellectual Property Rights": "Write 1 to 2 paragraphs. Clearly state who owns deliverables, IP, and pre-existing materials.",
    "Limitation of Liability": "Write a precise legal paragraph. State the maximum liability of each party and exclusions.",
    "Indemnification": "Write 1 to 2 paragraphs. State indemnification obligations of each party.",
    "Term & Termination": "Write 1 to 2 paragraphs. State the duration and all conditions under which either party can terminate.",
    "Dispute Resolution": "Write 1 to 2 paragraphs. State the process for resolving disputes — negotiation, mediation, arbitration, jurisdiction.",
    "Legal & General Terms": "Write standard legal boilerplate — governing law, entire agreement clause, severability, amendments, and notices.",
    "Signatures & Execution": "Include a signature block for all parties with Name, Title, Signature, and Date fields.",
    "Service Level Agreement": "Write a detailed SLA section with a table covering: Service, Metric, Target, Measurement Method, Penalty for Breach. Include UCaaS specific SLA metrics like uptime, response time, and resolution time.",
    "Change Management": "Write 1 to 2 paragraphs. Cover how changes to the agreement scope or terms will be requested, reviewed, and approved.",
    "Audit & Compliance Rights": "Write 1 to 2 paragraphs. State the rights of each party to audit compliance with the agreement terms.",
    "Force Majeure": "Write 1 precise paragraph. Define force majeure events and their impact on obligations under this agreement.",

    # ─────────────────────────────────────────────
    # Record Specific
    # ─────────────────────────────────────────────
    "Context & Background": "Write 1 to 2 paragraphs. Provide full background and the situation that led to this record.",
    "Main Content": "THIS IS THE MOST CRITICAL SECTION. Write minimum 4 subsections each covering a distinct aspect of the record. Be factual, objective, and comprehensive. Every fact must be supported with context and evidence.",
    "Data & Evidence": "Write a structured section. Reference all data sources, evidence, or supporting materials.",
    "Responsibilities": "Write a structured list or table. State who is responsible for what in relation to this record.",
    "Constraints & Considerations": "Write a bullet list of 3 to 5 items. State limitations, assumptions, or special considerations.",
    "Findings & Analysis": "Write 2 to 3 paragraphs. Analyze the main content and draw clear, objective findings.",
    "Outcome / Usage": "Write 1 short paragraph. State how this record will be used and what decisions it supports.",
    "Version & Updates": "Include a small table: Version, Date, Author, Summary of Changes.",
    "Impact Assessment": "Write 2 to 3 paragraphs. Assess the impact of the findings or events recorded — on operations, compliance, customers, or business outcomes.",
    "Recommendations": "Write 4 to 6 specific, actionable recommendations based on the findings. Each recommendation must have a clear owner and timeline.",
    "Next Steps & Action Items": "Write a table with columns: Action Item, Owner, Due Date, Status. Cover all follow up actions required.",
}


# UCaaS Industry Context
SAAS_CONTEXT = """
## Industry Context — SaaS (Software as a Service)

This document is being created for the **SaaS industry**. SaaS refers to cloud-based software
delivery where applications are hosted and maintained by the provider and accessed by customers
over the internet on a subscription basis.

When writing this document you MUST apply the following industry context:

- **Regulatory awareness**: SaaS operates under data privacy laws (GDPR, CCPA, HIPAA),
  cloud security frameworks (SOC 2 Type II, ISO 27001, ISO 27017), and industry specific
  compliance standards. Reference these where relevant.
- **Technology context**: SaaS products are built on cloud infrastructure like AWS, Azure,
  and GCP. They integrate with tools like Salesforce, HubSpot, Slack, Jira, and similar
  enterprise platforms. Reference relevant integrations where appropriate.
- **Customer focus**: SaaS businesses serve customers through subscription models with
  strict SLAs, uptime guarantees, onboarding processes, and customer success programs.
  Reflect this in tone and content.
- **Key SaaS roles**: Product Managers, Customer Success Managers, Account Executives,
  Solution Engineers, DevOps Engineers, Support Specialists, Onboarding Specialists,
  and Implementation Consultants. Use these roles where relevant.
- **Industry standards**: Reference SaaS best practices including subscription management,
  customer lifecycle management, churn reduction, product led growth, and cloud service
  delivery frameworks where applicable.
"""


def build_prompt(data: DocumentRequest) -> str:
    qa_sections = ""
    for item in data.answers:
        qa_sections += f"- {item.question}\n  Answer: {item.answer}\n\n"

    scale = DOCUMENT_SCALE_MAP.get(data.document_type, {})
    scale_guidance = f"""
    - Expected Length: {scale.get('pages', 'appropriate length for the document type')}
    - Tone: {scale.get('tone', 'professional and formal')}
    - Writing Style: {scale.get('style', 'structured and clear')}
    """.strip()

    components_list = [c.strip() for c in data.components.strip("'[]").split(",")]
    component_guidance = ""
    for component in components_list:
        instruction = COMPONENT_DEPTH_MAP.get(component)
        if instruction:
            component_guidance += f"- **{component}**: {instruction}\n"
        else:
            component_guidance += f"- **{component}**: Write with professional depth appropriate to the UCaaS industry and document type. Do NOT leave this section thin or vague.\n"

    prompt = f"""
    ## Role
    You are a senior professional document writer and UCaaS industry domain expert with 15+ years
    of experience creating enterprise-grade documentation for Unified Communications companies.
    Your task is to generate a complete, comprehensive, publication-ready document using the
    user's inputs as a foundation — enriched with your UCaaS expertise, industry best practices,
    and professional insights.
    
    ---
    
    {SAAS_CONTEXT}
    
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
    
    This is a **{data.document_type}** document. You MUST write it to the following standard:
    
    {scale_guidance}
    
    Do NOT write a document that is shorter or thinner than this standard.
    Do NOT pad with filler — every word must earn its place.
    
    ---
    
    ## CRITICAL — Per-Section Writing Instructions
    
    You MUST follow these instructions for EVERY section without exception.
    These are non-negotiable minimum quality standards:
    
    {component_guidance}
    
    **STRICT ENFORCEMENT RULES:**
    - Every section MUST meet its depth requirement — no exceptions
    - If a section instruction says "write 2 to 3 paragraphs" you MUST write at least 2 full paragraphs
    - If a section instruction says "write a table" you MUST include a properly formatted markdown table
    - If a section instruction says "THIS IS THE MOST CRITICAL SECTION" treat it as the centerpiece of the document
    - NEVER write a one-liner for any section
    - NEVER use placeholder text like "to be determined" or "insert here"
    - NEVER skip a section — every component must be fully written
    
    ---
    
    ## CRITICAL — Section Separation Rules
    
    This is extremely important for document structure:
    - Every major section MUST start with a `##` heading
    - Every major section MUST end with a horizontal rule `---` on its own line
    - Subsections use `###` headings
    - There must be a `---` divider between EVERY major section without exception
    - The title block at the top must also end with `---`
    - Do NOT group multiple components under one section — each component gets its own `##` heading and `---` divider
    
    ---
    
    ## Your Two-Layer Writing Mandate
    
    ### Layer 1 — User-Driven Content (Personalized)
    - Use the Q&A responses to write accurate, tailored content
    - Infer company details from the answers provided
    - Where details are implied but not stated, make reasonable UCaaS industry inferences
    
    ### Layer 2 — Expert-Augmented Content (UCaaS Knowledge-Driven)
    - Add UCaaS industry context, regulatory norms, and domain-specific frameworks
    - Write standalone sections fully from your UCaaS expert knowledge
    - Expand every section with professional depth — definitions, rationale, implications, examples
    - Add any missing but expected sections with `<!-- Expert Addition -->` tag
    
    ---
    
    ## Mandatory Markdown Formatting
    
    - `#` — Main document title only
    - `##` — Every major section heading
    - `###` — Subsection headings
    - **Bold** for key terms and emphasis
    - `-` or `*` for bullet points
    - Numbered lists for sequential steps
    - Markdown tables for structured data
    - Horizontal rules `---` between EVERY major section
    - Code blocks where technical content appears
    
    ---
    
    ## Document Structure Requirements
    
    Include ALL of the following:
    - **Title Block**: Document name, version, date, author, company — ends with `---`
    - **Executive Summary**: High-level purpose and scope — ends with `---`
    - **Main Sections**: Every component fully written — each ends with `---`
    - **Supporting Elements**: Tables, frameworks, checklists where useful
    - **Conclusion / Recommendations**: Actionable takeaways — ends with `---`
    - **Appendix**: Glossary, references, supplementary content — ends with `---`
    - **Footer**: Confidentiality notice — ends with `---`
    
    ---
    
    ## Autonomy Rules
    
    | Situation | Your Action |
    |---|---|
    | Section needs company data → provided | Write using the provided data |
    | Section needs company data → not provided | Infer from UCaaS industry context |
    | Section is a standalone concept | Write fully from UCaaS expert knowledge |
    | Standard section missing from user's list | Add it with `<!-- Expert Addition -->` tag |
    | Content is thin or vague in inputs | Expand with UCaaS industry depth |
    
    ---
    
    ## Output Rules
    
    - Output ONLY the final Markdown document
    - Do NOT explain your reasoning or process
    - Do NOT restate user inputs verbatim
    - Do NOT mention that you are an AI or reference this prompt
    - DO write as a credentialed UCaaS industry expert authoring a real enterprise deliverable
    - EVERY section must have its own `##` heading and end with `---`
    
    ---
    
    ## Final Directive
    
    Generate an authoritative, end-to-end professional document in Markdown for the UCaaS industry.
    Use the user's inputs as your foundation. Apply your UCaaS domain expertise throughout.
    Every section MUST meet the depth standard defined above.
    Every section MUST end with a `---` divider.
    This document must be ready for real-world professional use — detailed, purposeful, and industry accurate.
    """
    return prompt.strip()


def build_refine_section_prompt(data: RefineSectionRequest) -> str:
    prompt = f"""
    You are a senior UCaaS industry document editor with expertise in professional business documentation.
    
    Your job is to improve the section below based on the user's instruction while maintaining
    the highest professional standards for UCaaS industry documentation.
    
    **Current Section:**
    {data.section_text}
    
    **User Instruction:**
    {data.instruction}
    
    **Rules:**
    - Apply ONLY what the instruction asks — do not change anything else
    - Maintain the same professional UCaaS industry tone and style
    - Keep the same markdown formatting — headings, bullets, tables must be preserved
    - Keep the `##` heading at the top of the section
    - End the section with `---` divider
    - Do not add new sections — only improve the existing content
    - Return ONLY the improved section, nothing else
    - The rewritten section must be at least as detailed as the original — do not make it shorter
    """
    return prompt.strip()