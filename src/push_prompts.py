"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    full_name = f"{username}/{prompt_name}"
    print(f"Fazendo push para: {full_name}")

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    try:
        client = Client()
        client.push_prompt(full_name, object=prompt_template, is_public=True)
        print(f"✅ Prompt publicado com sucesso: {full_name}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["system_prompt", "user_prompt", "version", "techniques_applied"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: '{field}'")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs não preenchidos")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    print_section_header("Push de Prompts Otimizados ao LangSmith Hub")

    prompt_file = pathlib.Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"

    if not prompt_file.exists():
        print(f"❌ Arquivo não encontrado: {prompt_file}")
        print("   Crie o arquivo prompts/bug_to_user_story_v2.yml primeiro.")
        return 1

    data = load_yaml(str(prompt_file))
    if not data:
        return 1

    prompt_data = data.get("bug_to_user_story_v2")
    if not prompt_data:
        print("❌ Chave 'bug_to_user_story_v2' não encontrada no YAML.")
        return 1

    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return 1
    print("✅ Prompt válido!")

    success = push_prompt_to_langsmith("bug_to_user_story_v2", prompt_data)
    if not success:
        return 1

    techniques = prompt_data.get("techniques_applied", [])
    print(f"\nTécnicas aplicadas: {', '.join(techniques)}")
    print(f"Tags: {', '.join(prompt_data.get('tags', []))}")
    print("\n✅ Push concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
