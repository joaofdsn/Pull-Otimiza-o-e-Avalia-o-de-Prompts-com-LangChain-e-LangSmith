"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt antes de cada teste."""
        data = load_prompts(str(PROMPT_FILE))
        self.prompt = data[PROMPT_KEY]
        self.system_prompt = self.prompt.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' não encontrado no YAML"
        assert self.system_prompt.strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        role_keywords = [
            "Você é um", "você é um",
            "Você é uma", "você é uma",
            "Product Manager", "Especialista",
            "Você é", "você é",
        ]
        found = any(keyword in self.system_prompt for keyword in role_keywords)
        assert found, (
            "O system_prompt deve definir uma persona/role. "
            "Ex: 'Você é um Product Manager sênior...'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        format_keywords = [
            "Markdown", "markdown",
            "User Story", "user story",
            "Como [", "Como um",
            "Dado que", "Critérios de Aceitação",
            "Given", "When", "Then",
        ]
        found = any(keyword in self.system_prompt for keyword in format_keywords)
        assert found, (
            "O system_prompt deve especificar o formato de saída esperado. "
            "Ex: formato Markdown, User Story, Dado que/Quando/Então..."
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        example_keywords = [
            "Exemplo", "exemplo",
            "Example", "example",
            "Input:", "Output:",
            "Entrada", "entrada",
            "Saída esperada", "saída esperada",
        ]
        found = any(keyword in self.system_prompt for keyword in example_keywords)
        assert found, (
            "O system_prompt deve conter exemplos de entrada/saída (Few-shot Learning). "
            "Ex: '### Exemplo 1:', 'Entrada:', 'Saída esperada:'"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[TODO]" not in self.system_prompt, (
            "O system_prompt contém '[TODO]' não preenchido."
        )
        user_prompt = self.prompt.get("user_prompt", "")
        assert "[TODO]" not in user_prompt, (
            "O user_prompt contém '[TODO]' não preenchido."
        )

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"São necessárias pelo menos 2 técnicas em 'techniques_applied', "
            f"encontradas: {len(techniques)} — {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
