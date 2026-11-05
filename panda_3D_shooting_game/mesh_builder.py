"""
mesh_builder.py - Procedural 3D Mesh Generator for Panda3D with UV texture mapping.
Supports cubes, cylinders, ramps, and custom UV coordinates for modern textured rendering.
"""

import math
from panda3d.core import (
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath, Vec3, Vec4, Texture
)

def make_cube(dx=1.0, dy=1.0, dz=1.0, color=Vec4(0.8, 0.8, 0.8, 1.0), uv_scale=(1.0, 1.0)):
    """Creates an axis-aligned box with normals, vertex colors, and UV coordinates."""
    vformat = GeomVertexFormat.get_v3n3c4t2()
    vdata = GeomVertexData('cube_data', vformat, Geom.UH_static)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    
    hx, hy, hz = dx * 0.5, dy * 0.5, dz * 0.5
    ux, uy = uv_scale[0], uv_scale[1]
    
    # 6 faces: Top (+Z), Bottom (-Z), Front (+Y), Back (-Y), Right (+X), Left (-X)
    faces = [
        # Top (+Z)
        ([(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)], (0, 0, 1), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
        # Bottom (-Z)
        ([(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (0, 0, -1), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
        # Front (+Y)
        ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (0, 1, 0), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
        # Back (-Y)
        ([(hx, -hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (hx, -hy, hz)], (0, -1, 0), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
        # Right (+X)
        ([(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)], (1, 0, 0), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
        # Left (-X)
        ([(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)], (-1, 0, 0), [(0, 0), (ux, 0), (ux, uy), (0, uy)]),
    ]
    
    tris = GeomTriangles(Geom.UH_static)
    idx = 0
    for verts, norm, uvs in faces:
        for v, uv in zip(verts, uvs):
            vertex.add_data3f(*v)
            normal.add_data3f(*norm)
            vcolor.add_data4f(color)
            texcoord.add_data2f(*uv)
        
        tris.add_vertices(idx, idx + 1, idx + 2)
        tris.add_vertices(idx, idx + 2, idx + 3)
        idx += 4
        
    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('cube_geom')
    node.add_geom(geom)
    return NodePath(node)

def make_cylinder(radius=0.5, height=1.0, segments=16, color=Vec4(0.7, 0.7, 0.7, 1.0)):
    """Creates a vertical cylinder along Z axis with UV mapping."""
    vformat = GeomVertexFormat.get_v3n3c4t2()
    vdata = GeomVertexData('cyl_data', vformat, Geom.UH_static)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    
    hz = height * 0.5
    tris = GeomTriangles(Geom.UH_static)
    
    # Side walls
    idx = 0
    for i in range(segments):
        u1 = i / segments
        u2 = (i + 1) / segments
        a1 = u1 * 2.0 * math.pi
        a2 = u2 * 2.0 * math.pi
        
        x1, y1 = radius * math.cos(a1), radius * math.sin(a1)
        x2, y2 = radius * math.cos(a2), radius * math.sin(a2)
        
        nx1, ny1 = math.cos(a1), math.sin(a1)
        nx2, ny2 = math.cos(a2), math.sin(a2)
        
        vertex.add_data3f(x1, y1, -hz); normal.add_data3f(nx1, ny1, 0); vcolor.add_data4f(color); texcoord.add_data2f(u1, 0)
        vertex.add_data3f(x2, y2, -hz); normal.add_data3f(nx2, ny2, 0); vcolor.add_data4f(color); texcoord.add_data2f(u2, 0)
        vertex.add_data3f(x2, y2, hz);  normal.add_data3f(nx2, ny2, 0); vcolor.add_data4f(color); texcoord.add_data2f(u2, 1)
        vertex.add_data3f(x1, y1, hz);  normal.add_data3f(nx1, ny1, 0); vcolor.add_data4f(color); texcoord.add_data2f(u1, 1)
        
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
        vertex.add_data3f(0, 0, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color); texcoord.add_data2f(0.5, 0.5)
        vertex.add_data3f(x1, y1, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color); texcoord.add_data2f(0.5 + 0.5*math.cos(a1), 0.5 + 0.5*math.sin(a1))
        vertex.add_data3f(x2, y2, hz); normal.add_data3f(0, 0, 1); vcolor.add_data4f(color); texcoord.add_data2f(0.5 + 0.5*math.cos(a2), 0.5 + 0.5*math.sin(a2))
        tris.add_vertices(idx, idx + 1, idx + 2)
        idx += 3
        
        # Bottom cap
        vertex.add_data3f(0, 0, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color); texcoord.add_data2f(0.5, 0.5)
        vertex.add_data3f(x2, y2, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color); texcoord.add_data2f(0.5 + 0.5*math.cos(a2), 0.5 + 0.5*math.sin(a2))
        vertex.add_data3f(x1, y1, -hz); normal.add_data3f(0, 0, -1); vcolor.add_data4f(color); texcoord.add_data2f(0.5 + 0.5*math.cos(a1), 0.5 + 0.5*math.sin(a1))
        tris.add_vertices(idx, idx + 1, idx + 2)
        idx += 3

    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('cyl_geom')
    node.add_geom(geom)
    return NodePath(node)

def make_ramp(dx=2.0, dy=4.0, dz=1.5, color=Vec4(0.5, 0.5, 0.55, 1.0)):
    """Creates a slope/ramp wedge along the Y axis with UV coordinates."""
    vformat = GeomVertexFormat.get_v3n3c4t2()
    vdata = GeomVertexData('ramp_data', vformat, Geom.UH_static)
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    vcolor = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    
    hx = dx * 0.5
    hy = dy * 0.5
    tris = GeomTriangles(Geom.UH_static)
    idx = 0
    
    faces = [
        ([(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)], (0, 0, -1)),
        ([(-hx, hy, 0), (hx, hy, 0), (hx, hy, dz), (-hx, hy, dz)], (0, 1, 0)),
        ([(-hx, -hy, 0), (-hx, hy, dz), (hx, hy, dz), (hx, -hy, 0)], (0, -dz/dy, dy/dy)),
    ]
    for verts, norm in faces:
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for v, uv in zip(verts, uvs):
            vertex.add_data3f(*v); normal.add_data3f(*norm); vcolor.add_data4f(color); texcoord.add_data2f(*uv)
        tris.add_vertices(idx, idx + 1, idx + 2)
        tris.add_vertices(idx, idx + 2, idx + 3)
        idx += 4
        
    # Left Triangle
    vertex.add_data3f(-hx, -hy, 0); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(0, 0)
    vertex.add_data3f(-hx, hy, 0); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(1, 0)
    vertex.add_data3f(-hx, hy, dz); normal.add_data3f(-1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(1, 1)
    tris.add_vertices(idx, idx + 1, idx + 2)
    idx += 3
    
    # Right Triangle
    vertex.add_data3f(hx, -hy, 0); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(0, 0)
    vertex.add_data3f(hx, hy, dz); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(1, 1)
    vertex.add_data3f(hx, hy, 0); normal.add_data3f(1, 0, 0); vcolor.add_data4f(color); texcoord.add_data2f(1, 0)
    tris.add_vertices(idx, idx + 1, idx + 2)
    idx += 3
    
    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('ramp_geom')
    node.add_geom(geom)
    return NodePath(node)
