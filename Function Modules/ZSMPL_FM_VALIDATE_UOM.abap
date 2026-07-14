FUNCTION ZSMPL_FM_VALIDATE_UOM.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_UOM) TYPE  ERFME OPTIONAL
 *"     REFERENCE(IV_VALUE) TYPE  ERFME OPTIONAL
 *"     REFERENCE(IV_BOM_UOM) TYPE  ERFME OPTIONAL
 *"  EXCEPTIONS
 *"      UOM_CHANGED
 *"----------------------------------------------------------------------
 
IF iv_uom IS NOT INITIAL.
   IF iv_uom <> iv_value.
     MESSAGE 'User has changed default UoM - New UoM needs to be confirmed.' TYPE 'S' DISPLAY LIKE 'E'.
     RAISE UOM_CHANGED.
   ENDIF.
 ENDIF.
 
ENDFUNCTION.
