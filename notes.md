


Bot flow
- First, send init message text that introduces the task.
    - write about issue
    - answer qs about values
    - get reappraisal


todo: enforce 1-3 emotions



bot can send different kinds of messages. messages sent from bot take the form of a dictionary with the following keys:
- message: the text of the message
- widget_type: the type of widget to display (e.g., text, select)
- widget_props: a dictionary with additional properties for the widget (e.g., options for a select widget)
- state: a string with the current state of the conversation 
    - solicit_issue
    - solicit_emotions
    - collect_reap_feedback

Widget properties:
- text: no additional properties
- slider: min, max, default, step
- multiselect: options (list of dicts with keys "val" and "label")


changes made for dockerization
- REACT_APP_FLASK_API_URL=http://localhost:8000  - dropped port
- dropped period to indicate relative imports for python packages.