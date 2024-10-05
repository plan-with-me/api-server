import json
from openai import OpenAI

from core.config.secrets import OPENAI_KEY


class OpenAIClient():
    openai = OpenAI(api_key=OPENAI_KEY)

    
    def get_related_tags(self, base_tags: list[str]) -> list[str]:
        prompt = (
            "For each tag below, provide 7 related tags."
            "Each tags should be semantically or contextually related."
            "Each tag must match the language of the given word.\n\n"
            f"Tags: {', '.join(base_tags)}\n\n"
            "Respond in this string format:\n"
            '{"tag1": ["related1", "related2", ...], "tag2": [...]}'
        )
        completion = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
        )
        related_tags = json.loads(completion.choices[0].message.content)
        result = []
        for tags in related_tags.values():
            result.extend(tags)
        return sorted(result)
