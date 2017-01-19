"""prompt-toolkit utilities

Everything in this module is a private API,
not to be used outside IPython.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import unicodedata
from wcwidth import wcwidth

from IPython.core.completer import IPCompleter, provisionalcompleter
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.layout.lexers import Lexer
from prompt_toolkit.layout.lexers import PygmentsLexer

import pygments.lexers as pygments_lexers

_completion_sentinel = object()

from functools import wraps

def _completion_debugger(function):
    """
    Wrapper that will analyse completion sent both before and after the
    _completion_sentinel and mark those in the second group not in the first.
    """
    @wraps(function)
    def new_get_completions(self, document, complete_event):
        completions  = list(function(self, document, complete_event))
        from_jedi = []
        from_ipython = []
        push = from_jedi
        for e in completions:
            if e is _completion_sentinel:
                push = from_ipython
            else:
                push.append(e)
        yield from from_jedi
        if any([(_completion_sentinel is c) for c in completions]):
            yield Completion('', display='--- jedi/ipython ---')
        yield from [a for a in from_ipython if a not in from_jedi]
    return new_get_completions


class IPythonPTCompleter(Completer):
    """Adaptor to provide IPython completions to prompt_toolkit"""
    def __init__(self, ipy_completer=None, shell=None):
        if shell is None and ipy_completer is None:
            raise TypeError("Please pass shell=an InteractiveShell instance.")
        self._ipy_completer = ipy_completer
        self.shell = shell

    @property
    def ipy_completer(self):
        if self._ipy_completer:
            return self._ipy_completer
        else:
            return self.shell.Completer

    @_completion_debugger
    def get_completions(self, document, complete_event):
        if not document.current_line.strip():
            return

        # Some bits of our completion system may print stuff (e.g. if a module
        # is imported). This context manager ensures that doesn't interfere with
        # the prompt.
        with self.shell.pt_cli.patch_stdout_context():
            with provisionalcompleter():
                used, matches, jedi_matches = self.ipy_completer._complete(
                                line_buffer=document.current_line, # get full bugger here
                                cursor_pos=document.cursor_position_col,
                                cursor_line=document.cursor_position_row,
                                full_text=document.text,
            )

        if jedi_matches:
            for jm in jedi_matches:
                delta = len(jm.name_with_symbols) - len(jm.complete)
                if delta >  document.cursor_position_col or delta  < 0:
                    raise ValueError('OhNoooo this completion went wrong, please report a bug with : \n'
                            '   delta: %s \n' 
                            '   cursor_position: %s\n'
                            '   jedimatch %s|%s \n' % 
                            (delta,document.cursor_position_col,jm.name, jm.complete))
                yield Completion(jm.name_with_symbols, start_position=-delta, display=jm.name_with_symbols)

            # use for debug purpose to visually show a separation between the jedi
            # and IPython base completions.
        if jedi_matches is not None:
            yield _completion_sentinel

        start_pos = -len(used)
        for m in matches:
            if not m:
                # Guard against completion machinery giving us an empty string.
                continue

            m = unicodedata.normalize('NFC', m)

            # When the first character of the completion has a zero length,
            # then it's probably a decomposed unicode character. E.g. caused by
            # the "\dot" completion. Try to compose again with the previous
            # character.
            if wcwidth(m[0]) == 0:
                if document.cursor_position + start_pos > 0:
                    char_before = document.text[document.cursor_position + start_pos - 1]
                    m = unicodedata.normalize('NFC', char_before + m)

                    # Yield the modified completion instead, if this worked.
                    if wcwidth(m[0:1]) == 1:
                        yield Completion(m, start_position=start_pos - 1)
                        continue

            # TODO: Use Jedi to determine meta_text
            # (Jedi currently has a bug that results in incorrect information.)
            # meta_text = ''
            # yield Completion(m, start_position=start_pos,
            #                  display_meta=meta_text)
            yield Completion(m, start_position=start_pos)


class IPythonPTLexer(Lexer):
    """
    Wrapper around PythonLexer and BashLexer.
    """
    def __init__(self):
        l = pygments_lexers
        self.python_lexer = PygmentsLexer(l.Python3Lexer)
        self.shell_lexer = PygmentsLexer(l.BashLexer)

        self.magic_lexers = {
            'HTML': PygmentsLexer(l.HtmlLexer),
            'html': PygmentsLexer(l.HtmlLexer),
            'javascript': PygmentsLexer(l.JavascriptLexer),
            'js': PygmentsLexer(l.JavascriptLexer),
            'perl': PygmentsLexer(l.PerlLexer),
            'ruby': PygmentsLexer(l.RubyLexer),
            'latex': PygmentsLexer(l.TexLexer),
        }

    def lex_document(self, cli, document):
        text = document.text.lstrip()

        lexer = self.python_lexer

        if text.startswith('!') or text.startswith('%%bash'):
            lexer = self.shell_lexer

        elif text.startswith('%%'):
            for magic, l in self.magic_lexers.items():
                if text.startswith('%%' + magic):
                    lexer = l
                    break

        return lexer.lex_document(cli, document)
