
"""
Service layer for KPI management
"""
from apps.kpi.models import SubParameter, CutoffWindow, SubParameterWindow


class KPIService:
    """
    Service for KPI-related operations
    """
    
    @staticmethod
    def get_enabled_subparameters(month, year, department=None):
        """
        Get sub-parameters enabled for a specific window
        """
        # Get active cutoff window
        cutoff_window = CutoffWindow.get_active_window(month, year, department)
        
        if not cutoff_window:
            # If no cutoff window, return all active sub-parameters
            return SubParameter.objects.filter(is_active=True)
        
        # Get enabled sub-parameters for this window
        enabled_associations = SubParameterWindow.objects.filter(
            cutoff_window=cutoff_window,
            is_enabled=True
        ).values_list('sub_parameter_id', flat=True)
        
        if enabled_associations:
            return SubParameter.objects.filter(
                id__in=enabled_associations,
                is_active=True
            )
        else:
            # If no associations exist, return all active sub-parameters
            return SubParameter.objects.filter(is_active=True)
    
    @staticmethod
    def is_subparameter_enabled(sub_parameter, month, year, department=None):
        """
        Check if a sub-parameter is enabled for a specific window
        """
        cutoff_window = CutoffWindow.get_active_window(month, year, department)
        
        if not cutoff_window:
            return sub_parameter.is_active
        
        # Check association
        association = SubParameterWindow.objects.filter(
            sub_parameter=sub_parameter,
            cutoff_window=cutoff_window
        ).first()
        
        if association:
            return association.is_enabled
        
        # If no association, default to sub-parameter's is_active
        return sub_parameter.is_active
