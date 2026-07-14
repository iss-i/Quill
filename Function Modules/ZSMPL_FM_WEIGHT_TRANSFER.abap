FUNCTION ZSMPL_FM_WEIGHT_TRANSFER.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IV_TARE_WEIGHT) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_UOM) TYPE  MEINS OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_TARE_WEIGHT) TYPE  MENGE13
 *"     REFERENCE(EV_UOM) TYPE  MEINS
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_WEIGHT_TRANSFER                                    *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Store & retrieve tare weight of vessel in an order     *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 
DATA: ls_weight TYPE ztc_wt_transfer.
 
  " If weight details are passed from XStep, update the custom table
   " Store weight
   IF iv_tare_weight IS NOT INITIAL AND iv_uom IS NOT INITIAL.
     ls_weight-control_recipe = iv_control_recipe.
     ls_weight-tare_weight = iv_tare_weight.
     ls_weight-uom = iv_uom.
 
    "Insert ls_weight into ztc_wt_transfer custom table)
     MODIFY ztc_wt_transfer FROM ls_weight.
   ELSE.
     " Retrieve Tare Weight for order
     SELECT SINGLE *
       FROM ztc_wt_transfer
       INTO ls_weight
       WHERE ztc_wt_transfer~control_recipe = iv_control_recipe.
 
      IF sy-subrc <> 0.
         ev_uom = iv_uom.
       ELSE.
         ev_tare_weight = ls_weight-tare_weight.
         ev_uom = ls_weight-uom.
       ENDIF.
 
  ENDIF.
 
ENDFUNCTION.
