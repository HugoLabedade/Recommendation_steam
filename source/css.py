import streamlit as st

def display_image_on_hover(i, genre, image_url, description, jeu):
    # Generate unique class names for each image
    hover_class = f'hoverable_{i}'
    tooltip_class = f'tooltip_{i}'
    image_popup_class = f'image-popup_{i}'

    # Define the unique CSS for each image
    hover_css = f'''
        .{hover_class} {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}
        .{hover_class} .{tooltip_class} {{
            opacity: 0;
            position: absolute;
            top: 50%;
            left: calc(100% + 10px);
            transform: translateY(-50%);
            transition: opacity 0.5s;
            background: linear-gradient(to top right, lightcyan, #7AB8E5);
            color: #555;
            padding: 4px;
            border-radius: 4px;
            text-align: center;
            white-space: pre-wrap;
            width: 700px;
        }}
        .{hover_class}:hover .{tooltip_class} {{
            opacity: 1;
        }}
        .{image_popup_class} {{
            position: absolute;
            display: none;
            background-image: none;
            width: 200px;
            height: 200px;
        }}
        .{hover_class}:hover .{image_popup_class} {{
            display: block;
            background-image: url({image_url});
            background-size: cover;
            z-index: 999;
        }}
    '''
    tooltip_css = f"<style>{hover_css}</style>"

    # Define the html for each image
    image_hover = f'''
        <div class="{hover_class}">
            <img src="{image_url}"></img>
            <div class="{tooltip_class}"><h4 style="color: #555;"><b>{jeu}</b></h4><h5 style="color: #555;"><b>Genre:</h5><p style="border-radius: 3px; color: white;background-color: bluegrey;display: inline-block;">{genre}</p><p><h5 style="color: #555;">Description:</h5><p>{description}</p>
            </div>
        </div>
    '''
    
    # Write the dynamic HTML and CSS to the content container
    st.markdown(f'<p>{image_hover}{tooltip_css}</p>', unsafe_allow_html=True)