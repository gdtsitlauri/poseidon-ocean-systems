#include <cmath>

extern "C" {

double bezier_linear(double p0, double p1, double t) {
    return (1.0 - t) * p0 + t * p1;
}

double nurbs_weighted_point(double p0, double p1, double w0, double w1, double t) {
    const double b0 = 1.0 - t;
    const double b1 = t;
    const double denom = b0 * w0 + b1 * w1 + 1e-12;
    return (b0 * w0 * p0 + b1 * w1 * p1) / denom;
}

double moeller_trumbore_hit(double oz, double dz, double tri_z) {
    if (std::abs(dz) < 1e-12) {
        return -1.0;
    }
    return (tri_z - oz) / dz;
}

}
