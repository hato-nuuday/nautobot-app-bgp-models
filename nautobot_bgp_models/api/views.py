"""REST API viewsets for nautobot_bgp_models."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from nautobot.apps.api import NautobotModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from nautobot_bgp_models import filters, models
from nautobot_bgp_models.api.filter_backends import IncludeInheritedFilterBackend

from . import serializers


class BGPRoutingInstanceViewSet(NautobotModelViewSet):
    """REST API viewset for BGPRoutingInstance records."""

    queryset = models.BGPRoutingInstance.objects.all()
    serializer_class = serializers.BGPRoutingInstanceSerializer
    filterset_class = filters.BGPRoutingInstanceFilterSet


class AutonomousSystemViewSet(NautobotModelViewSet):
    """REST API viewset for AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    filterset_class = filters.AutonomousSystemFilterSet


class AutonomousSystemRangeViewSet(NautobotModelViewSet):
    """REST API viewset for AutonomousSystemRange records."""

    queryset = models.AutonomousSystemRange.objects.all()
    serializer_class = serializers.AutonomousSystemRangeSerializer
    filterset_class = filters.AutonomousSystemRangeFilterSet

    @action(detail=True, methods=["post"], url_path="create-next-asn")
    def create_next_asn(self, request, pk=None):
        """Create the next available ASN in this range for the specified VRF."""
        instance = self.get_object()
        vrf_id = request.data.get("vrf")
        if not vrf_id:
            return Response(
                {"error": "vrf is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            vrf = models.VRF.objects.get(pk=vrf_id)
        except models.VRF.DoesNotExist:
            return Response(
                {"error": "VRF not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Find used ASNs in this range and VRF
        used_asns = set(
            models.AutonomousSystem.objects.filter(
                asn__gte=instance.asn_min,
                asn__lte=instance.asn_max,
                vrf=vrf,
            ).values_list("asn", flat=True)
        )
        # Find the next available ASN
        for asn in range(instance.asn_min, instance.asn_max + 1):
            if asn not in used_asns:
                new_asn = models.AutonomousSystem.objects.create(asn=asn, vrf=vrf)
                serializer = serializers.AutonomousSystemSerializer(
                    new_asn, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "No available ASN in this range for this VRF"},
            status=status.HTTP_409_CONFLICT,
        )


include_inherited = OpenApiParameter(
    name="include_inherited",
    required=False,
    location=OpenApiParameter.QUERY,
    description="Include inherited configuration values",
    type=OpenApiTypes.BOOL,
)


class InheritableFieldsViewSetMixin:
    """Common mixin for ViewSets that support an additional `include_inherited` query parameter."""

    @extend_schema(parameters=[include_inherited])
    def list(self, request):
        """List all objects of this type."""
        return super().list(request)

    @extend_schema(parameters=[include_inherited])
    def retrieve(self, request, pk=None):
        """Retrieve a specific object instance."""
        return super().retrieve(request, pk=pk)


class PeerGroupViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    serializer_class = serializers.PeerGroupSerializer
    filter_backends = [IncludeInheritedFilterBackend, OrderingFilter]
    filterset_class = filters.PeerGroupFilterSet


class PeerGroupTemplateViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerGroupTemplate records."""

    queryset = models.PeerGroupTemplate.objects.all()
    serializer_class = serializers.PeerGroupTemplateSerializer
    filterset_class = filters.PeerGroupTemplateFilterSet


class PeerEndpointViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    serializer_class = serializers.PeerEndpointSerializer
    filter_backends = [IncludeInheritedFilterBackend, OrderingFilter]
    filterset_class = filters.PeerEndpointFilterSet


class PeeringViewSet(NautobotModelViewSet):
    """REST API viewset for Peering records."""

    queryset = models.Peering.objects.all()
    serializer_class = serializers.PeeringSerializer
    filterset_class = filters.PeeringFilterSet


class AddressFamilyViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    serializer_class = serializers.AddressFamilySerializer
    filterset_class = filters.AddressFamilyFilterSet


class PeerGroupAddressFamilyViewSet(
    InheritableFieldsViewSetMixin, NautobotModelViewSet
):
    """REST API viewset for PeerGroupAddressFamily records."""

    queryset = models.PeerGroupAddressFamily.objects.all()
    serializer_class = serializers.PeerGroupAddressFamilySerializer
    filterset_class = filters.PeerGroupAddressFamilyFilterSet


class PeerEndpointAddressFamilyViewSet(
    InheritableFieldsViewSetMixin, NautobotModelViewSet
):
    """REST API viewset for PeerEndpointAddressFamily records."""

    queryset = models.PeerEndpointAddressFamily.objects.all()
    serializer_class = serializers.PeerEndpointAddressFamilySerializer
    filterset_class = filters.PeerEndpointAddressFamilyFilterSet
