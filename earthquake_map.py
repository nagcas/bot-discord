import csv
import folium

def plotting():
  filename = "earthquake_data.csv"
  keys = ('Location', 'Time (UTC)', 'Latitude', 'Longitude', 'Magnitude', 'Depth (km)')
  records = []

  # read the data from the CSV file earthquake
  with open(filename, 'r') as csv_earthquakes:
    reader = csv.DictReader(csv_earthquakes)
    for row in reader:
      #print(row)
      #break
      records.append({ key: row[key] for key in keys })

  print(records[0])


  map = folium.Map(location = [43.00, 12.00], zoom_start = 5)

  for record in records:
    coords = (record['Latitude'], record['Longitude'])
    content = f"""
      {record['Location']} <br>
      Time: {record['Time (UTC)']} <br> 
      Magnitude: {record['Magnitude']} <br> 
      Depth (km): {record['Depth (km)']}"""
    print(content)
    
    if (float(record['Magnitude']) >= 5):
      color_marker = 'red'
    else:
      color_marker = 'blue'
    
    folium.CircleMarker(
        coords,
        radius = float(record['Magnitude']) * 2,
        color = color_marker,
        fill = True,
        fill_color = color_marker,
        popup = folium.Popup(content, max_width = 400)
    ).add_to(map)

  map