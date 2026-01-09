from app.services.parser import SECParser

def test_clean_text_normalization():
    """
    Test to ensure that extra spaces and line breaks are normalized.
    """
    dirty_text = "This   is  a    messy \n\n text."
    expected = "This is a messy text."
    assert SECParser.clean_text(dirty_text) == expected

def test_html_cleaning_logic():
    """
    Test that the HTML is cleaned up and the tables are preserved.
    """
    html_content = """
    <html>
        <head><script>bad script</script></head>
        <body>
            <p>Paragraph 1</p>
            <table>
                <tr><td>Revenue</td><td>100</td></tr>
            </table>
            <div style="display:none">Hidden noise</div>
        </body>
    </html>
    """

    result = SECParser.clean_html(html_content)

    assert "bad script" not in result
    assert "Paragraph 1" in result
    assert "Revenue" in result
    assert "100" in result