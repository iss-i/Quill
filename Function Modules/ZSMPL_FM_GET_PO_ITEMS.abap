FUNCTION ZSMPL_FM_GET_PO_ITEMS .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_ORDER) TYPE  AUFNR
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(ET_MATERIAL) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_MAT_DESC) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(ET_BATCH) TYPE  /SMPL/STR_TT_CHARG
 *"     REFERENCE(ET_BOM_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_ISSUED_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_UOM) TYPE  /SMPL/STR_TT_ERFME
 *"     REFERENCE(ET_SERNR) TYPE  /SMPL/STR_TT_SERNR
 *"     REFERENCE(ET_EXP_DT) TYPE  /SMPL/STR_TT_DATE
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_PO_ITEMS                                         *
 * Created by      : Carolina Osorno (COSORNO)                              *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : October 23, 2018                                       *
 * Purpose         : Get PO BOM component details                           *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development         SEDK901153     COSORNO        10/23/2018     *
 *--------------------------------------------------------------------------*
 
  TYPES: BEGIN OF lty_sernr_filter,
            mblnr TYPE mblnr,
            mjahr TYPE mjahr,
            zeile TYPE mblpo,
            taser TYPE taser,
          END OF lty_sernr_filter.
 
  TYPES: BEGIN OF lty_mch1,
     matnr TYPE matnr,
     charg TYPE charg_d,
     vfdat TYPE vfdat,
   END OF lty_mch1.
 
  DATA: lt_components   TYPE STANDARD TABLE OF bapi_order_component,
         st_objects      TYPE bapi_pi_order_objects,
         lt_return       TYPE bapiret2,
         st_component    LIKE LINE OF lt_components,
         it_material     TYPE TABLE OF matnr,
         st_matnr        LIKE LINE OF it_material,
         st_sernr_filter TYPE lty_sernr_filter,
         s_lv_irserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         s_lv_orserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         st_lv_orserob   LIKE LINE OF s_lv_orserob,
         count           TYPE i,
         lt_mch1         TYPE TABLE OF lty_mch1,
         ls_mch1         TYPE lty_mch1.
 
  CONSTANTS: cv_ser_uom    TYPE erfme VALUE 'EA',
              cv_ser_qty    TYPE erfmg VALUE 1,
              cv_bwart TYPE mseg-bwart VALUE '261',
              cv_taser TYPE rserob-taser VALUE 'SER03'.
 
  st_objects-components = abap_true.
 
  CALL FUNCTION 'BAPI_PROCORD_GET_DETAIL'
     EXPORTING
       number        = i_order
       order_objects = st_objects
     IMPORTING
       return        = lt_return
     TABLES
       component     = lt_components.
 
*  " Remove all components from a different phase as input parameter
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
 
  IF lt_components IS NOT INITIAL.
     SELECT matnr, charg, vfdat
       FROM mch1 INTO TABLE @lt_mch1
       FOR ALL ENTRIES IN @lt_components
       WHERE matnr = @lt_components-material and charg = @lt_components-batch.
 
  ENDIF.
 
  LOOP AT lt_components INTO st_component.
 
    CLEAR: st_sernr_filter,
     s_lv_irserob,
     s_lv_orserob.
 
    READ TABLE lt_mch1 INTO ls_mch1 WITH KEY matnr = st_component-material charg = st_component-batch.
     IF sy-subrc = 0.
       lv_dat = ls_mch1-vfdat.
     ENDIF.
 
    APPEND lv_dat to et_exp_dt.
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
      WHERE mseg~aufnr EQ @i_order
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
 *       SERXX               =
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
   ENDLOOP.
 


ENDFUNCTION.
