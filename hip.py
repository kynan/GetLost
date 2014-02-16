import numpy as np
from numpy import sin, cos, sqrt
import pandas as pd
from sklearn.neighbors import KDTree

fs_df = pd.read_csv('fs.csv')
fs_df.lat = fs_df.lat.apply(float)
fs_df.lng = fs_df.lng.apply(float)


def get_nearby(start, end, dist_meters=50):
    x0, y0 = start
    x1, y1 = end
    dx, dy = x1 - x0, y1 - y0
    m0 = dy / dx
    c0 = y0 - m0 * x0
    m1 = - dx / dy
    c1 = (m0 - m1) * x0 + c0

    m0 = dy / dx
    c0 = y1 - m0 * x1
    m1 = - dx / dy
    c2 = m0 * x1 - m1 * x1 + c0

    theta0 = np.arctan2(dy, dx)

    t = dist_meters / 1000.0 / 111.0
    _y = fs_df.lng
    _x = fs_df.lat
    if m0 > 0:
        idx = (_y > (m0*(_x - t*cos(theta0)) + c0 - t*sin(theta0))) &\
              (_y < (m0*(_x + t*cos(theta0)) + c0 + t*sin(theta0))) &\
              (_y < (m1*(_x - t*sin(theta0)) + c2 + t*cos(theta0))) &\
              (_y > m1*(_x + t*sin(theta0)) + c1 - t*cos(theta0))
    else:
        idx = (_y < (m0*(_x - t*cos(theta0)) + c0 - t*sin(theta0))) &\
              (_y > (m0*(_x + t*cos(theta0)) + c0 + t*sin(theta0))) &\
              (_y < (m1*(_x - t*sin(theta0)) + c2 + t*cos(theta0))) &\
              (_y > m1*(_x + t*sin(theta0)) + c1 - t*cos(theta0))
    return idx


def get_points(start, end, stride):
    x0, y0 = start
    x1, y1 = end
    Dx, Dy = x1 - x0, y1 - y0
    Dh = sqrt(Dx**2 + Dy**2)
    H = np.arange(0.0, Dh, stride)
    theta = np.arctan(Dy/Dx)
    dX = H*cos(theta)
    dY = H*sin(theta)
    X = dX + x0
    Y = dY + y0
    return zip(X, Y)


def get_hip_rank(points, sub):
    sub_coords = sub[['lat', 'lng']].values
    sub_scores = sub.checkinsCount.apply(int).values
    kdt = KDTree(sub_coords, metric='euclidean')
    d, i = kdt.query(np.array(points), k=10)
    return (sub_scores[i] / d**2 * 1e-11).sum(axis=1)


def get_ranking_array(coords):
    indexes = []
    points = []
    for start_coord, end_coord in zip(coords[:-1], coords[1:]):
        indexes.append(get_nearby(start_coord, end_coord, dist_meters=300))
        points.extend(get_points(start_coord, end_coord, 1e-5))
    sub = fs_df[reduce(lambda a, b: a | b, indexes)]

    hip_rank = get_hip_rank(points, sub)
    return hip_rank, hip_rank.sum()
