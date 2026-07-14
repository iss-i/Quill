FUNCTION zsmpl_fm_get_mat_items_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"     REFERENCE(I_MATERIAL) TYPE  MATNR OPTIONAL
 *"     REFERENCE(I_BATCH) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(I_COUNT) TYPE  INT3 OPTIONAL
 *"     REFERENCE(I_FLAG) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(I_PO_INFO) TYPE  CHAR1 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_MATNR) TYPE  MATNR
 *"     REFERENCE(EV_MAT_DESC) TYPE  MAKTX
 *"     REFERENCE(EV_BATCH) TYPE  CHARG_D
 *"     REFERENCE(EV_BOM_QUANTITY) TYPE  ERFMG
 *"     REFERENCE(EV_ISSUED_QUANTITY) TYPE  ERFMG
 *"     REFERENCE(EV_UOM) TYPE  ERFME
 *"     REFERENCE(EV_SERNR) TYPE  SERNR
 *"     REFERENCE(EV_CHAR_EXP_DT) TYPE  CHAR10
 *"     REFERENCE(EV_EXP_DT) TYPE  ETDATE
 *"     REFERENCE(EV_BATCHNO) TYPE  CHARG_D
 *"  EXCEPTIONS
 *"      TOO_MANY_RECORDS
 *"      BATCH_EXPIRED
 *"      DATE_INTERNAL_IS_INVALID
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_MAT_ITEMS_EBR                             *
 * Created by      : Jason Craig (JCRAIG)                                   *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : October 23, 2024                                       *
 * Purpose         : Get Material/Batch component details (expiry)          *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development           N/A           JCRAIG        23/10/2024     *
 * Changes for EBR & Project Dev.    N/A       JCRAIG        13/08/2025     *
 *--------------------------------------------------------------------------*
 

         TYPES: BEGIN OF lty_po_info,
            order TYPE aufnr,
            matnr TYPE matnr,
            batch TYPE charg_d,
          END OF lty_po_info.
 
  DATA: lt_components   TYPE STANDARD TABLE OF bapi_order_component,
         st_objects      TYPE bapi_pi_order_objects,
         st_component    LIKE LINE OF lt_components,
         ls_po_info      TYPE lty_po_info,
         lt_po_info      TYPE TABLE OF lty_po_info,
         lv_matnr        TYPE matnr18,
         lv_char_date    TYPE char10.
 
  CONSTANTS: cv_posnr   TYPE posnr VALUE '0001'.
 
  lv_matnr = i_material.
 
  st_objects-components = abap_true.
 
**************
   "JCRAIG Adding EBR changes to test batches
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
  IF i_po_info IS INITIAL.
 
  IF gt_components[] IS INITIAL AND  lcl_websocket->gv_function = 'SMPL_EBR'.
     CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL' DESTINATION 'NONE' STARTING NEW TASK 'NEW_TASK'
       PERFORMING f_get ON END OF TASK
       EXPORTING
         number        = i_order
         order_objects = st_objects
       TABLES
         component     = lt_components.
   ELSEIF gt_components[] IS INITIAL.
     CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL'
       EXPORTING
         number        = i_order
         order_objects = st_objects
       TABLES
         component     = gt_components.
   ENDIF.
 
  IF gt_components[] IS NOT INITIAL.
     lt_components = gt_components.
 *    ***************
 
*   " Remove all components from a different phase as input parameter
   IF i_phase IS NOT INITIAL.
     DELETE lt_components WHERE operation <> i_phase.
   ENDIF.
 
   IF i_material is not initial.
      DELETE lt_components WHERE material <> lv_matnr.
    ENDIF.
 
  IF i_batch IS NOT INITIAL.
     DELETE lt_components WHERE batch <> i_batch.
   ENDIF.
 

  DATA lv_dat TYPE datum.
   LOOP AT lt_components INTO st_component.
 
    SELECT SINGLE vfdat FROM mch1 INTO lv_dat WHERE charg = st_component-batch."matnr = st_component-material and charg = st_component-batch.
 
    "KWVP774 2026021 Addition
     IF lv_dat < sy-datum.
       RAISE batch_expired.
     ENDIF.
 
    "20240912 JCRAIG add functionality for char date
     IF i_flag = 'X'.
       lv_char_date = lv_dat.
       CALL FUNCTION 'CONVERT_DATE_TO_EXTERNAL'
        EXPORTING
          DATE_INTERNAL                  = lv_dat
        IMPORTING
          DATE_EXTERNAL                  = lv_char_date
        EXCEPTIONS
          DATE_INTERNAL_IS_INVALID       = 1
          OTHERS                         = 2
                 .
       IF SY-SUBRC <> 0.
 *       Implement suitable error handling here
         RAISE date_internal_is_invalid.
       ENDIF.
       ev_char_exp_dt = lv_char_date.
     ELSE.
       ev_exp_dt = lv_dat.
     ENDIF.
     "20240912 JCRAIG add functionality for char date
 
    "MATNR is the linetype of et_material with length 40 and st_component-material is a SAP structure BAPI_ORDER_COMPONENT field of length 18
     ev_mat_desc = st_component-material_description.
     ev_batch = st_component-batch.
     ev_batchno = st_component-batch.
     IF st_component-entry_quantity IS INITIAL.
       ev_bom_quantity = 1.
       ev_issued_quantity = 1.
     ELSE.
       ev_bom_quantity = st_component-entry_quantity.
       ev_issued_quantity = st_component-withdrawn_quantity.
     ENDIF.
     ev_uom = st_component-entry_uom.
 
  ENDLOOP.
 ENDIF.
 
ELSE.
 
  SELECT SINGLE aufnr matnr charg FROM afpo INTO ls_po_info WHERE aufnr = i_order AND posnr = cv_posnr.
 
    IF sy-subrc <> 0.
       MESSAGE 'Invalid Order' TYPE 'S' DISPLAY LIKE 'E'.
     ENDIF.
 
  ev_matnr = ls_po_info-matnr.
   ev_batch = ls_po_info-batch.
 
ENDIF.
 

ENDFUNCTION.
