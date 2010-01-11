from django.http import HttpResponse
from django.views.decorators.http import require_POST
from clickbank.ins.forms import ClickBankINSForm
from clickbank.ins.models import ClickBankINS


@require_POST
def ipn(request, item_check_callable=None):
    """
    ClickBank INS endpoint (notify_url).
    Used by ClickBank to confirm transactions.
    http://www.clickbank.com/help/account-help/account-tools/instant-notification-service/
    """
    flag = None
    ins_obj = None
    form = ClickBankINSForm(request.POST)
    if form.is_valid():
        try:
            ins_obj = form.save(commit=False)
        except Exception, e:
            flag = "Exception while processing. (%s)" % e
    else:
        flag = "Invalid form. (%s)" % form.errors

    if ins_obj is None:
        ins_obj = ClickBankINS()

    ins_obj.initialize(request)

    if flag is not None:
        ins_obj.set_flag(flag)
    else:
        if not ins_obj.verify_hash():
            return HttpResponse("INVALID HASH")

    ins_obj.save()
    return HttpResponse("OKAY")

