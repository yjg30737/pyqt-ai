from qtpy.QtWidgets import QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox


def get_form_layout(attributes_list):
    lay = QFormLayout()
    for i in range(len(attributes_list)):
        name = attributes_list[i]['name']
        value = attributes_list[i]['default']
        selection = attributes_list[i].get('selection', [])
        widget = get_proper_widget_by_type(name, value, selection)
        lay.addRow(name, widget)
        # widget.textChanged.connect(self.__setAccept)
        attributes_list[i]['widget'] = widget
    return lay, attributes_list

def get_proper_widget_by_type(name, value, selection):
    # If selecction is not empty
    if selection:
        print('selection:', selection)
        widget = QComboBox()
        widget.addItems(selection)
    else:
        # If the field is string
        if isinstance(value, str):
            widget = QLineEdit(value)
        # If the field is integer
        elif isinstance(value, int):
            widget = QSpinBox(value)
        # If the field is float
        elif isinstance(value, float):
            widget = QDoubleSpinBox(value)
        # If the field is boolean
        elif isinstance(value, bool):
            widget = QCheckBox(value)
        # If the field is list
        elif isinstance(value, list):
            groupBox = QGroupBox()
            groupBox.setTitle(name)
            # Loop through the value's instance and recursively call the function
            for i in range(len(value)):
                get_proper_widget_by_type(value[i], [])

    return widget