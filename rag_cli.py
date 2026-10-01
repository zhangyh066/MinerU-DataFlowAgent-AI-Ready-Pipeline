"""RAG 检索与问答命令行入口。

用法：
    python rag_cli.py build [--force]
    python rag_cli.py query --query "问题"
    python rag_cli.py ask --question "问题" [--with-llm]
    python rag_cli.py eval --auto --questions eval_questions.json
"""

import sys

from rag.cli import main

if __name__ == "__main__":
    sys.exit(main())
