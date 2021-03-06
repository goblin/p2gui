#!/usr/bin/env python

import os
import platform
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

class P2PoolConfig:
    def __init__(self):
        self.wTree = gtk.glade.XML("ui.glade")
        self.main_window = self.wTree.get_widget("main_window")
        self.main_window.connect("destroy", gtk.main_quit)

        self.conffile = os.path.join(os.path.expanduser('~'), '.p2pool.conf')
        if platform.system() == 'Windows':
            self.conffile =  os.path.join(os.environ['APPDATA'], 'P2Pool', 
                'p2pool.conf')
        elif platform.system() == 'Darwin':
            self.conffile = os.path.join(os.path.expanduser('~'), 'Library', 
                'Application Support', 'P2Pool', 'p2pool.conf')

        dic = { 
            "on_quit": gtk.main_quit,
            "on_save": self.save,
            "on_show_btc_pass_toggled": lambda widget: 
                self.wTree.get_widget("fld_password").set_property(
                    "visibility", widget.get_active()),
            "on_close_dialog_close": gtk.main_quit
        }

        self.wTree.signal_autoconnect(dic)
        self.main_window.show()

    def save(self, widget):
        out_file = open(self.conffile, 'w')
        try:
            for arg in self.wTree.get_widget_prefix('arg_'):
                if arg.get_text() != '':
                    out_file.write(arg.get_name()[4:] + ' ' + 
                        arg.get_text() + '\n')
            for arg in self.wTree.get_widget_prefix('flag_'):
                if arg.get_active():
                    out_file.write(arg.get_name()[5:] + '\n')
            user = self.wTree.get_widget('fld_username').get_text()
            pswd = self.wTree.get_widget('fld_password').get_text()
            if user:
                out_file.write(' '.join((user, pswd)))
        finally:
            out_file.close()

    def read_conf(self):
        cfg_file = open(self.conffile)
        got_user = False
        try:
            for arg_line in cfg_file.read().splitlines():
                if got_user:
                    raise Exception("Config contains arguments after user/password:\n" + arg_line)
                argval = arg_line.split()
                widget = self.wTree.get_widget("arg_" + argval[0])
                if widget is None: # it's either flag or userpass
                    widget = self.wTree.get_widget("flag_" + argval[0])
                    if widget is None: # it's userpass
                        self.wTree.get_widget('fld_username').set_text(argval[0])
                        if len(argval) > 1:
                            self.wTree.get_widget('fld_password').set_text(argval[1])
                        got_user = True
                    else: # it's a flag
                        widget.set_active(True)
                else: # it's an arg
                    widget.set_text(argval[1])
        except:
            raise
        finally:
            cfg_file.close()

    def main(self):
        try:
            try:
                self.read_conf()
            except IOError as ioe:
                if ioe.errno != 2:
                    raise
            except:
                raise
            self.wTree.get_widget("cfg_loc").set_text(self.conffile)
            gtk.main()
        except Exception as exc:
            self.main_window.hide()
            exit_dialog = self.wTree.get_widget("close_dialog")
            exit_dialog.set_markup(exc.__str__())
            exit_dialog.show()
            gtk.main() # it'll quit when a user presses the button

p2pcfg = P2PoolConfig()
p2pcfg.main()

# vim: set expandtab ts=4 sw=4:
