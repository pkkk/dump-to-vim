import terminatorlib.plugin
import terminatorlib.terminal
import tempfile
import re

# AVAILABLE must contain a list of all the classes that you want exposed
AVAILABLE = ['DumpToVimPlugin']
dump_terminal = None
dir_name = None

orig_grab = terminatorlib.terminal.Terminal.grab_focus
def grab_focus(terminal):
    global dump_terminal, dir_name
    if(dir_name == terminal.cwd):
        dump_terminal = terminal
        dir_name = None
    orig_grab(terminal)

def key_search(terminal):
    global dump_terminal, dir_name
    end_row = terminal.vte.get_cursor_position()[1] + terminal.vte.get_row_count()
    text_dump = terminal.vte.get_text_range(0, 0, end_row, 0, lambda *a:True)
    text_dump = re.sub('\s*$', '', text_dump)

    dir_name = dname = tempfile.mkdtemp(prefix='terminator_')
    fname = dname + "/dump_to_vim"

    f = open(fname, 'w')
    f.write(text_dump)
    f.close()

    terminal.emit('split-vert', dname)

    dump_terminal.vte.feed_child('cd ..;vim -c "set nowrap" -R %s;rm -r %s;exit\n' 
        % (fname, dname))
    dump_terminal.vte.feed_child('G0\x19')


class DumpToVimPlugin(terminatorlib.plugin.Plugin):
    capabilities = ['dump, vim']
    def __init__(self):
        terminatorlib.terminal.Terminal.grab_focus = grab_focus
        terminatorlib.terminal.Terminal.key_search = key_search

