---
name: wechat-publish-workflow
description: >
  An integrated toolkit and skill system for automating WeChat Official Account publishing workflows. 
  It combines an AI-driven authoring loop with a robust toolkit for publishing, updating, and managing articles.
  The core OpenClaw skill is located in the `skills/wechat-publish-workflow-skill/` subdirectory.
---

# WeChat Publish Workflow (Integrated System)

This repository provides a comprehensive solution for managing and automating content for WeChat Official Accounts. It is designed around a "skill + toolkit" architecture, where the AI skill orchestrates the workflow, and the underlying toolkit handles the technical execution of publishing tasks.

## Key Components

- **AI Workflow Entrypoint:** The primary OpenClaw skill for this system is found at `skills/wechat-publish-workflow-skill/SKILL.md`. This skill manages the intelligent aspects of content creation, ideation, and decision-making for publishing.
- **Execution Toolkit:** The `toolkit/` directory contains the Python scripts and configurations responsible for low-level tasks such as API integration, article publishing/updating, draft synchronization, and cover generation.
- **Documentation:** Detailed setup and operational guidelines are available in the `docs/` directory.

## Capabilities

- Incubate WeChat article ideas and material from conversations.
- Convert dialogues and experiences into structured WeChat articles.
- Publish and update WeChat Official Account drafts.
- Optimize article content and cover styling.
- Synchronize remote article modifications back to local drafts.

To start using the core AI-driven publishing capabilities, refer to the `skills/wechat-publish-workflow-skill/SKILL.md` file located within this repository.