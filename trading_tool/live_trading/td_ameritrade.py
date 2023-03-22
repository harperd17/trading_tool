from tda.orders.generic import OrderBuilder
from tda.orders.common import (OrderType, Session, Duration, OrderStrategyType, 
                               EquityInstruction, OptionInstruction, PriceLinkBasis,
                               StopPriceLinkBasis)
from tda.orders.common import one_cancels_other, first_triggers_second
from typing import Union, Optional

import logging
logging.basicConfig(level=logging.WARNING)

class MyOrderBuilder(OrderBuilder):
    def add_order_leg(self, instruction, symbol: str, quantity: int):
        if isinstance(instruction, EquityInstruction):
            self.add_equity_leg(instruction, symbol, quantity)
        if isinstance(instruction, OptionInstruction):
            self.add_option_leg(instruction, symbol, quantity)
    def get_order_builder(self):
        order_builder = OrderBuilder()
        for k, v in self.__dict__.items():
            setattr(order_builder, k, v)
        return order_builder



def _generic_order(session = Session.NORMAL, duration = Duration.DAY, strategy_type = OrderStrategyType.SINGLE):
    return (MyOrderBuilder()
            .set_session(session)
            .set_duration(duration)
            .set_order_strategy_type(strategy_type))

def _opposite_instruction(instruction):
    if isinstance(instruction, EquityInstruction):
        if instruction.name == 'BUY':
            return EquityInstruction.SELL
        if instruction.name == 'SELL_SHORT':
            return EquityInstruction.BUY_TO_CLOSE
    if isinstance(instruction, OptionInstruction):
        if instruction.name == 'BUY_TO_OPEN':
            return OptionInstruction.SELL_TO_CLOSE
        if instruction.name == 'SELL_TO_OPEN':
            return OptionInstruction.BUY_TO_CLOSE
    

def market_order(symbol, quantity, instruction, session = Session.NORMAL, duration = Duration.DAY):
    return (_generic_order(session, duration)
            .set_order_type(OrderType.MARKET)
            .add_order_leg(instruction, symbol, quantity))

def limit_order(symbol, quantity, instruction, limit_price,
                limit_price_link: PriceLinkBasis = PriceLinkBasis.MARK, session = Session.NORMAL, duration = Duration.DAY):
   order = (_generic_order(session, duration)
           .set_order_type(OrderType.LIMIT)
           .set_price_link_basis(limit_price_link)
           .set_price(limit_price))
   order.add_order_leg(instruction, symbol, quantity)
   return order

def stop_limit_order(symbol, quantity, instruction, stop_price: float, limit_price: float,
                     limit_offset: Optional[float] = None, stop_price_link: StopPriceLinkBasis = StopPriceLinkBasis.MARK, 
                     limit_price_link : PriceLinkBasis = PriceLinkBasis.MARK,
                     session = Session.NORMAL, duration = Duration.DAY):
    # validations
    if limit_price is not None and limit_offset is not None:
        logger.warnning("Both limit price and limit spread are provided. Limit spread will be ignored.")
    if limit_price is None and limit_offset is None:
        raise ValueError("Either a limit price or limit spread must be provided. Both are None.")
    # return order
    stop_limit_order = (_generic_order(session, duration)
        .set_order_type(OrderType.STOP_LIMIT)
        .set_stop_price_link_basis(stop_price_link)
        .set_stop_price(stop_price))

    if limit_price is not None:
        stop_limit_order.set_price(limit_price)
    if limit_price is None:
        stop_limit_order.set_stop_price_offset(limit_offset)

    stop_limit_order.add_order_leg(instruction, symbol, quantity)

    return stop_limit_order

def stop_market_order(symbol, quantity, instruction, stop_price,
                      stop_price_link: StopPriceLinkBasis = StopPriceLinkBasis.MARK,
                      session = Session.NORMAL, duration = Duration.DAY):
    return (_generic_order(session, duration)
            .set_order_type(OrderType.STOP)
            .set_stop_price_link_basis(stop_price_link)
            .set_stop_price(stop_price)
            .add_order_leg(instruction, symbol, quantity))

def stop_limit_entry_stop_limit_oco_limit_exit(symbol, quantity, entry_instruction,
                                               entry_stop_price, entry_limit_price,
                                               exit_stop_price, exit_stop_limit_price, exit_limit_price,
                                               entry_stop_price_link: StopPriceLinkBasis = StopPriceLinkBasis.MARK,
                                               entry_limit_price_link: PriceLinkBasis = PriceLinkBasis.MARK,
                                               exit_stop_price_link: StopPriceLinkBasis = StopPriceLinkBasis.MARK,
                                               exit_stop_limit_price_link: PriceLinkBasis = PriceLinkBasis.MARK,
                                               exit_limit_price_link: PriceLinkBasis = PriceLinkBasis.MARK,
                                               session = Session.NORMAL, duration = Duration.DAY):
    # create the entry order - stop limit
    entry_order = stop_limit_order(symbol, quantity, entry_instruction, entry_stop_price,
                                   entry_limit_price, stop_price_link = entry_stop_price_link,
                                   limit_price_link = entry_limit_price_link,
                                   session = session, duration = duration)
    
    # create the first exit order - stop limit
    exit_stop_limit_order = stop_limit_order(symbol, quantity, _opposite_instruction(entry_instruction),
                                             exit_stop_price, exit_stop_limit_price, stop_price_link = exit_stop_price_link,
                                             limit_price_link = exit_stop_limit_price_link,
                                             session = session, duration = duration)

    # create the second exit order - limit order
    exit_limit_order = limit_order(symbol, quantity, _opposite_instruction(entry_instruction), exit_limit_price,
                                   exit_limit_price_link, session, duration)

    # create an OCO for exit orders
    exit_oco_order = one_cancels_other(exit_stop_limit_order.get_order_builder(), exit_limit_order.get_order_builder())

    # return a first triggers second so when entry is triggered, OCO is triggered
    return first_triggers_second(entry_order.get_order_builder(), exit_oco_order)
