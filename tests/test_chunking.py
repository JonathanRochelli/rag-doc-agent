from app.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []


def test_short_text_single_chunk():
    chunks = chunk_text("Bonjour le monde.", chunk_size=800, overlap=150)
    assert len(chunks) == 1
    assert chunks[0].text == "Bonjour le monde."
    assert chunks[0].index == 0


def test_multiple_paragraphs_fit_in_one_chunk():
    text = "Premier paragraphe.\n\nDeuxième paragraphe.\n\nTroisième paragraphe."
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    assert len(chunks) == 1
    assert "Premier paragraphe." in chunks[0].text
    assert "Troisième paragraphe." in chunks[0].text


def test_long_text_splits_into_multiple_chunks():
    paragraph = "Ceci est une phrase de test répétée pour créer du contenu. " * 10
    text = "\n\n".join([paragraph] * 6)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_chunk_indices_are_sequential():
    paragraph = "Mot répété plusieurs fois pour dépasser la taille de chunk. " * 10
    text = "\n\n".join([paragraph] * 5)
    chunks = chunk_text(text, chunk_size=400, overlap=40)
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_overlap_carries_context_between_chunks():
    long_paragraph = "mot " * 300
    chunks = chunk_text(long_paragraph, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    # the tail of a chunk should reappear as a prefix in the next one
    tail_of_first = chunks[0].text[-50:].strip()
    assert tail_of_first[:10] in chunks[1].text
