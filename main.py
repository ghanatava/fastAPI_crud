from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List , Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session 


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_txt: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_txt: str
    choices: List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]


@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: db_dependency):
    result=db.query(models.Questions).filter(models.Questions.id==question_id).first()
    if not result:
        raise HTTPException(status_code=404,detail="Question does not exist!")
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id==question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="not found")
    return result

@app.post("/questions/")
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_txt=question.question_txt)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(choice_txt=choice.choice_txt, is_correct=choice.is_correct,question_id=db_question.id)
        db.add(db_choice)
        db.commit()
    
