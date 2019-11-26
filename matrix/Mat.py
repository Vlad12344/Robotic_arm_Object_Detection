import numpy as np
import math

def xyzrpw_2_pose(xyzrpw, type='zxz'):
    """Calculates the pose from the position (mm) and Euler angles (deg), given a [x,y,z,r,p,w] array.
    The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    """
    [x,y,z,r,p,w] = xyzrpw
    a = r
    b = p
    c = w
    ca = math.cos(a)
    sa = math.sin(a)
    cb = math.cos(b)
    sb = math.sin(b)
    cc = math.cos(c)
    sc = math.sin(c)
    return np.array([[cb*cc, cc*sa*sb - ca*sc, ca*cc*sb-sa*sc, x],[cb*sc, ca*cc + sa*sb*sc, ca*sb*sc - cc*sa, y],[-sb, cb*sa, ca*cb, z],[0,0,0,1]])

def Pose_2_TxyzRxyz(H):
    """Retrieve the position (mm) and Euler angles (rad) as an array [x,y,z,rx,ry,rz] given a pose.
    It returns the values that correspond to the following operation:
    H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz).

    :param H: pose
    """
    x = H[0,3]
    y = H[1,3]
    z = H[2,3]
    a = H[0,0]
    b = H[0,1]
    c = H[0,2]
    d = H[1,2]
    e = H[2,2]
    if c > (1.0 - 1e-6):
        ry1 = math.pi/2
        rx1 = 0
        rz1 = math.atan2(H[1,0],H[1,1])
    elif c < (-1.0 + 1e-6):
        ry1 = -math.pi/2
        rx1 = 0
        rz1 = math.atan2(H[1,0],H[1,1])
    else:
        sy = c
        cy1 = +math.sqrt(1-sy*sy)
        sx1 = -d/cy1
        cx1 = e/cy1
        sz1 = -b/cy1
        cz1 =a/cy1
        rx1 = math.atan2(sx1,cx1)
        ry1 = math.atan2(sy,cy1)
        rz1 = math.atan2(sz1,cz1)
    return [x, y, z, rx1, ry1, rz1]


def pose_2_xyzrpw(H):
    """Calculates the equivalent position (mm) and Euler angles (deg) as an [x,y,z,r,p,w] array, given a pose.
    It returns the values that correspond to the following operation:
    transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)

    :param H: pose
    :return: [x,y,z,w,p,r] in mm and deg
    """
    x = H[0,3]
    y = H[1,3]
    z = H[2,3]
    r, p, w = rot_2_euler(H)

    return [x, y, z, r, p, w]

def rot_2_euler(H):
    """x = H[0,3]
    y = H[1,3]
    z = H[2,3]x = H[0,3]
    y = H[1,3]
    z = H[2,3]
    :param R:
    :return:
    """
    if (H[2,0] > (1.0 - 1e-6)):
        p = -math.pi/2
        r = 0
        w = math.atan2(-H[1,2],H[1,1])
    elif H[2,0] < -1.0 + 1e-6:
        p = math.pi/2
        r = 0
        w = math.atan2(H[1,2],H[1,1])
    else:
        p = math.atan2(-H[2,0],math.sqrt(H[0,0]*H[0,0]+H[1,0]*H[1,0]))
        w = math.atan2(H[1,0],H[0,0])
        r = math.atan2(H[2,1],H[2,2])

    return r, p, w

def rot_x(rx):
    crx = math.cos(rx)
    srx = math.sin(rx)

    return np.array([[1,0,0,0], [0,crx,-srx,0], [0,srx,crx,0], [0,0,0,1]])

def rot_y(ry):
    crx = math.cos(ry)
    srx = math.sin(ry)

    return np.array([[crx,0,srx,0], [0,1,0,0], [-srx,0,crx,0], [0,0,0,1]])

def rot_z(rz):
    crx = math.cos(rz)
    srx = math.sin(rz)

    return np.array([[crx,-srx,0,0], [srx,crx,0,0], [0,0,1,0], [0,0,0,1]])

def transl(tx,ty=None,tz=None):
    """Returns a translation matrix (mm)
    :param float tx: translation along the X axis
    :param float ty: translation along the Y axis
    :param float tz: translation along the Z axis
    """
    if ty is None:
        xx = tx[0]
        yy = tx[1]
        zz = tx[2]
    else:
        xx = tx
        yy = ty
        zz = tz
    return np.array([[1,0,0,xx],[0,1,0,yy],[0,0,1,zz],[0,0,0,1]])

def invH(matrix):
    """Returns the inverse of a homogeneous matrix"""
    return np.transpose(matrix)

def matrix_mult(*args):
    result = np.eye(len(args[0][0]))
    for i in args:
        if result.shape[0] == i.shape[1]:
            result = np.matmul(result, i)
        else:
            raise AssertionError('Dimansions are not equal')
    return result

def pose_2_RRPosition(H):
    H = Pose_2_TxyzRxyz(H)
    xyz = H[0:3]
    # rpw = [H[4], H[3], H[5]]
    rpw = H[3:6]
    return [xyz, rpw]

def RRPosition_2_xyzrpw(H):
    return [H[0][0], H[0][1], H[0][2],
            H[1][0], H[1][1], H[1][2]]
