"""
Note that sometimes you will get duplicate signals emitted, depending on configuration of your systems.
If you do encounter this, you will need to add the "dispatch_uid" to your connect handlers:
http://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
 
"""
from django.dispatch import Signal
 
# Sent when a payment is successfully processed.
payment_was_successful = Signal()
 
# Sent when a payment is flagged.
payment_was_flagged = Signal()
 
# Sent when a subscription was cancelled.
subscription_cancel = Signal()
 
# Sent when a subscription cancellation was reversed.
subscription_uncancel = Signal()
 
# Sent when a refund has been issued.
payment_refund = Signal()

# Sent when a chargeback has been initiated.
payment_chargeback = Signal()

# Sent when a test order has been recieved
payment_test = Signal()
