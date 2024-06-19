import uno
import os
from com.sun.star.uno import Exception as UnoException
from com.sun.star.connection import NoConnectException
from threading import Thread
from controller import Supervisor

def connect_to_libreoffice(port=2002):
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    try:
        context = resolver.resolve(f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext")
        return context
    except NoConnectException:
        print("Couldn't connect to LibreOffice. Make sure that LibreOffice is running in listening mode.")
        return None

def get_sheet(doc, sheet_name):
    try:
        return doc.Sheets.getByName(sheet_name)
    except UnoException:
        print(f"The sheet with the name {sheet_name} not found.")
        return None

def update_cell(sheet, row, name, x, y, z):
    try:
        cell_name = sheet.getCellByPosition(0, row)
        cell_name.String = name
        
        cell_x = sheet.getCellByPosition(1, row)
        cell_x.Value = x
        
        cell_y = sheet.getCellByPosition(2, row)
        cell_y.Value = y
        
        cell_z = sheet.getCellByPosition(3, row)
        cell_z.Value = z
        
    except UnoException as e:
        print(f"Error updating the cell: {e}")

def update_table():
    global supervisor, doc, sheet
    while True:
        for i in range(children_field.getCount()):
            node = children_field.getMFNode(i)
            name_field = node.getField('name')
            if name_field:
                name_value = name_field.getSFString()
                if name_value in ["apple", "box", "wooden chair", "desk", "plastic fruit box"]:
                    translation_field = node.getField('translation')
                    translation = translation_field.getSFVec3f()
                    # We are looking for the corresponding row in the table and updating the values
                    found = False
                    for row in range(1, sheet.Rows.Count):  # We start with 1, since the 0 line is the headers
                        cell_name = sheet.getCellByPosition(0, row)
                        if cell_name.String == "":
                            update_cell(sheet, row, name_value, translation[0], translation[1], translation[2])
                            found = True
                            break
                        elif cell_name.String == name_value:
                            update_cell(sheet, row, name_value, translation[0], translation[1], translation[2])
                            found = True
                            break
                    # If the object is not found in the table, add a new row
                    if not found:
                        update_cell(sheet, sheet.Rows.Count, name_value, translation[0], translation[1], translation[2])
        
        try:
            doc.storeToURL(doc.URL, ())
        except UnoException as e:
            print(f"Error saving the document: {e}")

# Connecting to LibreOffice
context = connect_to_libreoffice()
if context is not None:
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    # Uploading a document
    file_path = os.path.join(os.getcwd(), "Сoordinates.ods")
    if os.path.exists(file_path):
        doc = desktop.loadComponentFromURL(f"file://{file_path}", "_blank", 0, ())
        if doc is not None:
            sheet = get_sheet(doc, "Coordinates")  # The name of the sheet you are using
            if sheet is not None:
                # Creating an instance of Supervisor
                supervisor = Supervisor()

                # Getting the root node of the scene
                root_node = supervisor.getRoot()

                # We get the child nodes of the root node
                children_field = root_node.getField('children')

                # We start updating the table in a separate thread
                thread = Thread(target=update_table)
                thread.daemon = True
                thread.start()

                # The main stimulation cycle
                while supervisor.step(32) != -1:  # Updating the simulation
                    pass  # Just waiting for the scene to update
    else:
        print("The table file was not found.")
else:
    print("Couldn't connect to LibreOffice.")
    
