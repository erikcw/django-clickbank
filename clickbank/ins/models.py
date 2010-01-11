from clickbank.ins.signals import *
from django.db import models
import hashlib

class ClickBankINS(models.Model):
    """Logs ClickBank INS (Instant Notification Service) interactions."""
    ccustname = models.CharField("Customer Name", max_length=510)
    ccuststate = models.CharField("Customer State", max_length=2, blank=True)
    ccustcc = models.CharField("Customer Country Code", max_length=2, blank=True)
    ccustemail = models.CharField("Customer Email", max_length=255)
    cproditem = models.CharField("ClickBank Product Number", max_length=5)
    cprodtitle = models.CharField("Product Title", help_text="Title of product at time of purchase.", max_length=255, blank=True)
    cprodtype = models.CharField("Type", help_text="Type of product on transaction (STANDARD, and RECURRING).", max_length=11)
    TRANSACTION_TYPE_CHOICES = (
        ('SALE', 'SALE'),
        ('BILL', 'BILL'),
        ('RFND', 'RFND'),
        ('CGBK', 'CGBK'),
        ('INSF', 'INSF'),
        ('CANCEL-REBILL', 'CANCEL-REBILL'),
        ('UNCANCEL-REBILL', 'UNCANCEL-REBILL'),
        ('TEST', 'TEST'),
    )
    ctransaction = models.CharField("Transaction", help_text="Action taken.", choices=TRANSACTION_TYPE_CHOICES, max_length=15)
    ctransaffiliate = models.CharField("Affiliate", help_text="Affiliate on transaction.", max_length=10)
    ctransamount = models.CharField("Net Revenue", help_text="Amount paid to party receiving notification (in pennies (1000 = $10.00))." max_length=10)
    PAYMENT_METHOD_CHOICES = (
        ('PYPL', 'PayPal'),
        ('VISA', 'VISA'),
        ('MSTR', 'MasterCard'),
        ('DISC', 'Discover'),
        ('AMEX', 'American Express'),
        ('SWIT', 'SWIT'),
        ('SOLO', 'SOLO'),
        ('JCBC', 'JCBC'),
        ('DNRS', 'DNRS'),
        ('ENRT', 'ENRT'),
        ('AUST', 'AUST'),
        ('BLME', 'BLME'),
        ('STVA', 'STVA'),
        ('MAES', 'MAES'),
    )
    ctranspaymentmethod = models.CharField("Payment Method", help_text="Method of payment by customer.", choices=PAYMENT_METHOD_CHOICES, max_length=4, blank=True)
    ctranspublisher = models.CharField("Vendor", help_text="Vendor on transaction.", max_length=10)
    ctransreceipt = models.CharField("Receipt Number", help_text="ClickBank receipt number.", max_length=13)
    cupsellreceipt = models.CharField("Parent Reciept", help_text="Parent receipt number for upsell transaction.", max_length=13)
    caffitid = models.CharField("Affiliate ID", help_text="Affiliate tracking id.", max_length=24, blank=True)
    cvendthru = models.CharField("Extra Info", help_text="Extra information passed to order form with duplicated information removed.", max_length=1024, blank=True)
    cverify = models.CharField("Verify", help_text="Used to verify the validity of the previous fields.", max_length=8)
    ctranstime = models.CharField("Transaction Timestamp", help_text="The Epoch time the transaction occurred (not included in cverify).", max_length=10)
    # Non-ClickBank Variables - full INS query and time fields.    
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)  # What we were sent by ClickBank
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"Transaction %s" % self.ctransreceipt

    def is_chargeback(self):
        return self.ctransaction in ('CGBK', 'INSF',)

    def is_payment(self):
        return self.ctransaction in ('SALE', 'BILL',)
    
    def is_refund(self):
        return self.ctransaction == 'RFND'

    def is_subscription_cancellation(self):
        return self.ctransaction == 'CANCEL-REBILL'

    def is_subscription_uncancellation(self):
        return self.ctransaction == 'UNCANCEL-REBILL'

    def is_test(self):
        return self.ctransaction == 'TEST'

    def send_signals(self):
        """Shout for the world to hear whether a txn was successful."""
        # Transaction signals:
        if self.is_payment():
            if self.flag:
                payment_was_flagged.send(sender=self)
            else:
                payment_was_successful.send(sender=self)
        # Subscription signals:
        else:
            if self.is_subscription_cancellation():
                subscription_cancel.send(sender=self)
            elif self.is_subscription_uncancellation():
                subscription_uncancel.send(sender=self)
            elif self.is_refund():
                payment_refund.senf(sender=self)
            elif self.is_chargeback():
                payment_chargeback(sender=self)
            elif self.is_test():
                payment_test.send(sender=self)

    def set_flag(self, info, code=None):
        """Sets a flag on the transaction and also sets a reason."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code

    def verify_hash(self):
        """Verify hash.
        
        Returns:
        True if hash is valid.
        False if transaction is invalid."""
        pop = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (self.ccustname,
                                                                   self.ccustemail,
                                                                   self.ccustcc,
                                                                   self.ccuststate,
                                                                   self.ctransreceipt,
                                                                   self.cproditem,
                                                                   self.ctransaction,
                                                                   self.ctransaffiliate,
                                                                   self.ctranspublisher,
                                                                   self.cprodtype,
                                                                   self.cprodtitle,
                                                                   self.ctranspaymentmethod,
                                                                   self.ctransamount,
                                                                   self.caffitid,
                                                                   self.cvendthru,
                                                                   "YOUR SECRET KEY")

        hash = hashlib.sha1(pop).hexdigest().upper()[:8]
        if hash == self.cverify:
            return True
        else:
            return False

