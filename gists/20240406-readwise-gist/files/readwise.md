## File Name
```{{title|replace(""","")|replace(""","")|replace("'","")|replace("'","")|truncate(127)}}```

---
## Page Title
```# {{ title }}```
## Page Metadata
```
{% if image_url -%}
![300]({{image_url}})
{% endif -%}

# Metadata
- Author: {% if author %}[[{{author}}]]{% endif %}
- Imported: [[{{date|date('F j, Y')}}]]
- Real Title: {{full_title}}
{% if document_tags -%}
- Document Tags: {% for tag in document_tags %} #{{tag}} {% endfor %}
{% endif -%}
{% if url -%}
- [Link]({{url}})
{% endif -%}
```
## Highlights header
```
{% if is_new_page %}
# Notes
## Highlights
{% elif has_new_highlights -%}
## New highlights added [[{{date|date('F m, Y')}}]]
{% endif -%}
```
## Highlight
```
> {{ highlight_text }}
{% if highlight_tags %}- Tags: {% for tag in highlight_tags %}#{{tag}}{% endfor %}{% endif %}
{% if highlight_note %}- **Note**: {{ highlight_note }}{% endif %}
{% if highlight_location and highlight_location_url %} * _[{{highlight_location}}]({{highlight_location_url}})_{% elif highlight_location %}_({{highlight_location}})_{% endif %}
```
## YAML front matter
```
tag: 
    - content/{{category}}
    - readwise
started-on: <%tp.date.now("YYYY-MM-DD")%>
finished-on: {% if has_new_highlights %}{{last_highlighted_date|date('F m, Y')}}{% endif %}
```

