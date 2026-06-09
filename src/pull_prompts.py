"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do LangSmith Hub e salva localmente."""
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    print_section_header("Pull de Prompts do LangSmith Hub")

    prompt_id = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull de: {prompt_id}")

    try:
        client = Client()
        prompt_template = client.pull_prompt(prompt_id, dangerously_pull_public_prompt=True)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt '{prompt_id}': {e}")
        return False

    system_prompt = ""
    user_prompt = ""

    for msg in prompt_template.messages:
        role = msg.__class__.__name__.lower()
        content = msg.prompt.template if hasattr(msg, "prompt") else str(msg)
        if "system" in role:
            system_prompt = content
        elif "human" in role:
            user_prompt = content

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
    if save_yaml(prompt_data, str(output_path)):
        print(f"✅ Prompt salvo em: {output_path}")
        return True
    else:
        print("❌ Falha ao salvar o prompt localmente.")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    if not success:
        print("\n❌ Pull falhou. Verifique as credenciais no .env")
        return 1
    print("\n✅ Pull concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
