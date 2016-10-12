Lectures in the Middle
======================

A statically compiled, online lecture note system.

Concerned that your lecture notes are being left to die in the hole that
is .pdf documents? Want to increase engagement, and ensure that content
is presented in the correct format for all devices? Want a full-text
search that includes your LaTeX math?

Then, boy, do we have the system for you!

This system takes a .tex file (or several of them), and compiles it to a
fancy-looking lecture notes website, like the one available at
< > (Lectures in the Middle was built for this). Just stick in some
of our custom syntax to define where lectures start and the sections you
want the compiler to pick up (as well as keypoints) and you're ready to
go!

Why Middleman?
--------------

University webservers completely suck. Why worry about them, their old,
decrepit PHP & MySQL installations, when you can just pre-compile your
website to html?

We chose middleman because it has fantastic documentation and is very
'back-to-basics' -- it just gave us what we needed.

Dependencies
------------

- ``` pandoc ```
- ``` pandoc-crossref, pandoc-citeproc ``` (install using ```cabal```)
- ``` ruby ``` and ``` bundle ```
- ``` python 3 ```
- The helper module, ``` ltmd ```

Why so many dependencies? For a system like this, it's best if it's fit-
and-forget. That's why we used as many external tools as possible -- the
rest is just short scripts that plug everything together.

Custom Syntax
-------------

These snippets should be placed in your LaTeX code:
- ```%%\lecture{<Lecture Number>}``` to denote the start of the lecture
- ```%%\section{<Section Name>}``` to denote the start of the section
- ```%%\keypoint{<Keypoint>}``` to denote a keypoint.

Usage
-----

Simply put your lecture note .tex files into ```/texfiles```, your images
into ```/web/images/```, and then run the ```compile.py``` script, using
```python3```.

This will, if run with the ```--pdflatex``` flag, also compile your
documents to .pdf files using pdflatex.

### Initial Usage

Initially, you will need to run ```bundle install``` to install the
required ruby dependencies.

Great, but, shouldn't this be in Ruby?
--------------------------------------

Yes.
