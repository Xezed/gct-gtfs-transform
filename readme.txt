1. You must install package for read from excel file:
	python -m pip install openpyxl
2. Run script kml2shape from the root of your files:
	python kml2shape.py

	It will generate two SQLite DBs from your excel files.

3. Run script kml3shape.py:

	python kml3shape.py	

	It will actually generate shapes.txt file for you.
	Optionally you can insert optional existing file with your shapes, for example:

	python kml3shape.py my_shapes.txt