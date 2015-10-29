#!/usr/bin/env python

"""Utility classes to create paper microplates. Require Python >= 3.3"""

import os
import copy
import shutil
import svgwrite

class PaperPlate:
    """General paper microplate.

    Properties
    ----------
    svg : svgwrite.Drawing
        An SVG representation of the paper plate.

    """

    def __init__(self, n_rows, n_cols, plate_length, plate_width,
                 barrier_thickness, well_diameter, well_separation,
                 margin, left_padding, top_padding,
                 edge_corner_radius, edge_thickness, edges_distance,
                 label_font_size, well_fill):
        """Create the representation of a paper plate.

        Parameters
        ----------
        n_rows: int
            The number of wells per plate row.
        n_cols: int
            The number of wells per plate column.
        plate_length: float
            The length of the whole plate in mm in the direction parallel to rows.
        plate_width: float
            The length in mm of the whole plate in the direction parallel to columns.
        barrier_thickness: float
            The thickness in mm of the line for the well barriers.
        well_diameter: float
            The diameter in mm of the well not considering the barrier thickness.
        well_separation: float
            The distance in mm between the centers of two wells.
        margin: float
            The distance in mm between the outer borders and the end of the figure.
        left_padding: float
            The distance in mm between the left outer edge and the center of the
            first column of wells.
        top_padding: float
            The distance in mm between the top outer edge and the center of the
            first row of wells.
        edge_corner_radius: float
            Radius in mm of the outer edge corner curvature.
        edge_thickness: float
            Thickness in mm of the line drawn for the inner and outer edges.
        edges_distance: float
            Distance in mm between the two borders
        label_font_size: float
            Font size of the letters and numbers identifying columns.
        well_fill: str or iterable of str
            Specify a single color as a string compatible with the SVG fill attribute
            or a matrix of n_rows by n_cols strings describing a color for each well.

        """

        self._n_rows = n_rows
        self._n_cols = n_cols
        self._plate_length = plate_length
        self._plate_width = plate_width
        self._barrier_thickness = barrier_thickness
        self._well_diameter = well_diameter
        self._well_separation = well_separation
        self._margin = margin
        self._edge_corner_radius = edge_corner_radius
        self._edge_thickness = edge_thickness
        self._edges_distance = edges_distance
        self._label_font_size = label_font_size

        if isinstance(well_fill, str):
            self._fill_matrix = [[well_fill for i in range(n_cols)] for j in range(n_rows)]
        else:
            self._fill_matrix = copy.deepcopy(well_fill)

        # Coordinates of the top left well center
        self._top_y = margin + top_padding
        self._left_x = margin + left_padding

        # Create SVG figure
        viewport_size = (plate_length + 2 * margin, plate_width + 2 * margin)
        viewport_dim = (str(viewport_size[0]) + 'mm', str(viewport_size[1]) + 'mm')
        self._svg = svgwrite.Drawing(filename='paper-plate.svg', size=viewport_dim)

        # Modify ViewBox so that each user unit is equal to 1mm
        # http://sarasoueidan.com/blog/svg-coordinate-systems/
        # http://stackoverflow.com/questions/13006601/setting-default-units-in-svg-python-svgwrite
        self._svg.viewbox(width=viewport_size[0], height=viewport_size[1])

        # Draw plate
        self._draw_edges()
        self._draw_wells()
        self._draw_labels()

    @property
    def svg(self):
        return self._svg

    def _draw_edges(self):
        """Draw the inner and outer edges."""
        fill='white'
        stroke='black'

        # Outer edge
        self._svg.add(self._svg.rect(insert=(self._margin, self._margin),
                                     size=(self._plate_length, self._plate_width),
                                     rx=self._edge_corner_radius,
                                     stroke_width = self._edge_thickness,
                                     stroke=stroke,
                                     fill=fill))

        # Inner edge
        insert_coord = self._margin + self._edges_distance
        inner_size = (self._plate_length - 2 * self._edges_distance,
                      self._plate_width - 2 * self._edges_distance)
        self._svg.add(self._svg.rect(insert=(insert_coord, insert_coord),
                                     size=inner_size,
                                     stroke_width=self._edge_thickness,
                                     rx=self._edge_corner_radius - self._edges_distance,
                                     stroke=stroke,
                                     fill=fill))

    def _draw_wells(self):
        """Draw the wells on the plate."""
        stroke='black'

        # Draw wells
        for row in range(self._n_rows):
            for col in range(self._n_cols):
                self._svg.add(self._svg.circle(center=(self._left_x + col * self._well_separation,
                                                       self._top_y + row * self._well_separation),
                                               r=self._well_diameter / 2.0,
                                               stroke_width=self._barrier_thickness,
                                               stroke=stroke,
                                               fill=self._fill_matrix[row][col]))

    def _draw_labels(self):
        """Draw letters and numbers to identify respectively rows and columns."""
        font_size = self._label_font_size
        for row in range(self._n_rows):
            self._svg.add(self._svg.text(text=chr(row + 65),
                                         insert=(-0.75 * self._well_separation + self._left_x,
                                                row * self._well_separation + self._top_y + font_size / 8.0),
                                         text_anchor='middle',
                                         font_size=font_size,
                                         alignment_baseline='middle',
                                         font_family='Futura'
                                         ))

        for col in range(self._n_cols):
            self._svg.add(self._svg.text(text=str(col + 1),
                                         insert=(col * self._well_separation + self._left_x,
                                                 -0.55 * self._well_separation + self._top_y - font_size / 8.0),
                                         text_anchor='middle',
                                         font_size=font_size,
                                         alignment_baseline='middle',
                                         font_family='Futura'
                                         ))

    def to_pdf_inkscape(self, pdf_file_path):
        """Save the paper plate in SVG and convert it to pdf with Inkscape."""

        # Make directory
        file_dir = os.path.dirname(os.path.abspath(pdf_file_path))
        os.makedirs(file_dir, exist_ok=True)

        # Save SVG
        file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
        svg_path = os.path.join(file_dir, file_name + '.svg')
        self._svg.saveas(svg_path)

        # Find Inkscape
        if shutil.which('inkscape') is None:
            inkscape_path = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
        else:
            inkscape_path = 'inkscape'

        pdf_path = os.path.abspath(pdf_file_path)
        os.system(inkscape_path + ' -f ' + svg_path + ' -A ' + pdf_path)


class Plate96(PaperPlate):
    """A 96 well paper microplate following standards ANSI/SLAS 4-2004 and ANSI/SBS 1-2004."""

    def __init__(self, barrier_tickness, well_diameter, margin,
                 edge_thickness=0.75, edge_distance=1.0, well_fill='white'):
        super().__init__(n_rows=8,
                         n_cols=12,
                         plate_length=127.76,
                         plate_width=85.48,
                         barrier_thickness=barrier_tickness,
                         well_diameter=well_diameter,
                         well_separation=9,
                         margin=margin,
                         left_padding=14.38,
                         top_padding=11.24,
                         edge_corner_radius=3.18,
                         edge_thickness=edge_thickness,
                         edges_distance=edge_distance,
                         label_font_size=4,
                         well_fill=well_fill)

class Plate384(PaperPlate):
    """A 384 well paper microplate following standards ANSI/SLAS 4-2004 and ANSI/SBS 1-2004."""

    def __init__(self, barrier_tickness, well_diameter, margin,
                 edge_thickness=0.75, edge_distance=1.0, well_fill='white'):
        super().__init__(n_rows=16,
                         n_cols=24,
                         plate_length=127.76,
                         plate_width=85.48,
                         barrier_thickness=barrier_tickness,
                         well_diameter=well_diameter,
                         well_separation=4.5,
                         margin=margin,
                         left_padding=12.7,
                         top_padding=8.99,
                         edge_corner_radius=3.18,
                         edge_thickness=edge_thickness,
                         edges_distance=edge_distance,
                         label_font_size=3,
                         well_fill=well_fill)

