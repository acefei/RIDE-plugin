import os
from robotide import publish
from robotide.pluginapi import Plugin
from wx import wx
from robotide.widgets import VerticalSizer, HorizontalSizer, TextField, Label, HtmlDialog


class PulginTextEditorEnhance(Plugin):
    """This plugin description."""
    def __init__(self, ride_app_ref):
        Plugin.__init__(self, ride_app_ref, initially_enabled=False)

    def enable(self):
        self.log('Plugin template enabled')
        self._build_ui()

    def disable(self):
        self.log('Plugin template disabled')

    def _build_ui(self):
        """Creates the UI for this plugin"""
        self._build_notebook_tab()

    def _build_notebook_tab(self):
        self.editor = SourceEditor(self.notebook, title='CafeEditor')

    # RIDE log
    def log(self, data):
        publish.RideLogMessage(data).publish()


class SourceEditor(wx.Panel):
    def __init__(self, parent, title):
        wx.Panel.__init__(self, parent)
        self._parent = parent
        self._create_ui(title)
        self.dirname = ''
        self.file_edited = None
        self.autosave_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.autosave_timer)
        self.autosave_timer.Start(60000*10)

    def _create_ui(self, title):
        self.SetSizer(VerticalSizer())
        self._create_editor_toolbar()
        self._create_editor_text_control()

        # Add the plugin into the table
        self._parent.add_tab(self, title, allow_closing=False)

    def _create_editor_toolbar(self):
        self.toolbar = HorizontalSizer()
        
        # Add open button
        self.open_button = wx.Button(self, label='Open', size=(-1, 25))
        self.toolbar.add_with_padding(self.open_button)
        self.open_button.Bind(wx.EVT_BUTTON, self.OnOpen)

        self.save_button = wx.Button(self, label='Save', size=(-1, 25))
        self.toolbar.add_with_padding(self.save_button)
        self.save_button.Bind(wx.EVT_BUTTON, self.OnSave)

        self.toolbar.add_with_padding(Label(self, label="Auto Save Frequency in min:"), padding=10)
        self.autosave_field = TextField(self, '', process_enters=True)
        self.autosave_field.Bind(wx.EVT_TEXT_ENTER, self.OnChangeTimer)
        self.toolbar.add_with_padding(self.autosave_field)

        # Add the tool bar into sizer
        self.Sizer.add_expanding(self.toolbar, propotion=0)

    def _create_editor_text_control(self):
        self.text = wx.stc.StyledTextCtrl(self, style=wx.TE_MULTILINE|wx.NO_BORDER|wx.WANTS_CHARS)
        self.text.SetCaretLineVisible(True)
        self.text.SetCaretWidth(3)
        self.text.SetUseAntiAliasing(True)

        style = self.text.GetStyleAt(0)
        self.text.StyleSetEOLFilled(style, True)
        self.text.SetMargins(0, 0)
        self.text.SetMarginWidth(1, 0)
        self.text.SetWrapMode(wx.stc.STC_WRAP_WORD)

        # Add the text panel into sizer
        self.Sizer.add_expanding(self.text)
        self.Sizer.Layout()

    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            # Open the file, read the contents and set them into
            # the text edit window
            self.file_edited = dlg.GetPath()
            fh = open(self.file_edited, 'r')
            self.text.SetText(fh.read())
            fh.close()

        dlg.Destroy()

    def OnSave(self, event):
        if not self.file_edited:
            return
        fh = open(self.file_edited, 'w')
        fh.write(self.text.GetText())
        fh.close()

    def OnTimer(self, event):
        self.OnSave(event)
        publish.RideLogMessage('Text Editor Saving.').publish()

    def OnChangeTimer(self, event):
        timer = self.autosave_field.GetValue()
        if int(timer) == 0:
            if self.autosave_timer.IsRunning():
                self.autosave_timer.Stop()
                publish.RideLogMessage('Auto Save Timer Stop.').publish()
        elif 0 < int(timer) <= 60:
            if self.autosave_timer.IsRunning():
                self.autosave_timer.Stop()

            self.autosave_timer.Start(int(timer)*60000)
            publish.RideLogMessage('Auto Save Timer Start.').publish()
        else:
            massages = '''<h1><br>Warning</h1>
            <p>The Timer range is 0 - 60.</p>
            '''
            HtmlDialog(title='WARNING', content=massages).Show()
