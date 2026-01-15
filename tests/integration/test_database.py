import pytest
from sqlmodel import select
from app.models.report import FinancialReport


@pytest.mark.asyncio
async def test_vector_similarity_search(db_session):
    """
    Scientific proof:
    We insert two documents with orthogonal (distinct) vectors.
    We search for a query vector that is identical to one of them.
    The database should return the correct one based on the cosine distance.
    """
    vec_a = [1.0] * 5 + [0.0] * 763
    vec_b = [0.0] * 5 + [1.0] * 5 + [0.0] * 758

    doc_a = FinancialReport(
        company_ticker="TEST_A",
        year=2025,
        report_type="10-K",
        section="Intro",
        content="This is Document A",
        embedding=vec_a,
    )

    doc_b = FinancialReport(
        company_ticker="TEST_B",
        year=2025,
        report_type="10-K",
        section="Risk",
        content="This is Document B",
        embedding=vec_b,
    )

    db_session.add(doc_a)
    db_session.add(doc_b)
    await db_session.commit()

    query_vec = vec_a

    statement = (
        select(FinancialReport)
        .order_by(FinancialReport.embedding.cosine_distance(query_vec))
        .limit(1)
    )

    result = await db_session.execute(statement)
    found_doc = result.scalar_one()

    assert found_doc.company_ticker == "TEST_A"
    assert found_doc.content == "This is Document A"

    await db_session.delete(doc_a)
    await db_session.delete(doc_b)
    await db_session.commit()


@pytest.mark.asyncio
async def test_database_persistence(db_session):
    """
    Simple CRUD test: Save and Read.
    """
    new_report = FinancialReport(
        company_ticker="CRUD_TEST",
        year=2024,
        report_type="10-Q",
        section="Test",
        content="Persistence check",
        embedding=[0.0] * 768,
    )
    db_session.add(new_report)
    await db_session.commit()
    await db_session.refresh(new_report)

    assert new_report.id is not None

    statement = select(FinancialReport).where(
        FinancialReport.company_ticker == "CRUD_TEST"
    )
    result = await db_session.execute(statement)
    fetched = result.scalar_one()

    assert fetched.content == "Persistence check"

    await db_session.delete(fetched)
    await db_session.commit()
