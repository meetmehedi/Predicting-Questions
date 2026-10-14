"""Data models and validation schema for Bangladesh HSC/SSC Exam Question Research Corpus (BD-ExamQ).

Covers Creative Questions (CQ - সৃজনশীল), Multiple Choice Questions (MCQ - বহুনির্বাচনী),
Traditional descriptive questions, NCTB syllabus mapping, and pedagogical annotations.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class ExamLevel(str, Enum):
    SSC = "SSC"
    HSC = "HSC"
    DAKHIL = "Dakhil"
    ALIM = "Alim"


class BoardName(str, Enum):
    DHAKA = "Dhaka"
    CHATTOGRAM = "Chattogram"
    RAJSHAHI = "Rajshahi"
    CUMILLA = "Cumilla"
    JASHORE = "Jashore"
    BARISHAL = "Barishal"
    SYLHET = "Sylhet"
    DINAJPUR = "Dinajpur"
    MYMENSINGH = "Mymensingh"
    MADRASAH = "Madrasah"
    TECHNICAL = "Technical"
    COMBINED = "Combined"  # Used in years with combined board exams like 2018


class QuestionType(str, Enum):
    CQ = "CQ"          # Creative Question (সৃজনশীল)
    MCQ = "MCQ"        # Multiple Choice Question (বহুনির্বাচনী)
    SHORT = "Short"    # Short answer / One word / Fill in blanks
    TRADITIONAL = "Traditional"  # Pre-CQ syllabus descriptive question


class CognitiveDomain(str, Enum):
    KNOWLEDGE = "knowledge"             # জ্ঞানমূলক (ক)
    COMPREHENSION = "comprehension"     # অনুধাবনমূলক (খ)
    APPLICATION = "application"         # প্রয়োগমূলক (গ)
    HIGHER_ORDER = "higher_order"       # উচ্চতর দক্ষতামূলক (ঘ)
    MIXED = "mixed"                     # Compound question (e.g. CQ stem overall)


class MCQVariant(str, Enum):
    SINGLE = "single"                           # সাধারণ বহুনির্বাচনী
    MULTIPLE_COMPLETION = "multiple_completion" # বহুপদী সমাপ্তিসূচক (i, ii, iii)
    STEM_CONTEXT = "stem_context"               # অভিন্ন তথ্যভিত্তিক বহুনির্বাচনী


class CurriculumPhase(str, Enum):
    PRE_CQ = "pre_cq"                           # Before CQ adoption
    EARLY_CQ = "early_cq"                       # Initial CQ rollout (2010-2015)
    FULL_SYLLABUS = "full_syllabus"             # Standard full syllabus (2016-2019)
    COVID_AUTOPASS = "covid_autopass"           # 2020 auto-evaluation
    COVID_SHORT_2021 = "covid_short_2021"       # 2021 condensed syllabus
    COVID_SHORT_2022_2023 = "covid_short_2022_2023" # 2022-2023 revised short syllabus
    TRANSITION_2024_PLUS = "transition_2024_plus"   # Post-2024 curriculum transitions


class VerificationStatus(str, Enum):
    RAW_OCR = "raw_ocr"
    SEMI_VERIFIED = "semi_verified"
    GOLD_VERIFIED = "gold_verified"


class SubQuestion(BaseModel):
    """Represents an individual sub-part of a Creative Question (CQ): ক, খ, গ, or ঘ."""
    part: str = Field(..., description="Sub-part label: 'ক', 'খ', 'গ', 'ঘ' or 'a', 'b', 'c', 'd'")
    cognitive_domain: CognitiveDomain = Field(..., description="Bloom's taxonomy cognitive domain")
    marks: int = Field(..., ge=1, le=4, description="Standard marks: ক=1, খ=2, গ=3, ঘ=4")
    text_bn: str = Field(..., description="Bangla text of the sub-question")
    text_en: Optional[str] = Field(None, description="English translation or English version text")
    chapter_id: Optional[str] = Field(None, description="Specific chapter ID if different from main question")
    topic_id: Optional[str] = Field(None, description="Specific topic ID mapped to NCTB curriculum")
    sample_answer_bn: Optional[str] = Field(None, description="Official mark scheme or model answer")


class MCQOption(BaseModel):
    """Represents an option in an MCQ question."""
    label: str = Field(..., description="'ক', 'খ', 'গ', 'ঘ' or 'A', 'B', 'C', 'D'")
    text_bn: str = Field(..., description="Bangla option text")
    text_en: Optional[str] = Field(None, description="English option text")
    is_correct: Optional[bool] = Field(None, description="Ground truth answer indicator")


class QuestionRecord(BaseModel):
    """Canonical record representing a single examination question (CQ, MCQ, or Traditional)."""
    id: str = Field(..., description="Globally unique question identifier (e.g. HSC-2023-DHA-PHY1-CQ-01)")
    exam: ExamLevel = Field(..., description="Examination level: SSC, HSC, Dakhil, Alim")
    year: int = Field(..., ge=2000, le=2030, description="Examination year")
    board: BoardName = Field(..., description="Education board name")
    subject: str = Field(..., description="Subject name in English (e.g. Physics, Bangla, ICT)")
    subject_code: Optional[str] = Field(None, description="Official NCTB subject code (e.g. '174')")
    paper: Optional[str] = Field(None, description="'1st', '2nd', or null for single paper subjects")
    set_name: Optional[str] = Field(None, alias="set", description="Question set (e.g. 'Ka', 'Kha', '1', '2')")
    q_type: QuestionType = Field(..., description="Question format: CQ, MCQ, Short, Traditional")
    question_no: Optional[int] = Field(None, description="Sequential question number in the paper (1 to 30)")
    marks: float = Field(..., gt=0, description="Total allocated marks (10 for standard CQ, 1 for MCQ)")
    
    # Text contents
    text_bn: Optional[str] = Field(None, description="Unified text representation in Bangla")
    text_en: Optional[str] = Field(None, description="Unified text representation in English")
    stem: Optional[str] = Field(None, description="Stimulus / উদ্দীপক text, context story, code snippet, or table")
    has_image: bool = Field(False, description="True if question contains a diagram, circuit, figure, or graph")
    image_paths: List[str] = Field(default_factory=list, description="Relative paths to attached figures")
    
    # Structured components
    sub_parts: Optional[List[SubQuestion]] = Field(
        None, description="Structured 4 sub-parts (ক, খ, গ, ঘ) for Creative Questions"
    )
    options: Optional[List[MCQOption]] = Field(
        None, description="Options for Multiple Choice Questions"
    )
    mcq_variant: Optional[MCQVariant] = Field(
        None, description="Specific MCQ variant (single, multiple-completion, context-based)"
    )
    answer_key: Optional[str] = Field(None, description="Correct MCQ option label (e.g. 'গ')")
    
    # Pedagogical & Curriculum Annotations
    chapter_id: str = Field(..., description="NCTB Chapter ID (e.g. 'PHY1-CH02')")
    chapter_name_bn: Optional[str] = Field(None, description="Chapter name in Bengali")
    chapter_name_en: Optional[str] = Field(None, description="Chapter name in English")
    topic_id: Optional[str] = Field(None, description="Primary topic ID (e.g. 'PHY1-CH02-TOP04')")
    topic_tags: List[str] = Field(default_factory=list, description="Descriptive concept keywords")
    bloom_level: CognitiveDomain = Field(..., description="Primary cognitive level or 'mixed' for CQ")
    curriculum_phase: CurriculumPhase = Field(
        CurriculumPhase.FULL_SYLLABUS, description="Curriculum regime for covariate analysis"
    )
    
    # Provenance & Data Quality Metadata
    source_url: Optional[str] = Field(None, description="URL of board archive, portal, or source document")
    ocr_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Estimated OCR confidence score (1.0 for verified text)"
    )
    verification_status: VerificationStatus = Field(
        VerificationStatus.SEMI_VERIFIED, description="Data verification tier"
    )
    annotator_id: Optional[str] = Field(None, description="Identifier of annotator or pipeline version")

    @field_validator("sub_parts")
    @classmethod
    def validate_cq_subparts(cls, v: Optional[List[SubQuestion]], info) -> Optional[List[SubQuestion]]:
        # If type is CQ and sub_parts is provided, verify it has parts
        if v is not None and len(v) > 0:
            parts = [sp.part for sp in v]
            # Standard Bangla CQ subparts are ক, খ, গ, ঘ
            bangla_labels = {"ক", "খ", "গ", "ঘ"}
            english_labels = {"a", "b", "c", "d"}
            part_set = set(parts)
            if not (bangla_labels.issubset(part_set) or english_labels.issubset(part_set)):
                # Warning or tolerance for non-standard, but ensure count is 4
                if len(v) not in (3, 4):
                    raise ValueError(f"Creative Questions normally contain 4 sub-parts (ক, খ, গ, ঘ), got {parts}")
        return v

    @model_validator(mode="after")
    def validate_question_integrity(self) -> QuestionRecord:
        # Check marks consistency
        if self.q_type == QuestionType.CQ:
            if self.sub_parts:
                sub_sum = sum(sp.marks for sp in self.sub_parts)
                if abs(sub_sum - self.marks) > 0.1:
                    raise ValueError(
                        f"CQ marks sum mismatch: sum of sub_parts={sub_sum} != total marks={self.marks}"
                    )
            if not self.stem and not self.text_bn:
                raise ValueError("CQ must contain either a stimulus ('stem') or full question text ('text_bn')")
        
        if self.q_type == QuestionType.MCQ:
            if self.options and len(self.options) < 2:
                raise ValueError("MCQ must have at least 2 options")
        return self


class ExamPaper(BaseModel):
    """Represents a complete examination paper containing multiple questions."""
    paper_id: str = Field(..., description="Unique exam paper ID (e.g. HSC-2023-DHA-PHY1)")
    exam: ExamLevel
    year: int
    board: BoardName
    subject: str
    paper: Optional[str] = None
    subject_code: Optional[str] = None
    time_minutes: int = Field(150, description="Total exam duration in minutes")
    total_marks: float = Field(..., description="Total paper marks (e.g. 50, 75, 100)")
    curriculum_phase: CurriculumPhase
    cq_total_questions: Optional[int] = Field(None, description="Number of CQs given (e.g. 8)")
    cq_answer_count: Optional[int] = Field(None, description="Number of CQs required to answer (e.g. 5)")
    mcq_total_questions: Optional[int] = Field(None, description="Number of MCQs (e.g. 25)")
    questions: List[QuestionRecord] = Field(default_factory=list)
