pub func rect(x : int, y : int, width : int, height : int) {
    use <psgraph>
    
    for i : 1 to height {
        psgraph::gotoxy(x, y + i - 1)
        for j : 1 to width {
            write("0")
        }
    }
}