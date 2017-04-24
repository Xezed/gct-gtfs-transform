from math import radians, cos, sin, asin, sqrt
import xml.etree.ElementTree as ET
import csv
import os
import re
import sqlite3
import sys


try:
    shape = sys.argv[1]
except:
    shape = False


def main(shape):
    if shape:
        with open(shape, 'rb') as f:
            input_set = set()
            input_shape = csv.reader(f, delimiter=',')
            for sh in input_shape:
                input_set.add(sh[0])

    with open('shapes.txt', 'wb') as csvfile:
        existed_set = set()
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(["shape_id", "shape_pt_sequence", "shape_dist_traveled", "shape_pt_lat", "shape_pt_lon"])
        routes = {}
        for dir_root, dirs, files in os.walk('KMLs'):
            files = [f for f in files if f.endswith('.kml')]
            for route in files:
                tree = ET.parse(os.path.join(dir_root, route))
                root = tree.getroot()
                routes[route] = get_coordinates(root, dir_root, route)

                count = sum(1 for x in routes[route] for y in x[1].split())
                i = 0

                for r in routes[route]:
                    reader = csv.reader(r[1].split(), delimiter=',')
                    route_id = r[0]
                    if shape:
                        existed_set.add(route_id)
                    for row in reader:
                        spamwriter.writerow([route_id, str(i), '', row[1], row[0]])
                        i += 1

    with open('shapes.txt', 'rb') as f:
        with open('new_shapes.txt', 'wb') as n:
            writer = csv.writer(n)
            old = csv.reader(f, delimiter=',')
            old_shape_dist_traveled = float()

            for i, row in enumerate(old):
                if i == 0:
                    writer.writerow(row)
                elif i == 1:
                    lat1 = row[3]
                    lon1 = row[4]
                    id1 = row[0]
                    writer.writerow([row[0], row[1], 0, row[3], row[4]])
                else:
                    lat2 = row[3]
                    lon2 = row[4]
                    id2 = row[0]

                    shape_dist_traveled = haversine(lon1, lat1, lon2, lat2)
                    if id1 != id2:
                        lat1 = lat2
                        lon1 = lon2
                        id1 = id2
                        old_shape_dist_traveled = 0
                        writer.writerow([row[0], row[1], 0, row[3], row[4]])
                        continue
                    id1 = id2
                    shape_dist_traveled += old_shape_dist_traveled

                    old_shape_dist_traveled = shape_dist_traveled
                    writer.writerow([row[0], row[1], shape_dist_traveled, row[3], row[4]])
                    lat1 = lat2
                    lon1 = lon2
        os.rename('new_shapes.txt', 'shapes.txt')

    with open('shapes.txt', 'rb') as f:
        with open('new_shapes', 'wb') as nf:
            writer = csv.writer(nf)
            old = csv.reader(f, delimiter=',')
            con1 = sqlite3.connect('1.db')
            c1 = con1.cursor()
            con2 = sqlite3.connect('2.db')
            c2 = con2.cursor()

            haversine1 = float(0)

            for i, row in enumerate(old):
                if i is 0:
                    writer.writerow(row)
                    continue
                if i is 1:
                    id1 = row[0]
                id2 = row[0]
                haversine2 = float(row[2])

                if id2 == id1:
                    haversine1 = haversine2
                    id1 = id2
                    continue
                if id1.startswith('T'):
                    t = (id1[2:5] + '%',)
                    c1.execute('SELECT max(abscisa) FROM routes WHERE ruta LIKE ?', t)
                    abscisa = c1.fetchone()[0]

                else:
                    t = id1.split('-')[1:]
                    abscisa = int()
                    c2.execute('SELECT max(abscisa) FROM routes WHERE linea LIKE ? AND ruta LIKE ?', t)
                    abscisa = c2.fetchone()[0]
                print abscisa, haversine1
                coef = abscisa / (haversine1*1000)
                with open('shapes.txt', 'rb') as o:
                    new = csv.reader(o, delimiter=',')
                    for new_row in new:
                        if id1 == new_row[0]:
                            shape_dist_traveled = float(new_row[2]) * coef * 1000
                            writer.writerow([new_row[0], new_row[1], int(shape_dist_traveled), new_row[3], new_row[4]])
                    haversine1 = 0
                    id1 = id2
        c1.close()
        con1.close()
        c2.close()
        con2.close()
        os.rename('new_shapes', 'shapes.txt')

    if shape:
        with open('shapes.txt', 'rb') as e:
            with open(shape, 'rb') as i:
                with open('new_shapes.txt', 'wb') as n:
                    writer = csv.writer(n)
                    inp = csv.reader(i, delimiter=',')
                    ex = csv.reader(e, delimiter=',')

                    for sh in ex:
                        if sh[0] not in input_set:
                            writer.writerow(sh)
                    for sh in inp:
                        if sh[0] in existed_set:
                            writer.writerow(sh)
        os.rename('new_shapes.txt', 'shapes.txt')


def get_coordinates(root, dir_root, route):
    coords = []
    for coordinates in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        for name in coordinates.findall('{http://www.opengis.net/kml/2.2}name'):
            for coordinate in coordinates.findall('.//{http://www.opengis.net/kml/2.2}coordinates'):
                if dir_root.endswith('Troncal'):
                    coords.append(('T' + '-' + name.text[:3], coordinate.text))
                else:
                    dir_id = re.findall(r'/([A-Z])', dir_root)[0]
                    route_id = re.findall(r'_(\d+)\.', route)[0]
                    name_id = re.findall(r'_(\d+)$', name.text)[0]
                    coord_id = dir_id + '-' + route_id + '-' + name_id
                    coords.append((coord_id, coordinate.text))
    return coords


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

if __name__ == '__main__':
    main(shape)