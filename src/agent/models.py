from pydantic import BaseModel, Field


class IssuePayload(BaseModel):
    """O formato de dados que a API espera receber no corpo da requisição."""

    title: str = Field(..., description="O título da issue a ser classificada.")
    description: str = Field(description="A descrição da issue.", default="")


class ClassificationResponse(BaseModel):
    """O formato de dados que a API retornará."""

    suggested_label: str
    reasoning: str
