FUNCTION zsmpl_fm_get_phase_po_itemsebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_PHASE) TYPE  VORNR OPTIONAL
 *"     REFERENCE(IV_BOM_PHASE) TYPE  CHAR1 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(ET_MATERIAL) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_MAT_DESC) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(ET_BATCH) TYPE  /SMPL/STR_TT_CHARG
 *"     REFERENCE(ET_BOM_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_ISSUED_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_UOM) TYPE  /SMPL/STR_TT_ERFME
 *"     REFERENCE(ET_SERNR) TYPE  /SMPL/STR_TT_SERNR
 *"     REFERENCE(ET_P_MATERIAL) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_P_MAT_DESC) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(ET_P_BOM_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_P_UOM) TYPE  /SMPL/STR_TT_ERFME
 *"  TABLES
 *"      COMPONENT STRUCTURE  BAPI_ORDER_COMPONENT OPTIONAL
 *"----------------------------------------------------------------------
 

*--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_PHASE_PO_ITEMS                            *
 * Created by      : Karl Maritz (KMARITZ)                                  *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : January 01, 2019                                       *
 * Purpose         : Get PO BOM component details for specific phase, or    *
 *                   get BOM details for all phase assignments using the    *
 *                   phase-specific filter flag IV_BOM_PHASE (1-Yes,2-No)   *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development           SEDK901153     KMARITZ        01/01/2019   *
 * EBR Enhancements              N/A            JCRAIG         01/03/2025   *
 * Configuration improvements    N/A            JCRAIG         04/10/2025   *
 *--------------------------------------------------------------------------*
   DATA: lv_result TYPE char1.
   TYPES: BEGIN OF lty_sernr_filter,
            mblnr TYPE mblnr,
            mjahr TYPE mjahr,
            zeile TYPE mblpo,
            taser TYPE taser,
          END OF lty_sernr_filter.
 
  TYPES: BEGIN OF lty_bom_proc,
            idnrk TYPE idnrk,
            itsob TYPE cs_sobsl,
          END OF lty_bom_proc.
 

  DATA: lt_components   TYPE STANDARD TABLE OF bapi_order_component,
         st_objects      TYPE bapi_pi_order_objects,
         st_component    LIKE LINE OF lt_components,
         st_sernr_filter TYPE lty_sernr_filter,
         st_bom_proc     TYPE lty_bom_proc,
         s_lv_irserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         s_lv_orserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         st_lv_orserob   LIKE LINE OF s_lv_orserob,
         lv_matnr        TYPE matnr,
         count           TYPE i.
 
  CONSTANTS: cv_ser_uom    TYPE erfme VALUE 'EA',
              cv_ser_qty    TYPE erfmg VALUE 1,
              cv_bwart      TYPE mseg-bwart VALUE '261',
              cv_taser      TYPE rserob-taser VALUE 'SER03',
              cv_phant_proc TYPE stpo-itsob VALUE 50. "Special procurement for phantom assembly
 
*  DATA(lcl_websocket) = NEW zcl_smpl_ebr_apc_ws( ).
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
  st_objects-components = abap_true.
 

  IF gt_components[] IS INITIAL AND  lcl_websocket->gv_function = 'SMPL_EBR'.
     CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL' DESTINATION 'NONE' STARTING NEW TASK 'NEW_TASK'
       PERFORMING f_get ON END OF TASK
       EXPORTING
         number        = iv_order
         order_objects = st_objects
       TABLES
         component     = lt_components.
   ELSEIF gt_components[] IS INITIAL.
     CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL'
       EXPORTING
         number        = iv_order
         order_objects = st_objects
       TABLES
         component     = gt_components.
   ENDIF.
 *  " Remove all components from a different phase as input parameter
 
  IF gt_components[] IS NOT INITIAL.
     lt_components = gt_components.
 
    "Filter out non-current phases if phase-specific filter is set to 1-Yes
     IF iv_bom_phase = '1'.
       DELETE lt_components WHERE operation <> iv_phase.
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
 

    LOOP AT lt_components INTO st_component.
 
      CLEAR:
       st_bom_proc,
       st_sernr_filter,
       s_lv_irserob,
       s_lv_orserob.
 
      lv_matnr = st_component-material.
 
      SELECT stpo~idnrk, stpo~itsob "Get special procurement value from bom
       FROM stpo
       INTO @st_bom_proc
       WHERE stpo~idnrk = @lv_matnr.
       ENDSELECT.
 
      IF st_bom_proc-itsob NE cv_phant_proc. "Check that material is not marked as phantom assembly
         "MATNR is the linetype of et_material with length 40 and st_component-material is a SAP structure BAPI_ORDER_COMPONENT field of length 18
         APPEND st_component-material TO et_material. "#EC CI_FLDEXT_OK[2215424]
         APPEND st_component-material_description TO et_mat_desc.
         APPEND st_component-batch TO et_batch.
         APPEND st_component-entry_quantity TO et_bom_quantity.
         APPEND st_component-withdrawn_quantity TO et_issued_quantity.
         APPEND st_component-entry_uom TO et_uom.
 
        "Load material doc key information
         SELECT mseg~mblnr, mseg~mjahr, mseg~zeile
           FROM mseg
           INTO @st_sernr_filter
          WHERE mseg~aufnr EQ @iv_order
         "mseg~matnr is a field of internal table MSEG with length 40 and i_material is a SAP structure BAPI_ORDER_COMPONENT field of length 18
            AND mseg~matnr EQ @st_component-material "#EC CI_FLDEXT_OK[2215424]
            AND mseg~charg EQ @st_component-batch
            AND mseg~bwart EQ @cv_bwart.
           s_lv_irserob-mblnr = st_sernr_filter-mblnr.
           s_lv_irserob-mjahr = st_sernr_filter-mjahr.
           s_lv_irserob-zeile = st_sernr_filter-zeile.
           s_lv_irserob-taser = cv_taser.
         ENDSELECT.
 
        " Load serial numbers
         CALL FUNCTION 'GET_SERNOS_OF_DOCUMENT'
           EXPORTING
             key_data            = s_lv_irserob
           TABLES
             sernos              = s_lv_orserob
 *           SERXX               =
           EXCEPTIONS
             key_parameter_error = 1
             no_supported_access = 2
             no_data_found       = 3
             OTHERS              = 4.
         IF sy-subrc NE 0.
           " If no serial numbers, add single blank serial number
           APPEND '' TO et_sernr.
         ELSE.
           APPEND '' TO et_sernr.
           " If serial numbers, add blank to first sernr field and then append all subsequent serial numbers with single qty
           LOOP AT s_lv_orserob INTO st_lv_orserob.
             APPEND '' TO et_material.
             APPEND '' TO et_mat_desc.
             APPEND '' TO et_batch.
             APPEND st_lv_orserob-sernr TO et_sernr.
             APPEND cv_ser_qty TO et_bom_quantity.
             APPEND '' TO et_issued_quantity.
             APPEND cv_ser_uom TO et_uom.
           ENDLOOP.
         ENDIF.
       ELSE.
         APPEND st_component-material TO et_p_material. "Write phantom materials to export table
         APPEND st_component-material_description TO et_p_mat_desc.
         APPEND st_component-entry_quantity TO et_p_bom_quantity.
         APPEND st_component-entry_uom TO et_p_uom.
       ENDIF.
     ENDLOOP.
     BREAK srahane.
   ENDIF.
 ENDFUNCTION.
 FORM f_get USING p_task.
 
  IF gt_components[] IS INITIAL.
     RECEIVE RESULTS FROM FUNCTION    'BAPI_PROCORD_GET_DETAIL'
     TABLES
       component     = gt_components.
 
*    DATA(lcl_websocket) = NEW zcl_smpl_ebr_apc_ws( ).
     DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
    IF lcl_websocket->gv_function = 'SMPL_EBR'.
 
*      CALL METHOD lcl_websocket->gv_zcl_smpl_ebr_apc_ws_ref->if_apc_wsp_extension~on_message
       CALL METHOD lcl_websocket->gv_smpl_ebr_cl_apc_ws_ref->if_apc_wsp_extension~on_message
         EXPORTING
           i_message         = lcl_websocket->gv_message_ref
           i_message_manager = lcl_websocket->gv_message_manager_ref
           i_context         = lcl_websocket->gv_context_ref.
     ENDIF.
   ENDIF.
 ENDFORM.
