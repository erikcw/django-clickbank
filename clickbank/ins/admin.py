from django.contrib import admin
from clickbank.ins.models import ClickBankINS

class ClickBankINSAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ("__unicode__", "flag", "flag_info", "ctransreceipt", "ctransaction", "created",)
    search_fields = ("ctransreceipt", "ccustname", "ccustemail",)

admin.site.register(ClickBankINS, ClickBankINSAdmin)
