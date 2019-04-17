import kivy

kivy.require("1.9.0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from collections import OrderedDict
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.base import EventLoop
import openpyxl
import mysql.connector
import os

# Change default Window size
from kivy.config import Config

Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'width', 1500)
Config.set('graphics', 'minimum_width', 800)
Config.set('graphics', 'height', 800)
Config.set('kivy', 'exit_on_escape', '0')
Config.write()

Builder.load_string("""
######################################################    MISC    ######################################################
<MenuBoxLayout>
    padding: 10,10,10,10
    canvas.before:
        Color:
            rgba: 1,1,1,0.05
        Rectangle:
            pos: self.pos
            size: self.size

<AuditTitleLayout>
    canvas.before:
        Color:
            rgba: 1,1,1,0.2
        Rectangle:
            pos: self.pos
            size: self.size

#####################################################    POPUPS    #####################################################
<ErrorTitlePopup>:
    title: "Error"
    size_hint: None, None    
    size: 300, 100

<YNPopup>:
    size_hint: None, None    
    auto_dismiss: False
    BoxLayout:
        size_hint: 1, 1
        orientation: 'vertical'
        BoxLayout:
            id: msgbox
            size_hint: 1, .75
            Label:
                halign: 'center'
                size_hint: 1, 1
                id: msg
        BoxLayout:
            size_hint: 1, .25
            orientation: 'horizontal'
            Button:
                id: yes
                size_hint: .5, None
                height: 35
                text: "Yes"
                on_press: 
                    root.to_closed()
                    root.dismiss()
            Button:
                size_hint: .5, None
                height: 35
                text: "Cancel"
                on_release: 
                    root.not_to_closed()
                    root.dismiss()

<QuitPopup>:
    title: "Exit program?"
    size_hint: None, None    
    size: 400, 100
    auto_dismiss: False
    BoxLayout:
        size_hint: 1, 0.9
        orientation: 'horizontal'
        Button:
            size_hint: 1, 1
            text: "Yes"
            on_release: root.quitScreen()
        Button:
            size_hint: 1, 1
            text: "Cancel"
            on_release: root.dismiss()

<AuditNotePopup>
    title: "Set Audit Note"
    size_hint: None,None		
    size: 500,500		
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        padding: 10,10,10,10
        TextInput:
            id: a_note
            size_hint: 1, .7
            text: root.get_audit_note()
        Button:
            size_hint: 1, .15
            text: 'Save'
            background_color: (.75, .75, .75, 1.0)
            on_press: root.edit_audit_note(a_note)
            on_release: root.dismiss()
        Button:
            size_hint: 1,.15
            text: 'Cancel'
            background_color: (.75, .75, .75, 1.0)
            on_release:
                root.dismiss()

<CreatedAuditPopup>
    title: "Audit successfully created & opened!"
    size_hint: None,None		
    size: 350,350		
    auto_dismiss: False
    BoxLayout:
        size_hint: 1,1
        orientation: 'vertical'
        ScrollView:
            size_hint: 1,.8
            bar_width: 5
            Label:
                id: capl
                padding: (10,10)
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                color: (1,1,1,.75)
                text: ''
        Button:
            size_hint: 1,.2
            text: 'OK'
            on_release: root.dismiss()

####################################################    SCREENS    #####################################################
<MenuScreen>:
    on_pre_enter: grid.update_buttons(grid)
    BoxLayout:
        size_hint: 1,1 
        orientation: 'vertical'
        # [padding_left, padding_top, padding_right, padding_bottom]
        padding: 75,50,75,60
        BoxLayout:
            size_hint: 1,.1
            padding: 0,0,0,15
            Label:
                pos_hint: {'center_x': 0.5,'center_y': 0.5}
                text: "GOES-R Audits"
                font_size: 30
                bold: True
        MenuBoxLayout:
            size_hint: 1,.73
            pos_hint: {'center_x': 0.5,'center_y': 0.5}
            ScrollView:
                bar_width: 7
                scroll_type: ['bars', 'content']
                size_hint: 1,1
                SelectableGrid:
                    size_hint: 1, None
                    cols: 1
                    multiselect: False
                    id: grid
        BoxLayout:
            size_hint: 1,.07
        Button:
            size_hint: 1,.1
            text: "Begin New Audit"
            font_size: 18
            on_release: root.permission_new_audit()

<NewAuditScreen>:
    on_pre_enter: root.changeRootpath(fc)
    id: NewAuditScreen
    BoxLayout:
        size_hint: 1,1
        orientation: 'vertical'
        padding: 10,10,10,10
        BoxLayout:
            size_hint: .15,.05
            Button:
                background_color: 1,1,1,0.5
                text: 'Back to Audits'
                on_release:
                    root.manager.transition.direction = 'right'
                    root.manager.current = 'menu'
        BoxLayout:
            size_hint: 1,.88
            orientation: 'vertical'
            # [padding_left, padding_top, padding_right, padding_bottom]
            padding: 50,0,50,20
            MenuBoxLayout:
                size_hint: 1,.1
                orientation: 'horizontal'
                AnchorLayout:
                    size_hint: .15,1
                    padding: 20,0,20,0
                    Label:
                        width: len(a_name_lab.text)*10
                        id: a_name_lab
                        text: "Audit Title:"
                        font_size: 22
                AnchorLayout:
                    padding: 5,0,10,0
                    size_hint: .45,1
                    TextInput:
                        id: a_name
                        multiline: False
                        write_tab: False
                        size_hint: 1,None
                        height: 40
                        font_size: 20
                BoxLayout:
                    size_hint: .1,1
                Button:
                    size_hint: .2,1
                    text: 'Set Audit Note'
                    on_press: root.note_popup()
            BoxLayout:
                size_hint: 1,.05
            MenuBoxLayout:
                id: fileSection
                size_hint: 1,.8
                orientation: 'vertical'
                BoxLayout:
                    size_hint: 1, .06
                    AnchorLayout:
                        size_hint: None,1
                        anchor_x: 'left'
                        anchor_y: 'top'
                        width: len(ubtn.text)*10
                        Label:
                            id: ubtn
                            text: 'Chosen File Path: '
                            font_size: 17
                    AnchorLayout:
                        size_hint: .75,1
                        anchor_x: 'right'
                        anchor_y: 'top'
                        padding: 0,0,20,0
                        TextInput:
                            size_hint: 1,1
                            id: cfp
                BoxLayout:
                    size_hint: 1, .92
                    orientation: 'vertical'
                    padding: 20,10,20,20
                    AnchorLayout:
                        size_hint: 1,.1
                        padding: 270,0,0,0
                        anchor_x: 'left'
                        Label:
                            size_hint: None,None
                            text: "Please select an Excel file (e.g. \'.xlsx\').  Single-click to enter folder.  Double-click to choose file."
                            italic: True
                    MenuBoxLayout:
                        orientation: 'vertical'
                        size_hint: 1,.82
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint: 1,1
                            BoxLayout:
                                size_hint: .3, .15
                                size_hint_y: None
                                height: sp(40)
                                ToggleButton:
                                    group: 'fileview'
                                    allow_no_selection: False
                                    state: 'down'
                                    size_hint: .5,1
                                    text: 'Icon View'
                                    background_normal: ''
                                    background_color: (.2,.2,.2,1)
                                    on_press: fc.view_mode = 'icon'
                                ToggleButton:
                                    group: 'fileview'
                                    allow_no_selection: False
                                    size_hint: .5,1
                                    text: 'List View'
                                    background_normal: ''
                                    background_color: (.2,.2,.2,1)
                                    on_press: fc.view_mode = 'list'
                            FileChooser:
                                id: fc
                                rootpath: ""
                                FileChooserIconLayout:
                                    on_submit: root.upload(fc, cfp)
                                FileChooserListLayout:
                                    on_submit: root.upload(fc, cfp)
        BoxLayout:
            size_hint: 1,.07
            AnchorLayout:
                anchor_x: 'right'
                size_hint: .25, 1
                Button:
                    size_hint: .25,1
                    text: 'Create Audit'
                    font_size: 20
                    on_press: root.check_inputs(a_name, cfp, fc)

<AuditScreen>
    on_pre_enter: 
        root.manager.transition.direction = 'left'
        root.load_audit(anb, anlbl)
    BoxLayout:
        size_hint: 1, 1
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,.935
            AuditTitleLayout:
                id: anb
                size_hint: None,.05
                Label:
                    id: anlbl
            BoxLayout:
                size_hint: 1,.95
        BoxLayout:		
            size_hint: 1,.065
            Button:		
                text: 'Menu'
                id: menu_btn
                background_color: (.3,.3,.3,1)
                on_press: root.manager.transition.direction = 'right'		
                on_press: root.manager.current = 'menu'

""")

########################################################################################################################
# ScreenManager created here instead of in build() so it can be used by methods to swap screens on button press(es)
sm = ScreenManager()
new_audit_note = ""

global loaded_audit
loaded_audit = ""

# Connect to mysql db
try:
    conn = mysql.connector.connect(user="root", password="", host='127.0.0.1')
    cur = conn.cursor()
except mysql.connector.DatabaseError as e:
    print(e)


def SQL_pca_db_dict():
    cur.execute("USE pcaDBs;")

    cur.execute("SELECT name, title, closed FROM db_info ORDER BY name DESC")
    rows = cur.fetchall()

    pca_db_dict = {}
    audit_status = {}

    for row in rows:
        # Create name:title dictionary
        pca_db_dict[str(row[0])] = str(row[1])

        # Create name:status dictionary
        if row[2] is None:
            audit_status[str(row[1])] = "o"
        else:
            audit_status[str(row[1])] = "c"

    # Reorder pca_db_dict by key in descending order (e.g. pca4, pca3, pca2, pca1)
    ordered_pca_db_dict = OrderedDict(sorted(pca_db_dict.items(), key=lambda t: t[0], reverse=True))

    return ordered_pca_db_dict, audit_status


def SQL_data_verification(data_list):
    good_to_go = True

    for item in data_list:
        if '"' in item:
            good_to_go = False

    return good_to_go


######################################################    MISC    ######################################################
class SelectableGrid(CompoundSelectionBehavior, GridLayout):
    n_list = []
    b_list = []
    global pca_Dict
    global status_Dict
    pca_Dict, status_Dict = SQL_pca_db_dict()

    def update_buttons(self, grid):
        global pca_Dict
        global status_Dict

        # Clear selectable grid and b_list
        grid.clear_widgets()
        self.b_list = []

        for db_name in pca_Dict.keys():
            self.b_list.append(pca_Dict[db_name])

        # Use faded text color if audit is closed
        for title in self.b_list:
            if status_Dict[title] == "c":
                btn = Button(text=str(title), font_size=18, size=(50, 50),
                             color=(1, 1, 1, .4), background_color=(.5, .5, .5, 1))
            else:
                btn = Button(text=str(title), font_size=18, size=(50, 50))
            grid.add_widget(btn)

        self.g = grid
        self.size = (50, self.get_num_audits() * 50)

        return grid

    def add_widget(self, widget):
        """ Override the adding of widgets so we can bind and catch their
        *on_touch_down* events. """
        widget.bind(on_touch_down=self.button_touch_down,
                    on_touch_up=self.button_touch_up)
        self.n_list.append(widget)
        return super(SelectableGrid, self).add_widget(widget)

    def button_touch_down(self, button, touch):
        """ Use collision detection to select buttons when the touch occurs
        within their area. """
        if button.collide_point(*touch.pos):
            self.select_with_touch(button, touch)

    def button_touch_up(self, button, touch):
        """ Use collision detection to de-select buttons when the touch
        occurs outside their area and *touch_multiselect* is not True. """
        if not (button.collide_point(*touch.pos) or
                self.touch_multiselect):
            self.deselect_node(button)

    def select_node(self, node):
        node.background_color = (0, 182, 229, .667)

        x = node.parent.parent.parent.parent.parent.parent
        try:
            x.refresh_table(node.text, x.ids.oBox1, x.ids.jbox, x.ids.mbox1, x.ids.grid)
        except AttributeError:
            pass

        return super(SelectableGrid, self).select_node(node)

    def deselect_node(self, node):
        global status_Dict
        if status_Dict[node.text] == "c":
            node.background_color = (.5, .5, .5, 1)
        else:
            node.background_color = (1, 1, 1, 1)
        super(SelectableGrid, self).deselect_node(node)

    def on_selected_nodes(self, grid, nodes):
        # Repopulate selectable grid and b_list
        for node in nodes:
            global loaded_audit
            loaded_audit = node.text

            status_Dict = SQL_pca_db_dict()[1]

            if status_Dict[node.text] == 'c':
                # Label(="This audit has already been closed.\nDo you still wish to continue?")
                popup = YNPopup(title="Note:", size=(300, 175))
                popup.ids.msg.text = "This audit has already been closed.\nDo you still wish to continue?"
                popup.open()
                self.deselect_all_nodes(grid)
            else:
                sm.current = "audit"
                self.deselect_all_nodes(grid)

        return

    def select_all_nodes(self, grid):
        for node in grid.children:
            # Can change color of selected button
            node.background_color = (0, 182, 229, .667)
            super(SelectableGrid, self).select_node(node)

    def deselect_all_nodes(self, grid):
        global status_Dict

        for node in grid.children:
            if status_Dict[node.text] == "c":
                node.background_color = (.5, .5, .5, 1)
            else:
                node.background_color = (1, 1, 1, 1)
            super(SelectableGrid, self).deselect_node(node)

    def get_num_audits(self):
        """gets number of jlabs
        :return: length of list, int"""
        return len(self.b_list)


class MenuBoxLayout(BoxLayout):
    pass


class AuditTitleLayout(BoxLayout):
    pass


#####################################################    POPUPS    #####################################################
class YNPopup(Popup):
    def to_closed(self):
        sm.transition.direction = 'left'
        sm.current = 'audit'

    def not_to_closed(self):
        global loaded_audit
        loaded_audit = ""


class ErrorTitlePopup(Popup):
    pass


class CreatedAuditPopup(Popup):
    pass


class QuitPopup(Popup):
    """Class to quit screen when 'yes' is selected in the popup
    :param: None
    :return: None
    """

    def quitScreen(self):
        """ calls exit"""
        # if 'cur' in globals():
        #     cur.close()
        # if 'conn' in globals():
        #     conn.close()
        exit(1)


class AuditNotePopup(Popup):

    def edit_audit_note(self, a_note):
        global new_audit_note
        new_audit_note = a_note.text

    def get_audit_note(self):
        return new_audit_note


####################################################    SCREENS    #####################################################
class MenuScreen(Screen):

    def permission_new_audit(self):
        # Check if all audits are closed
        cur.execute("USE pcaDBs")
        cur.execute("SELECT title FROM db_info WHERE closed IS NULL")
        row = cur.fetchone()
        if row is None:
            sm.transition.direction = 'left'
            sm.current = 'new_audit'
        else:
            for title in row:
                not_closed = str(title)
            popup = CreatedAuditPopup(title="Sorry...", size=(350, 215))
            popup.ids.capl.text = "You cannot begin a new audit because \'{}\' is still open.\n\nPlease select and close \'{}\' first.".format(
                not_closed, not_closed)
            popup.open()


class NewAuditScreen(Screen):

    def changeRootpath(self, fc):
        if os.name == 'nt':
            fc.rootpath = "C:/"
        else:
            fc.rootpath = "/home"

    def note_popup(self):
        print self.children[0].children[1].children[0].children[0].children[0].children[0].children[0].rootpath
        popup = AuditNotePopup()
        popup.open()

    def check_inputs(self, a_name, cf, filechooser):
        # Verify data
        global new_audit_note

        ver_list = [a_name.text, new_audit_note]

        if SQL_data_verification(ver_list):
            # Extract file name for Popup
            if len(filechooser.path) > 1:
                filename = filechooser.selection[0].replace((filechooser.path + "/"), "")
            else:
                filename = filechooser.selection[0].replace("/", "")

            # Check audit name, file, and note
            if len(a_name.text) == 0:
                self.popup = ErrorTitlePopup(content=Label(text="Please title this audit."))
                self.popup.open()
            elif len(cf.text) == 0:
                self.popup = ErrorTitlePopup()
                self.popup.content = Label(text="Please select a file for this audit.")
                self.popup.open()
            else:
                if len(new_audit_note) > 0:
                    self.create_audit(a_name, cf, True, filename)
                else:
                    self.popup = Popup(title="Note:", size=(300, 175), size_hint=(None, None))

                    no_note_bl = BoxLayout(orientation='vertical', size_hint=(1, 1))

                    no_note_msg = Label(text="You did not set a note for this audit.\nContinue anyway?",
                                        halign='center', size_hint=(1, .7))
                    no_note_bl.add_widget(no_note_msg)

                    yes_no_bl = BoxLayout(orientation='horizontal', size_hint=(1, .3))
                    no_btn = Button(text="No")
                    no_btn.bind(on_press=lambda x: self.popup.dismiss())
                    yes_btn = Button(text="Yes")
                    yes_btn.bind(on_press=lambda y: self.popup.dismiss())
                    yes_btn.bind(on_press=lambda z: self.create_audit(a_name, cf, False, filename))
                    yes_no_bl.add_widget(no_btn)
                    yes_no_bl.add_widget(yes_btn)
                    no_note_bl.add_widget(yes_no_bl)

                    self.popup.content = no_note_bl
                    self.popup.open()
        else:
            popup = ErrorTitlePopup()
            popup.content = Label(text="Sorry, input cannot include quotation marks (i.e. \'\"\').")
            popup.width = 400
            popup.open()

    def create_audit(self, a_name, cf, note_bool, the_file):
        pca_dbs = self.SQL_get_pca_dbs()
        new_db_num = len(pca_dbs) + 1
        audit_created = False

        # try:
        db_name = "pca{}".format(new_db_num)
        # Create the new database
        cur.execute("CREATE DATABASE {}".format(db_name))
        # Add the new database's name, title (i.e. user-given name), note (or NULL if no note),
        # open date (i.e. today), and close date (defaults to NULL) to db_info table in pcaDBs database
        cur.execute("USE pcaDBs")
        if len(new_audit_note) > 0:
            cur.execute(
                "INSERT INTO db_info (name, title, note) VALUES(\"{}\",\"{}\",\"{}\")".format(db_name, a_name.text,
                                                                                              new_audit_note))
        else:
            cur.execute(
                "INSERT INTO db_info (name, title, note) VALUES(\"{}\",\"{}\",NULL)".format(db_name, a_name.text))

        self.PYXL_parse_data(cf.text, db_name)

        # Save changes to server, sealing changes
        conn.commit()
        audit_created = True
        # except (Exception, mysql.connector.DatabaseError) as e:
        #     # Drop newly created database and remove from db_info in pcaDBs
        #     cur.execute("USE pcaDBs")
        #     cur.execute("DELETE FROM db_info WHERE name = 'pca5'")
        #     cur.execute("DROP DATABASE {}".format(db_name))
        #     # conn.commit()
        #
        #     # Use edited version of CreatedAuditPopup to tell user of error
        #     popup = CreatedAuditPopup(title="Sorry, the audit could not be created.", size=(350, 200))
        #     popup.ids.capl.text = str(e)
        #     popup.open()

        # Have PopUp indicate success or failure of audit db creation
        self.create_audit_results(a_name, db_name, cf, note_bool, the_file, audit_created)

    def PYXL_parse_data(self, filepath, db_name):
        self.SQL_create_table(db_name)

        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)

        # Print name of sheets in workbook
        sheetNameList = wb.sheetnames

        # If success stays an empty string, inventory table was successfully populated
        success = ''

        # Read in and save to table
        for name in sheetNameList:
            self.PYXL_populate_table(wb, name)

    def PYXL_populate_table(self, book, name):
        maximo_fields = {}
        insert_dict = {}
        ws = book[name]
        zone = name.split(' ', 1)[0]

        # Read in and save to table
        rowCnt = 1
        for row in ws.rows:
            if rowCnt == 1:
                # Get header order from Excel sheet
                i = 0
                for cell in row:
                    maximo_fields[i] = str(cell.value)
                    i += 1
                # print "MF: ", maximo_fields

                insert_dict = self.SQL_inventory_switch()
                # print "ID: ", insert_dict
            else:
                curr_row_dict = {}

                for i in range(len(row)):
                    curr_row_dict[maximo_fields.get(i)] = str(row[i].value).replace('"', '\"')

                # print "CRD: ", curr_row_dict

                # Parse PHYSICAL_LOCATION
                phys_loc_fields = ['system_type', 'site', 'room', 'rack']
                phys_loc_dict = {}

                if str(curr_row_dict['PHYSICAL_LOCATION']) != 'None':
                    loc_parts = curr_row_dict['PHYSICAL_LOCATION'].split('-', 4)
                    if len(loc_parts) > 2:
                        loc_parts[2:4] = ['-'.join(loc_parts[2:4])]

                for j in range(len(phys_loc_fields)):
                    try:
                        phys_loc_dict[phys_loc_fields[j]] = loc_parts[j]
                    except IndexError:
                        phys_loc_dict[phys_loc_fields[j]] = 'NULL'
                    j += 1

                curr_row_dict.pop('PHYSICAL_LOCATION')

                # print "phys_loc_dict: ", phys_loc_dict

                for key in phys_loc_dict:
                    curr_row_dict[key] = phys_loc_dict[key]

                # CREATE INSERT STATEMENT
                curr_insert = "INSERT INTO inventory VALUES(NULL,\'{}\',".format(zone)

                print "curr_insert:"
                print curr_insert
                print "insert_dict:"
                print insert_dict


                for i in range(2, len(insert_dict)):
                    print(insert_dict[i])
                    if str(curr_row_dict[insert_dict[i]]) is None:
                        curr_insert += "NULL,"
                    elif str(curr_row_dict[insert_dict[i]]) == "A":
                        curr_insert += "\'Antenna\',"
                    elif str(curr_row_dict[insert_dict[i]]) == "G":
                        curr_insert += "\'Ground\',"
                    else:
                        curr_insert += "\'" + str(curr_row_dict[insert_dict[i]]) + "\',"

                curr_insert = curr_insert[:-1] + ")"

                try:
                    cur.execute(curr_insert)
                except Exception as e:
                    print str(e)
                    print curr_insert

                # print "CI: ", curr_insert
                # print(curr_insert)

            rowCnt += 1

    def SQL_inventory_switch(self):
        """
        makes a switch statement from Machine table (minus machine_code) to be used in write_changes() to identify
        which Machine field(s) have been changed...returns column name of changed field(s)
        :param arg: index (in both list and switch) of changed field
        :return: column name of changed field
        """
        col_names = []

        cur.execute("SHOW COLUMNS FROM inventory")
        rows = cur.fetchall()

        for row in rows:
            col_names.append(str(row[0]))

        switch = {}
        for i in range(len(col_names)):
            switch[i] = col_names[i]

        return switch

    def SQL_create_table(self, db_name):
        cur.execute("USE {}".format(db_name))
        # Does not account for duplicates
        cur.execute("SELECT DATABASE();")
        print (cur.fetchall())
        cur.execute("CREATE TABLE inventory ("
                    "status TEXT, "
                    "comment TEXT,"
                    "zone TEXT, "
                    "system_type TEXT, "
                    "site TEXT, "
                    "room TEXT, "
                    "rack TEXT, "
                    "PROPERTY_NUMBER TEXT, "
                    "HOSTNAME TEXT, "
                    "COMPONENT_TYPE TEXT, "
                    "MANUFACTURER TEXT, "
                    "MODEL_NUMBER TEXT, "
                    "SERIAL_NUMBER TEXT, "
                    "COMPONENT_REV TEXT, "
                    "ASSET_NUMBER TEXT);")

        conn.commit()

    def SQL_get_pca_dbs(self):
        cur.execute("SHOW DATABASES;")
        rows = cur.fetchall()

        pca_dbs = []

        for row in rows:
            if "pca" in str(row[0]) and str(row[0]) != "pcaDBs":
                pca_dbs.append(str(row[0]))

        return pca_dbs

    def create_audit_results(self, a_name, db_name, cf, note_bool, the_file, created_bool):
        if created_bool:
            if note_bool:
                # There IS a note
                # Format CreatedAuditPopup Label
                cap_lab = "Title:\n     {}\n\n".format(a_name.text) + "Database Name:\n     {}\n\n".format(
                    db_name) + "Intake File:\n     {}\n\n".format(the_file) + "Audit Note:\n{}".format(new_audit_note)
                # BUG 3: MAKE HEADERS BOLD IN STRING
                popup = CreatedAuditPopup()
                popup.ids.capl.text = cap_lab
                popup.open()

                # Clear note
                global new_audit_note
                new_audit_note = ''
            else:
                # There is NOT a note
                # Format CreatedAuditPopup Label
                cap_lab = "Audit Title:\n     {}\n\n".format(a_name.text) + "Database Name:\n     {}\n\n".format(
                    db_name) + "Intake File:\n     {}\n\n".format(the_file)

                popup = CreatedAuditPopup()
                popup.ids.capl.text = cap_lab
                popup.open()

            # Clear audit name and chosen file path TextInputs
            a_name.text = ''
            cf.text = ''

    def upload(self, file_chosen, chosen_fp):
        try:
            global chosen_filepath
            chosen_filepath = str(file_chosen.selection[0])

            chosen_fp.text = chosen_filepath
        except IndexError:
            self.popup = ErrorTitlePopup()
            self.popup.content = Label(text="Please select a file.")
            self.popup.size_hint = (None, None)
            self.popup.size = (175, 100)
            self.popup.open()


class AuditScreen(Screen):
    EventLoop.window.title = 'new title'

    def load_audit(self, anb, anlbl):
        global loaded_audit
        self.ids.anlbl.text = loaded_audit
        # Make welcome message utilizing username
        anlbl.color = (1, 1, 1, .9)
        anlbl.font_size = 20
        anlbl.bold = True
        anlbl.text = loaded_audit
        wel_width = len(anlbl.text) * 15
        wel_height = anlbl.height

        anb.width = wel_width
        anb.height = wel_height


########################################################################################################################
class AuditTrackerApp(App):

    def build(self):
        # Build app
        # Bind custom on_request_close method (popup prompt on close attempt)
        Window.bind(on_request_close=self.on_request_close)
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(NewAuditScreen(name='new_audit'))
        sm.add_widget(AuditScreen(name="audit"))
        sm.current = 'menu'
        # sm.current = 'new_audit'
        return sm

    def on_request_close(self, *args):
        self.popQuitProgram()
        return True

    def popQuitProgram(self):
        popup = QuitPopup()
        popup.open()


if __name__ == '__main__':
    AuditTrackerApp().run()
