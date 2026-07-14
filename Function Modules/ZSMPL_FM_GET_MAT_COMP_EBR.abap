FUNCTION zsmpl_fm_get_mat_comp_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_ORDER) TYPE  AUFNR
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(ET_MATNR) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_MATXT) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(ET_QTY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_UOM) TYPE  /SMPL/STR_TT_ERFME
 *"----------------------------------------------------------------------
 *{   INSERT         DE2K901878                                        1
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_COMP                                         *
 * Created by      : Karl Maritz (KMARITZ)                                  *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : February 1, 2019                                       *
 * Purpose         :                                 *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                          KMARITZ       26/06/2019    *
 *--------------------------------------------------------------------------*
   DATA: lt_components TYPE STANDARD TABLE OF bapi_order_component, "#EC CI_USAGE_OK[2522971] Required for BAPI Call
         st_objects    TYPE bapi_pi_order_objects,
         lt_return     TYPE bapiret2,
         st_component  LIKE LINE OF lt_components,
         lv_info       TYPE potx2.
 

  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).  "zcl_smpl_ebr_apc_ws( ).
   st_objects-components = abap_true.
 

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
 
  ELSEIF gt_components[] IS NOT INITIAL.
     lt_components = gt_components.
 *  " Remove all components from a different phase as input parameter
     IF i_phase IS NOT INITIAL.
       DELETE lt_components WHERE operation <> i_phase.
     ENDIF.
 
    " Remove all components that do not have a required quantity and have other quantities
     DATA ls_tabix TYPE sy-tabix.
     LOOP AT lt_components INTO st_component WHERE req_quan EQ 0.
       ls_tabix = sy-tabix.
 
      " Check table for other rows with same reservation number and item.
       READ TABLE lt_components
         WITH KEY reservation_number = st_component-reservation_number reservation_item = st_component-reservation_item
            TRANSPORTING NO FIELDS.
 
      IF sy-subrc EQ 0.
         DELETE lt_components INDEX ls_tabix.
       ENDIF.
     ENDLOOP.
 
    CLEAR st_component.
 
    LOOP AT lt_components INTO st_component.
 
      APPEND st_component-material TO et_matnr.
       APPEND st_component-material_description TO et_matxt.
       APPEND st_component-req_quan TO et_qty.
       APPEND st_component-base_uom TO et_uom.
 
    ENDLOOP.
   ENDIF.
 *}   INSERT
 ENDFUNCTION.
