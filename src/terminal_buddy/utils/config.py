from pydantic import BaseModel, Field


class Config(BaseModel):
    OLLAMA_MODEL_NAME: str = Field(default="qwen3:0.6b")
    OLLAMA_EMBEDDINGS_MODEL_NAME: str = Field(default="nomic-embed-text")
    EXAMPLES_JSON_PATH: str = Field(default="/Users/atharva/projects/TBuddy/terminal-buddy/data/examples/text_2_command_examples.json")
