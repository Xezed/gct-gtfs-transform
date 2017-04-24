Instructions:

Modify this python tool:

	https://github.com/atlregional/gct-gtfs-transform

to accomplish three things:

1. Construct the shape_id with the directory in which the KML is found, an ID found in the KML's filename, and another ID found on the path object contained in the KML.

For KMLs found in the ‘Troncal’ folder:

	The shape_id should be a concatenation of the first letter of the directory (T) and the 3-digit code at the beginning of the path object name.

	Ex. The shape H54 - P. USME_179 in file 1_110.kml.kml should have the shape_id T—H54

For KMLs found in other folders:

	The shape_id should be a concatenation of the first letter of the directory in which the KML was found, the number in the filename, and the last number in the path object.

	Ex. The shape Z7F-1_20170306_2703 from file 0_395.kml.kml should have the shape_id U—395—2703
24485
2. Calculate the field shape_dist_traveled using the path’s geometry and scaling the values so that the max value equals the max distance of the corresponding route in the ‘matriz de distancia’ provided.

For KMLs found in the ‘Troncal’ folder:

	The total length is the max value of ‘Abscisa’ for the corresponding route in the file Matriz Distancia SAE1

For other KMLs:
	
	The total length is the max value of ‘Posicion’ for the corresponding route (identified by the ruta and linea codes extracted from the filename and path object name) in the file Matriz Distancia SAE2

3. Input an existing shapes.txt file, automatically delete shapes that do not have corresponding KML's in the directory, and add shapes from KMLs in the directory that do not have corresponding shapes in the original file.

