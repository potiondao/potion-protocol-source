"""
Usage Example code for the constraints module
"""
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.constraints.bounds import configure_bounds, get_lower_bound, get_upper_bound


def bounds_builder():
    """
    Example Hello World for using the constraints configuration builder

    Returns
    -------
    None
    """
    builder = ConstraintsConfigBuilder().add_lower_bound(
        lambda a: 0.0).add_upper_bound(lambda a: 1.0)

    config = builder.build_config()

    print(config)


def bounds_builder_monotonic():
    """
    Example Hello World for using the constraints configuration builder with monotonic
    constraints

    Returns
    -------
    None
    """
    my_strike = 0.9
    other_strike = 1.0
    other_put_prem = 0.2

    builder = ConstraintsConfigBuilder().add_lower_bound(
        lambda a: other_put_prem - (other_strike - my_strike)).add_upper_bound(
        lambda a: other_put_prem)

    config = builder.build_config()

    print(config)


def bounds_usage():
    """
    Example Hello World for using the constraints module

    Returns
    -------
    None
    """
    config = ConstraintsConfigBuilder().add_lower_bound(
        lambda a: 0.0).add_upper_bound(lambda a: 0.9).add_lower_bound(
        lambda a: 0.1).add_upper_bound(lambda a: 1.0).build_config()

    configure_bounds(config)

    # optionally pass a dict with info to the boundary functions at calculation time
    lower_bound = get_lower_bound({})
    upper_bound = get_upper_bound({})

    print('lb: ', lower_bound, ' ub: ', upper_bound)


if __name__ == '__main__':
    bounds_builder()
    bounds_builder_monotonic()
    bounds_usage()
