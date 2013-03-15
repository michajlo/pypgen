PyPGen
======

A quick foray into functional parsers, in Python.

Not too sure how to do anything too creative based on my knowledge
of Python syntax/conventions, but a stupid simple caclualtor with
add or subtract is pretty easy:

    int_val = r("[0-9]+").w(int)
    add_or_sub = int_val.then(rep(l("+").oor(l("-")).then(int_val)))

Which for the input "1+2+3-4" will yield `Success((1, [('+', 2), ('+', 3), ('-', 4)]), )`.
Nothing too fancy, but fun to get working to some degree.
