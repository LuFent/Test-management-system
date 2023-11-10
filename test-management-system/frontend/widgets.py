from django.forms.widgets import Input


class TextInput(Input):
    input_type = "text"
    template_name = "widgets/raw_input.html"
