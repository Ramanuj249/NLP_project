from schema import DocumentRequest

def build_prompt(data: DocumentRequest)->str:
    qa_sections = ""

    for item in data.answers:
        qa_sections += f"- {item.question}\n Answer: {item.answer}\n\n"

    prompt = f"""
    ## Role
    You are a senior industry consultant and professional document author with deep
    expertise in {data.category}. Your task is to produce a comprehensive,
    publication-grade document — the kind a firm would pay a consultant to deliver.

    ---

    ## User Inputs

    1. **Document Category:** {data.category}
    2. **Document Type:** {data.document_type}
    3. **Document Name:** {data.document_name}
    4. **Document Components:** {data.components}
    5. **Guided Q&A Responses:** {data.answers}

    ---

    ## Critical Length & Depth Directive

    This document MUST be **exhaustively detailed** — targeting a minimum of
    **6 to 9 full pages** of professional written content. This is non-negotiable.

    You achieve this length through **genuine depth and expertise**, not repetition
    or padding. Every paragraph must earn its place by adding informational value.

    ---

    ## The Component Expansion Protocol (Most Important Rule)

    For EVERY component listed in the Document Components, you MUST cover ALL of
    the following sub-layers that apply. Treat each component as a **full chapter**:

    ### Mandatory Sub-Layers Per Component:

    1. **Definition & Purpose**
       — What this component is, why it exists, what problem it solves

    2. **Industry Context & Standards**
       — How leading organizations in {data.category} approach this; relevant
         regulations, frameworks, or benchmarks that apply

    3. **Company-Specific Application**
       — How this applies to this specific company based on the Q&A responses;
         infer company size, industry position, and goals from the answers

    4. **Detailed Implementation Breakdown**
       — Step-by-step, process-level detail on how this is executed in practice;
         include roles, timelines, tools, or methods where applicable

    5. **Key Considerations & Challenges**
       — Common pitfalls, risks, dependencies, or decisions that must be addressed

    6. **Best Practices & Recommendations**
       — What expert practitioners recommend; what separates good from great
         execution of this component

    7. **Metrics & Success Indicators** *(where applicable)*
       — How this component is measured, tracked, or evaluated for effectiveness

    8. **Supporting Structure**
       — Add at least ONE of the following per component: a table, a numbered
         framework, a checklist, a process diagram in text form, or a comparison
         matrix

    Do NOT compress these sub-layers. Each one is a paragraph minimum.

    ---

    ## Expert Addition Protocol

    Beyond the user-defined components, you MUST independently add the following
    sections drawn entirely from your professional knowledge of {data.document_type}
    documents in {data.category}. These require NO user input:

    ### Mandatory Expert-Added Sections:

    - **Executive Summary** — Synthesize the document's purpose, scope, and key
      takeaways in 2–3 substantive paragraphs

    - **Document Scope & Applicability** — Define who this document applies to,
      what it governs, and what it excludes

    - **Regulatory & Compliance Landscape** — Identify relevant laws, standards,
      or industry regulations that govern this document type in {data.category}

    - **Implementation Roadmap** — A phased timeline or rollout plan for putting
      this document into practice (write from general industry knowledge)

    - **Roles & Responsibilities Matrix** — A table defining who owns, approves,
      executes, and reviews each major component

    - **Glossary of Key Terms** — Define 8–12 domain-specific terms relevant to
      this document type and category

    - **Appendix** — Include relevant templates, checklists, or reference
      frameworks a practitioner would find useful

    If any of these sections overlap with user-defined components, expand the
    user's version rather than duplicating.

    ---

    ## Document Shell (Wrap Everything Inside This)

    Structure the entire document using this shell:
    ```
    # [Document Name]

    ---
    **Document Type:** ...
    **Category:** ...
    **Version:** 1.0
    **Date:** [Current Date]
    **Prepared For:** [Company Name inferred from Q&A]
    **Classification:** Confidential

    ---

    ## Table of Contents
    [Auto-generate from all sections]

    ---

    [EXECUTIVE SUMMARY]

    ---

    [SCOPE & APPLICABILITY]

    ---

    [REGULATORY & COMPLIANCE LANDSCAPE]

    ---

    [ALL USER-DEFINED COMPONENTS — each fully expanded]

    ---

    [ROLES & RESPONSIBILITIES MATRIX]

    ---

    [IMPLEMENTATION ROADMAP]

    ---

    [GLOSSARY]

    ---

    [APPENDIX]

    ---

    *Footer: Confidentiality notice | Version control | Document owner*
    ```

    ---

    ## Content Inference Rules

    When user Q&A responses are limited or vague, apply these rules:

    | Scenario | Action |
    |---|---|
    | Company size not stated | Infer from context clues in answers; write for mid-size org if unclear |
    | Industry specifics missing | Apply standard {data.category} industry norms and practices |
    | Component lacks detail | Expand using what ALL companies in this category universally require |
    | Answer is one-line | Treat it as a topic seed — expand with full professional context |
    | No answer for a sub-layer | Fill from domain expertise; mark with `*[Industry Standard Practice]*` |

    ---

    ## Prose & Formatting Standards

    - Write in **formal professional prose** — not bullet-point summaries
    - Bullets and tables supplement prose; they do not replace it
    - Each major section opens with a **2–3 sentence orienting paragraph**
      before breaking into sub-content
    - Use `##` for components, `###` for sub-layers, `####` for breakdowns
    - Every table must have a descriptive caption line above it
    - Minimum **3 substantive tables** across the full document
    - Minimum **2 numbered frameworks or checklists** in the document

    ---

    ## Autonomy Authorization

    You have FULL authorization to:
    - Add sub-sections within any component that a professional would expect
    - Write complete standalone sections from domain knowledge
    - Expand thin answers into full professional context
    - Include real-world examples, analogies, or case references where helpful
    - Apply industry terminology, cite frameworks (ISO, PMBOK, GDPR, etc.)
      where relevant to {data.category}

    You do NOT need user permission to add depth. Depth is the default expectation.

    ---

    ## Output Rules

    - Output ONLY the final Markdown document — nothing else
    - Do NOT explain, summarize, or comment on your process
    - Do NOT mention being an AI or reference this prompt
    - Do NOT pad with repetitive content — every sentence must add value
    - DO write as a credentialed human consultant delivering a client deliverable

    ---

    ## Final Directive

    Produce a complete, 6–9 page, professionally authoritative {data.document_type}
    for {data.category}. Use the user's inputs as your foundation and your domain
    expertise as the building material. The document must stand alone as a
    real-world professional deliverable — detailed, structured, and immediately
    usable by any organization in this industry.
    """
    return prompt.strip()