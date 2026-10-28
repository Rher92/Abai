from rest_framework.routers import SimpleRouter

from .views import TicketViewSet

# trailing_slash=False keeps the exact paths from the spec: /tickets, /tickets/{id}, /tickets/{id}/send
router = SimpleRouter(trailing_slash=False)
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = router.urls
