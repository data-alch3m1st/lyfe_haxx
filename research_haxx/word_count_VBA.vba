Sub WordCount_ExcludeFootnotesAndPage1()
    Dim doc As Document
    Dim mainRange As Range
    Dim startPage2 As Range
    Dim countRange As Range
    Dim totalWords As Long
    Dim page1Words As Long
    Dim msg As String

    Set doc = ActiveDocument

    ' Ensure layout is up-to-date (force repagination)
    doc.Repaginate

    ' Get the main document story (main flow)
    Set mainRange = doc.StoryRanges(wdMainTextStory)

    ' If the document has fewer than 2 pages, result is zero after excluding page 1
    If doc.ComputeStatistics(wdStatisticPages) < 2 Then
        MsgBox "Document has fewer than 2 pages. Word count excluding page 1: 0", vbInformation
        Exit Sub
    End If

    ' Find the start of page 2 within the main story.
    ' Use GoTo to move to page 2; then create a range from that point to the end of the main story.
    Set startPage2 = doc.Range(0, 0)
    On Error Resume Next
    Set startPage2 = doc.GoTo(What:=wdGoToPage, Which:=wdGoToAbsolute, Count:=2)
    On Error GoTo 0

    ' The GoTo can place the range inside headers/footers if not careful,
    ' so ensure we request a range within the main story by intersecting with mainRange.
    If startPage2.Start < mainRange.Start Then startPage2.Start = mainRange.Start
    If startPage2.End > mainRange.End Then startPage2.End = mainRange.End

    ' Build the counting range: from start of page 2 to the end of the mainStory
    Set countRange = doc.Range(Start:=startPage2.Start, End:=mainRange.End)

    ' Remove any content that belongs to footnotes or endnotes — though main story excludes those,
    ' some reference markers remain; we will count only words in the countRange as-is.
    totalWords = countRange.Words.Count

    msg = "Word count excluding footnotes/endnotes and excluding page 1: " & totalWords
    MsgBox msg, vbInformation
End Sub