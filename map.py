from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import folium
import base64
import sys


def get_decimal_coord(gps_info):
    def convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    
    lat = convert_to_degrees(gps_info['GPSLatitude'])
    if gps_info['GPSLatitudeRef'] == 'S':
        lat = -lat

    lon = convert_to_degrees(gps_info['GPSLongitude'])
    if gps_info['GPSLongitudeRef'] == 'W':
        lon = -lon

    return lat, lon

def get_coordinates(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()

    gps_info = {}

    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag)
            if tag_name == 'GPSInfo':
                for key in value:
                    gps_tag = GPSTAGS.get(key)
                    gps_info[gps_tag] = value[key]
                if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                    return get_decimal_coord(gps_info)
    
    return None

def create_map(args):
    image_location = []

    for filename in os.listdir(args):
        if filename.lower().endswith(('jpg', 'jpeg', 'png')):
            file_path = os.path.join(args, filename)
            coordinates = get_coordinates(file_path)

            if coordinates:
                image_location.append((coordinates, filename))
    

    if len(image_location) > 0:
        m = folium.Map(location=image_location[0][0], zoom_start=15)

       
        for location, filename in image_location:
           
            encoded_image = base64.b64encode(open(os.path.join(args, filename), 'rb').read()).decode()
            html = f"<b>{filename}</b><br><img src='data:image/jpeg;base64,{encoded_image}' width='200'>"

          
            folium.Marker(
                location=location,
                tooltip=filename,
                popup=folium.Popup(html, max_width=250)
            ).add_to(m)

      
        m.save("map.html")
        print("Map saved as map.html")
    else:
        print("No valid GPS data found in any of the images.")


if __name__ == "__main__":
    create_map(sys.argv[1])
