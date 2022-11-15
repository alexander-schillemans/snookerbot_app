from jinja2 import Environment, FileSystemLoader, Template

def render_template(template_name, context):

    file_loader = FileSystemLoader('./templates')
    env = Environment(loader=file_loader)
    template = env.get_template(template_name)

    rendered_content = template.render(**context)
    
    return rendered_content