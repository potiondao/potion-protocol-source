"""
Usage Example code for the payoff module
"""
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import configure_payoff, get_payoff_odds, get_position_max_loss


def payoff_builder():
    """
    Example Hello World for using the payoff configuration builder

    Returns
    -------
    None
    """
    builder = PayoffConfigBuilder()

    config = builder.build_config()

    print(config)


def payoff_builder_custom():
    """
    Example Hello World for using the payoff configuration builder with custom logic

    Returns
    -------
    None
    """
    builder = PayoffConfigBuilder().add_option_leg(
        call_or_put='put', direction='short').set_underlying_payoff_leg(1.0, 1.0)

    config = builder.build_config()

    print(config)


def payoff_usage():
    """
    Example Hello World for using the payoff module

    Returns
    -------
    None
    """
    config = PayoffConfigBuilder().add_option_leg(
        call_or_put='put', direction='short').build_config()

    configure_payoff(config)
    odds = get_payoff_odds()
    max_loss = get_position_max_loss()

    print('odds: ', odds)
    print('max loss: ', max_loss)


def payoff_usage_premium():
    """
    Example Hello World for using the payoff module with a custom premium amount

    Returns
    -------
    None
    """
    config = PayoffConfigBuilder().add_option_leg(
        call_or_put='put', direction='short').build_config()

    configure_payoff(config)
    odds = get_payoff_odds(premium=0.1)
    max_loss = get_position_max_loss(premium=0.1)

    print('odds: ', odds)
    print('max loss: ', max_loss)


if __name__ == '__main__':
    payoff_builder()
    payoff_builder_custom()
    payoff_usage()
    payoff_usage_premium()
