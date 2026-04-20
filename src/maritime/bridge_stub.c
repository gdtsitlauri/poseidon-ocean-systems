#include <math.h>

double bridge_score(double speed_kn, int sea_state) {
    return speed_kn * (1.0 + 0.04 * sea_state) + 0.2 * sqrt(fabs(speed_kn));
}
