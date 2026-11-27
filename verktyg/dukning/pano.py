import numpy as np
from PIL import Image

def _rot(yaw, pitch):
    p, y = np.radians(pitch), np.radians(yaw)
    Rx = np.array([[1,0,0],[0,np.cos(p),-np.sin(p)],[0,np.sin(p),np.cos(p)]])  # camera y-down
    Ry = np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]])
    return Ry @ Rx

def bilinear(im, u, v):
    H, W = im.shape[:2]
    u0 = np.floor(u).astype(int); v0 = np.floor(v).astype(int)
    du = (u - u0)[..., None]; dv = (v - v0)[..., None]
    u1 = (u0 + 1) % W; u0 = u0 % W
    v1 = np.clip(v0 + 1, 0, H-1); v0 = np.clip(v0, 0, H-1)
    a = im[v0, u0]*(1-du) + im[v0, u1]*du
    b = im[v1, u0]*(1-du) + im[v1, u1]*du
    return a*(1-dv) + b*dv

def persp(eq, yaw, pitch, hfov, w, h):
    """eq: float array HxWx3 equirect. returns perspective view (camera y down, pitch + = up)."""
    H, W = eq.shape[:2]
    f = (w/2)/np.tan(np.radians(hfov)/2)
    x = np.arange(w) - w/2 + .5; y = np.arange(h) - h/2 + .5
    X, Y = np.meshgrid(x, y)
    d = np.stack([X, Y, np.full_like(X, f)], -1)
    R = _rot(yaw, pitch)
    d = d @ R.T
    lon = np.arctan2(d[...,0], d[...,2]); lat = np.arctan2(-d[...,1], np.hypot(d[...,0], d[...,2]))
    u = (lon/np.pi + 1)/2*W - .5; v = (0.5 - lat/np.pi)*H - .5
    return bilinear(eq, u, v)

def back(eq_shape, img, yaw, pitch, hfov, rows=None, cols=None):
    """Project perspective img back to equirect grid. Returns (vals, valid, (r0,c-index array)) for region."""
    H, W = eq_shape[:2]; h, w = img.shape[:2]
    f = (w/2)/np.tan(np.radians(hfov)/2)
    r0, r1 = rows; cs = cols
    vv = np.arange(r0, r1) + .5; uu = cs + .5
    U, V = np.meshgrid(uu, vv)
    lon = (U/W*2 - 1)*np.pi; lat = (0.5 - V/H)*np.pi
    d = np.stack([np.cos(lat)*np.sin(lon), -np.sin(lat), np.cos(lat)*np.cos(lon)], -1)
    R = _rot(yaw, pitch)
    c = d @ R  # world -> camera
    z = c[...,2]
    with np.errstate(divide='ignore', invalid='ignore'):
        px = c[...,0]/z*f + w/2 - .5; py = c[...,1]/z*f + h/2 - .5
    valid = (z > 0) & (px >= 0) & (px <= w-1) & (py >= 0) & (py <= h-1)
    px = np.clip(np.nan_to_num(px), 0, w-1); py = np.clip(np.nan_to_num(py), 0, h-1)
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int)
    x1 = np.minimum(x0+1, w-1); y1 = np.minimum(y0+1, h-1)
    dx = (px-x0)[...,None]; dy = (py-y0)[...,None]
    a = img[y0,x0]*(1-dx) + img[y0,x1]*dx; b = img[y1,x0]*(1-dx) + img[y1,x1]*dx
    return a*(1-dy) + b*dy, valid, px, py
