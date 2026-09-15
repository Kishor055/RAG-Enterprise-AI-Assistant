# RAG Enterprise AI Assistant — Project Blueprint

## Executive Summary
The **RAG Enterprise AI Assistant** is a production-grade, secure, and modular Retrieval-Augmented Generation platform designed for enterprise document intelligence. It enables authorized users across an organization to securely upload confidential documents (PDFs, Word documents, spreadsheets, text files), organize them into domain-specific Knowledge Bases, and interact with them using natural language queries.

Unlike generic conversational AI models that suffer from hallucinations and lack domain context, this assistant grounds every answer directly in the organization's private data repositories, providing exact source citations (file name, page number, section, snippet hash) for full traceability and auditability.

---

## 1. Problem Statement
Modern enterprises generate massive volumes of unstructured and semi-structured documents daily—including legal contracts, technical manuals, internal policy documents, financial audits, and standard operating procedures (SOPs). 

Key challenges faced by organizations include:
1. **Information Silos & Retrieval Inefficiency**: Employees spend up to 20% of their working hours manually searching through enterprise repositories and long-form documents for specific answers.
2. **LLM Hallucinations**: Off-the-shelf Large Language Models (LLMs) cannot access private enterprise documents and often generate confident but incorrect (hallucinated) responses when queried on domain-specific facts.
3. **Data Security & Privacy Risks**: Uploading proprietary enterprise documents to public LLM platforms poses severe data leakage, compliance, and regulatory risks.
4. **Lack of Access Control in Information Retrieval**: Existing search tools often ignore document permissions, exposing sensitive executive or financial data to unauthorized personnel.
5. **Traceability Deficit**: Decision-makers require verifiable sources and page-level references rather than black-box AI answers.

---

## 2. Project Objectives
The objective of this project is to architect, build, test, and document a robust, enterprise-ready RAG system that directly addresses these challenges while serving as a comprehensive final-year software engineering project.

### Core Objectives:
- **Grounded Information Retrieval**: Implement semantic and hybrid search over chunked enterprise documents to feed accurate context to an LLM.
- **Strict Data Isolation & Security**: Enforce Role-Based Access Control (RBAC) and Document-Level Security (DLS) so users only retrieve information from documents they have explicit permission to read.
- **Verifiable Citations**: Ensure every generated response includes precise inline and footnotes citations linking back to original source files and page numbers.
- **Provider-Agnostic Architecture**: Design clean abstract interfaces for LLM providers, Embedding providers, Document Processors, and Vector Databases, enabling seamless swapping without breaking core application code.
- **Resource-Efficient Engineering**: Optimize the local development pipeline for non-GPU developer machines (e.g., Intel UHD integrated graphics) via API-driven LLMs and lightweight local vector storage adapters.

---

## 3. Target Users & User Personas

| Persona | Role | Key Needs & Objectives |
| :--- | :--- | :--- |
| **Enterprise Admin** | System Administrator | Manages user accounts, assigns RBAC roles, provisions Knowledge Bases, monitors audit logs, configures system guardrails. |
| **Knowledge Manager / Content Owner** | Department Lead / Analyst | Uploads proprietary documents, manages document metadata, tags documents, organizes Knowledge Bases, verifies chunking quality. |
| **Enterprise Employee** | Standard User | Asks natural language questions, views grounded AI responses, inspects page-level citations, exports chat summaries. |
| **Auditor / Compliance Officer** | Security Representative | Reviews query history, inspects audit logs for data access patterns, verifies prompt injection defenses and document security boundaries. |

---

## 4. Functional Requirements

### 4.1 Authentication & User Management
- **FR-1.1**: Secure user signup, login, password hashing (Argon2 / Bcrypt), and JWT-based session management.
- **FR-1.2**: Role-Based Access Control (RBAC) with defined roles: `Admin`, `Knowledge Manager`, `Standard User`.
- **FR-1.3**: User profile management and active token revocation (logout).

### 4.2 Knowledge Base & Document Management
- **FR-2.1**: Support document uploads in multiple formats (`.pdf`, `.docx`, `.txt`, `.csv`, `.md`).
- **FR-2.2**: Support multi-tenant document isolation and explicit permission mapping (Private, Departmental, Global).
- **FR-2.3**: Automated document pipeline: Text extraction, sanitization, recursive chunking, metadata tag generation, embedding generation.
- **FR-2.4**: Document status tracking (`Pending`, `Processing`, `Indexed`, `Failed`) with error log details.
- **FR-2.5**: Ability to re-index, archive, or hard-delete documents along with their associated vector embeddings.

### 4.3 RAG Query & Conversational Assistant
- **FR-3.1**: Natural language chat interface with session history and context-aware follow-up questions.
- **FR-3.2**: Knowledge Base filtering: Users can select single or multiple Knowledge Bases to constrain query scope.
- **FR-3.3**: Semantic search & vector retrieval filtered strictly by user authorization.
- **FR-3.4**: Context construction with strict system prompts preventing out-of-domain hallucinations.
- **FR-3.5**: Grounded response generation with inline citation badges `[Source: File, Page X]`.
- **FR-3.6**: Source drawer displaying retrieved passage snippets, similarity scores, and document metadata.

### 4.4 Governance, Audit & Monitoring
- **FR-4.1**: Comprehensive audit log recording query text, retrieved document IDs, user ID, timestamp, response latency, and token usage.
- **FR-4.2**: Prompt injection detection and input query sanitization.
- **FR-4.3**: System health check endpoint inspecting database connectivity, vector store status, and LLM API availability.

---

## 5. Non-Functional Requirements

### 5.1 Performance & Latency
- **NFR-1.1 Query Response Time**: End-to-end question-answering response time within 2.5–4.5 seconds over external API LLMs.
- **NFR-1.2 Retrieval Speed**: Sub-300ms vector similarity retrieval across up to 100,000 document chunks.
- **NFR-1.3 Asynchronous Ingestion**: Heavy document processing and embedding generation offloaded to asynchronous background tasks to keep UI responsive.

### 5.2 Scalability & Modular Flexibility
- **NFR-2.1 Provider Independence**: Strict interface adapters (`BaseLLM`, `BaseEmbedding`, `BaseVectorStore`) allowing switching between OpenAI, Gemini, Claude, ChromaDB, Qdrant, and pgvector via `.env` configuration.
- **NFR-2.2 Database Decoupling**: Database layer designed using SQLAlchemy ORM to run on SQLite locally and PostgreSQL in production without schema modifications.

### 5.3 Security & Compliance
- **NFR-3.1 Data Isolation**: Zero cross-tenant data leaks. A user without read access to Document X must never retrieve chunks from Document X.
- **NFR-3.2 Secret Protection**: Zero hardcoded API keys; all sensitive credentials loaded exclusively from environment variables or secure key vaults.
- **NFR-3.3 Input Hygiene**: Defense against prompt injection and malicious file uploads (MIME type verification, size caps).

### 5.4 Maintainability & Viva Readiness
- **NFR-4.1 Code Quality**: Type hints, docstrings, unit tests, and separation of concerns (Controller-Service-Repository pattern).
- **NFR-4.2 Academic Artifacts**: Complete set of diagrams (ER, DFD, Sequence, Component) suitable for final-year thesis defense and viva presentation.

---

## 6. Scope Boundaries & MVP Definition

### 6.1 In-Scope for MVP
1. Modular FastAPI backend with clean interface adapters for LLM, Embeddings, and Vector Store.
2. Modern React + Vite frontend with dynamic chat interface, document drawer, source citation inspector, and admin console.
3. Asynchronous document ingestion pipeline supporting PDF, DOCX, TXT, and Markdown files.
4. Recursive character chunking with metadata tagging (document_id, page_number, chunk_index, owner_id, access_level).
5. User authentication & authorization (JWT + RBAC + Document-Level Security filters).
6. Grounded RAG query execution with citation extraction and source highlight drawer.
7. Local dev setup optimized for non-GPU hardware (API LLM + local SQLite/Chroma file storage).

### 6.2 Out-of-Scope for Initial MVP (Future Scope)
1. Heavy local LLM execution requiring dedicated CUDA GPUs.
2. Multi-modal RAG (video/audio processing).
3. Complex OCR for scanned handwritten images (standard digital PDF text extraction is in-scope).
4. Real-time multi-user collaborative canvas.

---

## 7. Future Enhancements Roadmap
- **Phase A**: Hybrid Search (BM25 Keyword Search + Dense Vector Search combined with Reciprocal Rank Fusion - RRF).
- **Phase B**: Cross-Encoder Reranking using lightweight CPU-friendly models (`bge-reranker-small`).
- **Phase C**: GraphRAG integration for entity-relationship knowledge graph querying over enterprise documents.
- **Phase D**: Enterprise SSO integration (OAuth2 / SAML / Azure AD).
