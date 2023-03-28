#A 0.11

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableView, QMessageBox, QInputDialog, QFormLayout, QAbstractItemView
from mysql.connector import connect, Error
from random import randint

class Item:
    def __init__(self, id, name, quantity, description, location):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.description = description
        self.location = location

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the database connection
        self.db = connect(
            host="",
            user="",
            port="",
            password="",
            database="inventorypro"
        )

        # Set up the main window
        self.setWindowTitle('Inventory Management System')
        self.setGeometry(100, 100, 800, 600)

        # Set up the table view
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set up the add item form
        self.add_item_name_label = QLabel('Name:')
        self.add_item_name_input = QLineEdit()
        self.add_item_qty_label = QLabel('Quantity:')
        self.add_item_qty_input = QLineEdit()
        self.add_item_desc_label = QLabel('Description:')
        self.add_item_description_input = QLineEdit()
        self.add_item_loc_label = QLabel('Location:')
        self.add_item_loc_input = QLineEdit()
        self.add_item_button = QPushButton('Add Item')
        self.add_item_button.clicked.connect(self.add_item)

        # Set up the edit and delete buttons
        self.edit_item_button = QPushButton('Edit Item')
        self.edit_item_button.clicked.connect(self.edit_item)
        self.delete_item_button = QPushButton('Delete Item')
        self.delete_item_button.clicked.connect(self.delete_item)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_view)

        add_item_form = QFormLayout()
        add_item_form.addRow(self.add_item_name_label, self.add_item_name_input)
        add_item_form.addRow(self.add_item_qty_label, self.add_item_qty_input)
        add_item_form.addRow(self.add_item_desc_label, self.add_item_description_input)
        add_item_form.addRow(self.add_item_loc_label, self.add_item_loc_input)
        add_item_form.addRow(self.add_item_button)
        main_layout.addLayout(add_item_form)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_item_button)
        button_layout.addWidget(self.delete_item_button)
        main_layout.addLayout(button_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

                # Create the button
        add_items_button = QPushButton('Add 5000 Items')
        add_items_button.clicked.connect(self.add_5000_items)

        # Add the button to the layout
        main_layout.addWidget(add_items_button)

        # Load the initial items from the database
        self.load_items()

    def add_5000_items(app): #used to populate database for performance testing metrics (tested with 750,000 entries) .22 second load times @750k records
        for i in range(5000):
            name = f'Item {i+1}'
            qty = randint(1, 100)
            description = f'Description for item {i+1}'
            location = f'Location {i+1}'
            app.add_item(name=name, qty=qty, description=description, location=location)
        print('Items added successfully!')



    def edit_item(self):
        # Get the selected row from the table view
        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            return
        index = indexes[0]

        # Get the new data from the user
        item = self.items[index.row()]
        name, ok = QInputDialog.getText(self, 'Edit Item', 'New name:', QLineEdit.Normal, item.name)
        if not ok or not name:
            return
        description, ok = QInputDialog.getText(self, 'Edit Item', 'New description:', QLineEdit.Normal, item.description)
        if not ok:
            return
        qty_str, ok = QInputDialog.getText(self, 'Edit Item', 'New quantity:', QLineEdit.Normal, str(item.quantity))
        if not ok:
            return
        location, ok = QInputDialog.getText(self, 'Edit Item', 'New location:', QLineEdit.Normal, item.location)
        if not ok:
            return

        # Update the item in the database
        cursor = self.db.cursor()
        query = "UPDATE items SET name = %s, description = %s, quantity = %s, location = %s WHERE id = %s"
        values = (name, description, qty_str, location, item.id)
        cursor.execute(query, values)
        self.db.commit()

        # Update the item in the items list and table model
        item.name = name
        item.description = description
        item.quantity = int(qty_str)
        item.location = location
        self.table_model.setData(index.sibling(index.row(), 1), name)
        self.table_model.setData(index.sibling(index.row(), 2), description)
        self.table_model.setData(index.sibling(index.row(), 3), qty_str)
        self.table_model.setData(index.sibling(index.row(), 4), location)




    def load_items(self):
        # Clear the table model
        self.table_model.clear()

        # Add the table headers
        self.table_model.setHorizontalHeaderLabels(['ID', 'Name', 'Quantity', 'Description', 'Location'])

        # Check if 'location' column exists in the 'items' table
        cursor = self.db.cursor()
        query = "SHOW COLUMNS FROM items LIKE 'location'"
        cursor.execute(query)
        result = cursor.fetchone()
        if not result:
            # If 'location' column does not exist, add it to the 'items' table
            query = "ALTER TABLE items ADD COLUMN location VARCHAR(255)"
            cursor.execute(query)

        # Load the items from the database
        query = "SELECT * FROM items"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Add the items to the table model
        for row in rows:
            item = Item(*row)
            id_item = QStandardItem(str(item.id))
            name_item = QStandardItem(item.name)
            qty_item = QStandardItem(str(item.quantity))
            desc_item = QStandardItem(item.description)
            loc_item = QStandardItem(item.location)
            self.table_model.appendRow([id_item, name_item, qty_item, desc_item, loc_item])

        # Resize the table columns to fit the contents
        self.table_view.resizeColumnsToContents()



    def add_item(self, name, qty, description, location):
        if name and qty:
            try:
                qty = int(qty)
                if qty < 0:
                    raise ValueError
            except ValueError:
                error_dialog = QMessageBox(self)
                error_dialog.setWindowTitle('Error')
                error_dialog.setText('Quantity must be a positive integer')
                error_dialog.exec_()
                return

            cursor = self.db.cursor()
            # Check if 'description' and 'location' columns exist in the 'items' table
            query = "SHOW COLUMNS FROM items LIKE 'description'"
            cursor.execute(query)
            result = cursor.fetchone()
            if not result:
                # If 'description' column does not exist, add it to the 'items' table
                query = "ALTER TABLE items ADD COLUMN description VARCHAR(255)"
                cursor.execute(query)

            query = "SHOW COLUMNS FROM items LIKE 'location'"
            cursor.execute(query)
            result = cursor.fetchone()
            if not result:
                # If 'location' column does not exist, add it to the 'items' table
                query = "ALTER TABLE items ADD COLUMN location VARCHAR(255)"
                cursor.execute(query)

            # Insert the new item into the database
            query = "INSERT INTO items (name, quantity, description, location) VALUES (%s, %s, %s, %s)"
            values = (name, qty, description, location)
            cursor.execute(query, values)
            self.db.commit()
            self.load_items()
        else:
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle('Error')
            error_dialog.setText('Please enter a name and quantity')
            error_dialog.exec_()






    def search_items(self):
        search_text = self.search_input.text().strip()
        if search_text:
            cursor = self.db.cursor()
            query = "SELECT id, name, quantity FROM items WHERE name LIKE %s"
            values = ('%' + search_text + '%',)
            cursor.execute(query, values)
            self.table_model.removeRows(0, self.table_model.rowCount())
            for item in cursor:
                row = []
                for column in item:
                    cell = QStandardItem(str(column))
                    cell.setEditable(False)
                    row.append(cell)
                self.table_model.appendRow(row)

    def edit_item(self):
        # Get the selected row from the table view
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return
        index = indexes[0]

        # Get the item data from the table model
        model_index = self.table_view.model().index(index.row(), 0)
        item_id = self.table_view.model().data(model_index)

        # Get the new name, description, quantity, and location from the user
        name, ok = QInputDialog.getText(self, 'Edit Item', 'New name:', QLineEdit.Normal, index.sibling(index.row(), 1).data(Qt.DisplayRole))
        if not ok or not name:
            return
        description, ok = QInputDialog.getText(self, 'Edit Item', 'New description:', QLineEdit.Normal, index.sibling(index.row(), 3).data(Qt.DisplayRole))
        if not ok:
            return
        qty_str = index.sibling(index.row(), 2).data(Qt.DisplayRole)
        qty, ok = QInputDialog.getInt(self, 'Edit Item', 'New quantity:', value=int(qty_str))
        if not ok:
            return
        location, ok = QInputDialog.getText(self, 'Edit Item', 'New location:', QLineEdit.Normal, index.sibling(index.row(), 4).data(Qt.DisplayRole))
        if not ok:
            return

        # Update the item in the database
        cursor = self.db.cursor()
        query = "UPDATE items SET name = %s, description = %s, quantity = %s, location = %s WHERE id = %s"
        values = (name, description, qty, location, item_id)
        cursor.execute(query, values)
        self.db.commit()

        # Update the table model
        self.table_model.setData(index.sibling(index.row(), 1), name)
        self.table_model.setData(index.sibling(index.row(), 3), description)
        self.table_model.setData(index.sibling(index.row(), 2), qty)
        self.table_model.setData(index.sibling(index.row(), 4), location)



    def delete_item(self):
        # Get the selected row from the table view
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return
        index = indexes[0]

        # Get the item ID from the table model
        item_id = self.table_model.item(index.row(), 0).text()

        # Ask the user to confirm the delete operation
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle('Confirm Delete')
        confirm_dialog.setText(f'Are you sure you want to delete item {item_id}?')
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        confirm_dialog.setDefaultButton(QMessageBox.Cancel)
        result = confirm_dialog.exec_()
        if result == QMessageBox.Cancel:
            return

        # Delete the item from the database
        cursor = self.db.cursor()
        query = "DELETE FROM items WHERE id = %s"
        cursor.execute(query, (item_id,))
        self.db.commit()

        # Reload the items in the table
        self.load_items()




if __name__ == '__main__':
    app = QApplication([])
    inventory_app = InventoryApp()
    inventory_app.show()
    app.exec_()
