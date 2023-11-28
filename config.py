from enum import IntEnum

# NOTIFY_TYPE enum
class NotificationTypes(IntEnum):
    NONE  = 0
    EMAIL = 1
    TEXT  = 2
    ALEXA = 3
    ALL   = 4

# Messages used in notifications
common_text = "Previous Balance = {prev_bal:0,.2f} and New Balance = {cur_bal:0,.2f}, ${dol_val:0,.2f} USD (@{usd_xchng:0,.2f}/NRG)"
no_chg_bal = "No change in balance from last check. " + common_text
increase_bal = "New balance increased. " + common_text
decrease_bal = "Current balance is less than previous balance. Please check the block explorer. " + common_text