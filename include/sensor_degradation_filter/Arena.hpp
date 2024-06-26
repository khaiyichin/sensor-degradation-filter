#ifndef ARENA_HPP
#define ARENA_HPP

#include <vector>
#include <random>
#include <cmath>
#include <algorithm>
#include <assert.h>
#include <string>
#include <numeric>

/**
 * @brief Class to store arena information
 *
 */
class Arena
{
    /**
     * @brief Struct to store 2-D dimensions
     *
     * @tparam T Any floating or integer types
     */
    template <typename T>
    struct Dimensions
    {
        /**
         * @brief Construct a new Dimensions< T> struct
         *
         */
        Dimensions<T>() {}

        /**
         * @brief Construct a new Dimensions< T> struct
         *
         * @param x x dimension
         * @param y y dimension
         */
        Dimensions<T>(const T &x, const T &y) : x(x), y(y) {}

        T x; ///< x dimension

        T y; ///< y dimension
    };

public:
    /**
     * @brief Construct a new Arena object
     *
     */
    Arena() {}

    /**
     * @brief Construct a new Arena object
     *
     * @param tile_count Number of tiles in x and y dimensions
     * @param lower_lim_2d Lower limit coordinate values in x and y
     * @param tile_size Size of square tiles in units of meters
     * @param fill_ratio Black tile fill ratio
     * @param seed Random number generator seed
     */
    Arena(const std::pair<unsigned int, unsigned int> &tile_count,
          const std::pair<float, float> &lower_lim_2d,
          const float &tile_size,
          const float &fill_ratio,
          const unsigned int &seed = 0);

    /**
     * @brief Generate the tiles
     *
     */
    void GenerateTileArrangement();

    /**
     * @brief Get the Color object
     *
     * @param x x coordinate
     * @param y y coordinate
     * @return unsigned int The color either black (0) or white (1)
     */
    unsigned int GetColor(const float &x, const float &y);

    /**
     * @brief Get the true fill ratio of black tiles to total tiles
     *
     * @return float The fill ratio
     */
    float GetTrueTileDistribution();

    /**
     * @brief Get the total number of tiles in the arena
     *
     * @return unsigned int Number of tiles
     */
    unsigned int GetTotalNumTiles() { return num_tiles_.x * num_tiles_.y; }

private:
    float fill_ratio_; ///< Fill ratio

    float tile_size_; ///< Size of the tile in units of meters

    unsigned int seed_; ///< Random number generator seed

    Dimensions<unsigned int> num_tiles_; ///< Dimensions in units of tiles

    Dimensions<float> lower_lim_; ///< Lower limit coordinates of 2-D arena

    std::vector<std::vector<unsigned int>> layout_; ///< Grid layout of the arena, with values 1 or 0
};

#endif