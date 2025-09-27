# src/schema_utils.py
from pydantic import BaseModel, Field, conint
from typing import Literal
from configs import ERROR_CATEGORIES

# Create a Literal type that only allows values from our list of categories
ErrorType = Literal[tuple(ERROR_CATEGORIES)]

class ErrorAnalysis(BaseModel):
    """
    A structured model for the analysis of a student's error.
    """
    error_type: ErrorType = Field(
        ..., 
        description="The single, most appropriate error category from the predefined list."
    )
    detailed_explanation: str = Field(
        ..., 
        description="A concise, clear explanation of what the student did wrong."
    )

    class Config:
        # This allows creating an instance from a dictionary
        from_attributes = True


class ConversationEvaluation(BaseModel):
    """
    A structured model for the evaluation of a tutoring conversation.
    Each rubric is scored on a scale of 1 to 5.
    """
    goal_achievement_score: conint(ge=1, le=5) = Field(..., description="Score for Goal Achievement & Correctness.")
    socratic_guidance_score: conint(ge=1, le=5) = Field(..., description="Score for Socratic Guidance.")
    empathy_and_tone_score: conint(ge=1, le=5) = Field(..., description="Score for Empathy & Tone.")
    conciseness_and_clarity_score: conint(ge=1, le=5) = Field(..., description="Score for Conciseness & Clarity.")
    student_engagement_score: conint(ge=1, le=5) = Field(..., description="Score for Student Engagement.")
    conversational_efficiency_score: conint(ge=1, le=5) = Field(..., description="Score for Conversational Efficiency.")
    
    justification: str = Field(..., description="A brief, overall justification for the scores provided.")

    class Config:
        from_attributes = True
