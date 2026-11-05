"""
mesh_builder.py - Procedural 3D Mesh Generator for Panda3D.
Generates textured and vertex-colored meshes (cubes, cylinders, spheres, wedges, quads)
without requiring any external .egg or .bam files.
"""

import math
from panda3d.core import (
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath, Vec3, Vec4
)

def make_cube(dx=1.0, dy=1.0, dz=1.0, color=Vec4(0.8, 0.8, 0.8, 1.0)):
    """Creates an axis-aligned box centered at origin."""
    vformat = GeomVertexFormat.get_v3n3c4()
    vdata = GeomVertexData('cube_data', vformat, Geom.UH_static)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    
    hx, hy, hz = dx * 0.5, dy * 0.5, dz * 0.5
    
    # 6 faces: +Z, -Z, +Y, -Y, +X, -X
    faces = [
        # Top (+Z)
        ([(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)], (0, 0, 1)),
        # Bottom (-Z)
        ([(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (0, 0, -1)),
        # Front (+Y)
        ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (0, 1, 0)),
        # Back (-Y)
        ([(hx, -hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (hx, -hy, hz)], (0, -1, 0)),
        # Right (+X)
        ([(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)], (1, 0, 0)),
        # Left (-X)
        ([(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)], (-1, 0, 0)),
    ]
    
    tris = GeomTriangles(Geom.UH_static)
    idx = 0
    for verts, norm in faces:
        for v in verts:
            vertex.add_data3f(*v)
            normal.add_data3f(*norm)
            vcolor.add_data4f(color)
        
        tris.add_vertices(idx, idx + 1, idx + 2)
        tris.add_vertices(idx, idx + 2, idx + 3)
        idx += 4
        
    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('cube_geom')
    node.add_geom(geom)
    return NodePath(node)

def make_cylinder(radius=0.5, height=1.0, segments=12, color=Vec4(0.7, 0.7, 0.7, 1.0)):
    """Creates a vertical cylinder along Z axis centered at origin."""
    vformat = GeomVertexFormat.get_v3n3c4()
    vdata = GeomVertexData('cyl_data', vformat, Geom.UH_static)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    
    hz = height * 0.5
    tris = GeomTriangles(Geom.UH_static)
    
    # Side walls
    idx = 0
    for i in range(segments):
        a1 = (i / segments) * 2.0 * math.pi
        a2 = ((i + 1) / segments) * 2.0 * math.pi
        
        x1, y1 = radius * math.cos(a1), radius * math.sin(a1)
        x2, y2 = radius * math.cos(a2), radius * math.sin(a2)
        
        nx1, ny1 = math.cos(a1), math.sin(a1)
        nx2, ny2 = math.cos(a2), math.sin(a2)
        
        # 4 vertices per quad
        vertex.add_data3f(x1, y1, -hz); normal.add_data3f(nx1, ny1, 0); vcolor.add_data4f(color)
        vertex.add_data3f(x2, y2, -hz); normal.add_data3f(nx2, ny2, 0); vcolor.add_data4f(color)
        vertex.add_data3f(x2, y2, hz);  normal.add_data3f(nx2, ny2, 0); vcolor.add_data4f(color)
        vertex.add_data3f(x1, y1, hz);  normal.add_data3f(nx1, ny1, 0); vcolor.add_data4f(color)
        
        tris.add_vertices(idx, idx + 1, idx + 2)
        tris.add_vertices(idx, idx + 2, idx + 3)
        idx += 4
        
    # Top & bottom caps
    for i in range(segments):
        a1 = (i / segments) * 2.0 * math.pi
        a2 = ((i + 1) / segments) * 2.0 * math.pi
        x1, y1 = radius * math.cos(a1), radius * math.sin(a1)
        x2, y2 = radius * math.cos(a2), radius * math.sin(a2)
        
        # Top cap
        vertex.add_data3f(0, 0, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color)
        vertex.add_data3f(x1, y1, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color)
        vertex.add_data3f(x2, y2, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color)
        tris.add_vertices(idx, idx + 1, idx + 2)
        idx += 3
        
        # Bottom cap
        vertex.add_data3f(0, 0, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color)
        vertex.add_data3f(x2, y2, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color)
        vertex.add_data3f(x1, y1, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color)
        tris.add_vertices(idx, idx + 1, idx + 2)
        idx += 3

    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('cyl_geom')
    node.add_geom(geom)
    return NodePath(node)

def make_ramp(dx=2.0, dy=4.0, dz=1.5, color=Vec4(0.5, 0.5, 0.55, 1.0)):
    """Creates a slope/ramp wedge along the Y axis."""
    vformat = GeomVertexFormat.get_v3n3c4()
    vdata = GeomVertexData('ramp_data', vformat, Geom.UH_static)
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    
    hx = dx * 0.5
    hy = dy * 0.5
    
    # 5 faces: bottom, back (+Y), slope, left (-X), right (+X)
    # Bottom: (-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)
    # Back: (-hx, hy, 0), (hx, hy, 0), (hx, hy, dz), (-hx, hy, dz)
    # Slope: (-hx, -hy, 0), (-hx, hy, dz), (hx, hy, dz), (hx, -hy, 0)
    tris = GeomTriangles(Geom.UH_static)
    idx = 0
    
    faces = [
        ([(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)], (0, 0, -1)),
        ([(-hx, hy, 0), (hx, hy, 0), (hx, hy, dz), (-hx, hy, dz)], (0, 1, 0)),
        ([(-hx, -hy, 0), (-hx, hy, dz), (hx, hy, dz), (hx, -hy, 0)], (0, -dz/dy, dy/dy)),
    ]
    for verts, norm in faces:
        for v in verts:
            vertex.add_data3f(*v); normal.add_data3f(*norm); vcolor.add_data4f(color)
        tris.add_vertices(idx, idx + 1, idx + 2)
        tris.add_vertices(idx, idx + 2, idx + 3)
        idx += 4
        
    # Side triangles
    # Left
    vertex.add_data3f(-hx, -hy, 0); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color)
    vertex.add_data3f(-hx, hy, 0); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color)
    vertex.add_data3f(-hx, hy, dz); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color)
    tris.add_vertices(idx, idx + 1, idx + 2)
    idx += 3
    
    # Right
    vertex.add_data3f(hx, -hy, 0); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color)
    vertex.add_data3f(hx, hy, dz); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color)
    vertex.add_data3f(hx, hy, 0); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color)
    tris.add_vertices(idx, idx + 1, idx + 2)
    idx += 3
    
    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('ramp_geom')
    node.add_geom(geom)
    return NodePath(node)
