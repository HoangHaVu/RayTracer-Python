'''
Created on 17.04.2018

@author: Hoang Ha Vu
'''

import math
import PIL.Image


class Scene:

    def __init__(self, camera, objectList, lights):
        self.camera = camera
        self.objectList = objectList
        self.lights = lights
        self.width = self.camera.width
        self.height = self.camera.height
        self.backgroundColor = Color(0, 0, 0)
        self.image = PIL.Image.new(
            "RGB", (self.width, self.height), 0)

    def render(self):

        for x in range(self.width):
            for y in range(self.height):
                ray = camera.build_ray(x, y)
                color = self.shootRay(ray)
                self.image.putpixel(
                    (self.width - x - 1, self.height - y - 1), (int(color.x), int(color.y), int(color.z)))

        return self.image

    def shootRay(self, ray, reflexionDepth=0, maxReflexionDepth=2):

        color = Color()

        if reflexionDepth >= maxReflexionDepth:
            return color

        intersection = self.checkIntersection(ray)
        if intersection is None:
            return color

        obj, hitdist = intersection

        # calculateColor at IntersectionPoint
        intersectionPoint = ray.pointAtParameter(hitdist)
        surfaceNormVector = obj.normalAt(
            intersectionPoint)

        materialColor = obj.material.colorAt(intersectionPoint)

        # Ambient light
        color += materialColor * obj.material.ambient

        for light in self.lights:
            vecPointToLight = (light - intersectionPoint).normalize()
            rayPointToLight = Ray( intersectionPoint, vecPointToLight)

            # Shading of objects
            if self.checkIntersection(rayPointToLight) is None:
                shadingIntensity = surfaceNormVector.dot(
                    vecPointToLight)
                if shadingIntensity > 0:
                    color += materialColor * shadingIntensity

        reflectedRay = Ray(intersectionPoint, ray.direction.reflection(
            surfaceNormVector).normalize())

        color += self.shootRay(reflectedRay, reflexionDepth +
                               1) * obj.material.specular
        return color

    def checkIntersection(self, ray):
        intersection = None
        for obj in self.objectList:
            hitDist = obj.intersectionParameter(ray)
            if hitDist is not None and (intersection is None) and hitDist > 0:
                intersection = obj, hitDist
        return intersection


class Camera:

    def __init__(self, e, up, c, fieldOfView):

        self.e = e
        self.up = up
        self.c = c
        self.fieldOfView = fieldOfView

        self.f = (c - e).normalize()
        self.s = self.f.cross(up).normalize()
        self.u = self.s.cross(self.f)

    def setScreenSize(self, width, height):
        self.width = width
        self.height = height

        ratio = width / float(height)
        alpha = self.fieldOfView / 2.0
        self.halfHeight = math.tan(alpha)
        self.halfWidth = ratio * self.halfHeight
        self.pixelWidth = self.halfWidth / (width - 1) * 2
        self.pixelHeight = self.halfHeight / (height - 1) * 2

    def build_ray(self, x, y):
        xComp = self.s.scale(x * self.pixelWidth - self.halfWidth)
        yComp = self.u.scale(y * self.pixelHeight - self.halfHeight)
        return Ray(self.e, self.f + xComp + yComp)


class Vector:

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def norm(self):
        return math.sqrt(sum(num * num for num in self))

    def normalize(self):
        return self / self.norm()

    def reflect(self, other):
        other = other.normalize()
        return self - 2 * (self * other) * other

    def __repr__(self):
        return "Vector({}, {}, {})".format(*self)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Vector(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    def scale(self, factor):
        return self * factor

    def reflection(self, other):
        other = other.normalize()
        return self - 2 * (self.dot(other)) * other

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

# Punkt als Instanz eines Vektors definieren


Point = Vector
Color = Vector


class Material(object):
    """
    @param color: Die Basis-Farbe
    @param ambient: ambienter Anteil der Beleuchtung ( auch im Schatten )
    @param specular: spekulare Anteil der Beleuchtung ( Highlights ) 
    """
    def __init__(self, color):
        self.color = color
        self.ambient = 0.2
        self.specular = 0.5
    
    
   
    def colorAt(self, p):
        """
        @return: Farbe von der Oberflaeche an Punkt P
        """  
        return self.color


class CheckedMaterial(object):

    """
    Schachbrett Muster
    @param baseColor: Basis Farbe weiss
    @param otherColor:andere Farbe schwarz
    @param ambient: ambiente Antteil der Beleuchtung
    @param specular: spekulare Anteil der Beleuchtung
    @param checkSize: Groesse des Feld 
    """
    def __init__(self):
        self.baseColor = Color(200, 200, 200)
        self.otherColor = Color(0, 0, 0)
        self.ambient = 0.2
        self.specular = 0.5
        self.checkSize = 1

    def colorAt(self, p):
        """
        @return: gibt die Farbe weiss oder schwarz zurueck
        """
        p.scale(1.0 / self.checkSize)
        if (int(abs(p.x) + 0.5) + int(abs(p.y) + 0.5) + int(abs(p.z) + 0.5)) % 2:
            return self.otherColor
        return self.baseColor


class Ray(object):
    """
    @param origin: Ausgangspunkt des Strahls (Ortsvektor)
    @param direction: Richtung des Strahls (Richtungsvektor)
    """

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()

    def __repr__(self):
        """
        Default Konstruktor
        """
        return 'Ray(%s,%s)' % (repr(self.origin), repr(self.direction))

    def pointAtParameter(self, dist):
        """
        @return: gibt die Laenge des Strahls als Vektor zurueck
        """
        return self.origin + self.direction * dist


class Sphere(object):
    """
    @param center: Mittelpunkt der Kugel
    @param radius: Radius der Kugel
    @param material: Material der Kugel
    """

    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def __repr__(self):
        """
        Default Konstruktor
        """
        return 'Sphere(%s, %s)' % (repr(self.center), repr(self.radius))

    def intersectionParameter(self, ray):
        """
        gibt die Distanz zum Intersection Point zurueck
        """
        co = self.center - ray.origin
        v = co.dot(ray.direction)
        discriminant = v * v - co.dot(co) + self.radius * self.radius
        if discriminant < 0:
            return None
        else:
            return v - math.sqrt(discriminant)

    def normalAt(self, p):
        """
        gibt die Normale der Kugel zurueck
        """
        return (p - self.center).normalize()


class Plane(object):
    """
    @param point: ein Punkt auf der Ebene
    @param normal: die Normale der Ebene
    @param material: das Material der Ebene
    """

    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal
        self.material = material

    def __repr(self):
        """
        Default Konstruktor der Ebene
        """
        return 'Plane(%s,%s)' % (repr(self.point), repr(self.normal))

    def intersectionParameter(self, ray):
        """
        gibt die Distanz des Strahls zu der Ebene (Intersection point) zurueck
        """
        op = ray.origin - self.point
        a = op.dot(self.normal)
        b = ray.direction.dot(self.normal)
        if b:
            return -a / b
        else:
            return None

    def normalAt(self, p):
        """
        gibt die Normale der Ebene zurueck
        """
        return self.normal


class Triangle(object):
    """
    @param a: Punkt A des Dreiecks
    @param b: Punkt B des Dreiecks
    @param c: Punkt C des Dreiecks
    @param u: Richtungsvektor von Punkt A zu Punkt B
    @param v: Richtungsvektor von Punkt A zu Punkt C
    @param material: Material des Dreiecks
    """

    def __init__(self, a, b, c, material,):
        self.a = a
        self.b = b
        self.c = c
        self.u = self.b - self.a  # direction vector
        self.v = self.c - self.a  # direction vector
        self.material = material

    def __repr__(self):
        """
        Default Konstruktor
        """
        return 'Triangle(%s,%s, %s)' % (repr(self.a), repr(self.b), repr(self.c))

    def intersectionParameter(self, ray):
        """
       gibt die Distanz des Strahls zu dem Dreieck (Intersection point) zurueck
        """
        w = ray.origin - self.a
        dv = ray.direction.cross(self.v)
        dvu = dv.dot(self.u)
        if dvu == 0.0:
            return None
        wu = w.cross(self.u)
        r = dv.dot(w) / dvu
        s = wu.dot(ray.direction) / dvu
        if 0 <= r and r <= 1 and 0 <= s and s <= 1 and r + s <= 1:
            return wu.dot(self.v) / dvu
        else:
            return None

    def normalAt(self, p):
        """
        Normale des Objekts
        """
        return self.u.cross(self.v).normalize()


if __name__ == "__main__":
    #Objektliste erstellen
    objectList = [
        Sphere(Point(2.5, 3, -10), 2, Material(Color(255, 0, 0))),
        Sphere(Point(-2.5, 3, -10), 2, Material(Color(0, 255, 0))),
        Sphere(Point(0, 7, -10), 2, Material(Color(0, 0, 255))),
        Triangle(Point(2.5, 3, -10), Point(-2.5, 3, -10),
                 Point(0, 7, -10), Material(Color(255, 255, 0))),
        Plane(Point(0, 0, 0), Vector(0, 1, 0),
              CheckedMaterial())
    ]

    
    #Liste mit Lichtquellen erstellen
    lightList = [Point(30, 30, 10), Point(-10, 100, 30)]
    camera = Camera(Point(1, 1.8, 10), Point(0, 1, 0), Point(0, 3, 0), 45)
    camera.setScreenSize(400, 400)
    scene = Scene(camera, objectList, lightList)
    image = scene.render()
    image.show()
