FUNCTION ZSMPL_FM_CALC_WFI.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"     REFERENCE(I_TOT_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(I_OG_QTY) TYPE  ERFMG OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_FIN_VOL) TYPE  ERFMG
 *"     REFERENCE(EV_COMP_R) TYPE  TEXT30
 *"  CHANGING
 *"     REFERENCE(CV_REQ_QTY) TYPE  ERFMG OPTIONAL
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_CALC_WFI                                      *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Calculate the required quantity for WFI based on the   *
 *                    order quantity's remaining component ratio.           *
 *                     Additionally, recalculate the required qty and       *
 *                     component amount for updated batch sizes.           *                        *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 
  DATA: lt_components   TYPE STANDARD TABLE OF bapi_order_component,
         st_objects      TYPE bapi_pi_order_objects,
         lv_ratio        TYPE erfmg,
         lt_return       TYPE bapiret2,
         st_component    LIKE LINE OF lt_components,
         lv_wfi_frac     TYPE erfmg,
         lv_fin_vol      TYPE erfmg,
         count           TYPE i.
 
  CONSTANTS: cv_one   TYPE erfmg VALUE 1.
 
*---------------------------------------------
 "Water for Addition is Calculated by Subtracting the sum of all raw
 "components for a single Base unit of the finished product from the Base Unit
 " e.g. WFI Req Qty = 1 - (0.3 + 0.12 + 0.23)
 " In summary, the BOM quantities of each raw component is added for 1 unit
 " of the main product, and the required WFI amount is the remaining quantity.
 *---------------------------------------------
 
  IF i_order IS NOT INITIAL.
     "Retrieve the planned order quantity
     SELECT SINGLE gamng FROM afko INTO @DATA(l_tot_qty) WHERE aufnr = @i_order.
 
    "If order quantity is passed from XStep, use for calculations instead (optional - updated batch size)
     IF i_tot_qty IS NOT INITIAL.
       l_tot_qty = i_tot_qty.
     ENDIF.
 
    DATA(l_ratio_qty) = l_tot_qty.
 
    st_objects-components = abap_true.
 
    "Retrieve BOM information for current order
     CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL'
       EXPORTING
         number        = i_order
         order_objects = st_objects
       IMPORTING
         return        = lt_return
       TABLES
         component     = lt_components.
 
*    " Remove all components from a different phase as input parameter
     IF i_phase is not initial.
       DELETE lt_components WHERE operation <> i_phase.
     ENDIF.
 
    " Remove all components that do not have a required quantity and have other quantities
     DATA ls_tabix TYPE sy-tabix.
     LOOP AT lt_components INTO st_component WHERE req_quan EQ 0.
       ls_tabix = sy-tabix.
 
      " Check table for other rows with same reservation number and item
       READ TABLE lt_components
         WITH KEY reservation_number = st_component-reservation_number reservation_item = st_component-reservation_item
            TRANSPORTING NO FIELDS.
 
      IF sy-subrc EQ 0.
         DELETE lt_components INDEX ls_tabix.
       ENDIF.
     ENDLOOP.
 
    CLEAR st_component.
 
    DATA lv_dat TYPE datum.
 
    "Calculate ratio of each raw component
     LOOP AT lt_components INTO st_component.
 
      IF st_component-entry_uom = 'G' OR st_component-entry_uom = 'ML'.
         st_component-entry_quantity = st_component-entry_quantity / 1000.
 
        "Skip consumable materials
         ELSEIF st_component-entry_uom = 'EA'.
           CONTINUE.
       ENDIF.
 
      "Calculate Base Unit ratio (e.g. 0.05kg for 1kg of product)
       st_component-entry_quantity = st_component-entry_quantity / l_ratio_qty. "i_tot_qty.
 
      lv_ratio = lv_ratio + st_component-entry_quantity.
 
      CLEAR st_component.
 
    ENDLOOP.
 
    "Calculate remaining WFI ratio
     lv_wfi_frac = cv_one - lv_ratio.
     "Calculate WFI required qty
     lv_fin_vol = lv_wfi_frac * l_tot_qty. "i_tot_qty.
 
    ev_fin_vol = lv_fin_vol.
     cv_req_qty = lv_fin_vol.
 
  ENDIF.
 
  DATA: lv_convert TYPE f.
   "If Batch Size is changed, calculate new required qty's for each original BOM qty
   IF i_tot_qty IS NOT INITIAL AND i_og_qty IS NOT INITIAL.
     lv_convert = i_tot_qty / i_og_qty.
     cv_req_qty = lv_convert * cv_req_qty.
   ENDIF.
 
  "Calculate and output Component Amount (reverse calculated from the required qty)
   DATA: lv_frac_char TYPE char30.
   lv_frac_char = lv_wfi_frac.
   ev_comp_r = lv_wfi_frac && ` ` && 'kg/kg'.
 

ENDFUNCTION.
