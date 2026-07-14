FUNCTION zsmpl_fm_get_wt_itms_by_ty_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_ORDER) TYPE  AUFNR
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"     REFERENCE(I_MAT_TYPE) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(I_PLANT) TYPE  WERKS_D OPTIONAL
 *"     REFERENCE(I_PO_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(I_RATIO) TYPE  ERFMG OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(ET_MATERIAL) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_MAT_DESC) TYPE  /SMPL/STR_TT_MAKTX
 *"     REFERENCE(ET_BATCH) TYPE  /SMPL/STR_TT_CHARG
 *"     REFERENCE(ET_BOM_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_ISSUED_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG
 *"     REFERENCE(ET_UOM) TYPE  /SMPL/STR_TT_ERFME
 *"     REFERENCE(ET_SERNR) TYPE  /SMPL/STR_TT_SERNR
 *"     REFERENCE(ET_EXP_DT) TYPE  /SMPL/STR_TT_DATE
 *"     REFERENCE(ET_MAT_ALT) TYPE  /SMPL/STR_TT_MATNR
 *"     REFERENCE(ET_ORDER) TYPE  AUFNR_T
 *"     REFERENCE(ET_PHASE) TYPE  /SMPL/STR_TT_VORNR
 *"     REFERENCE(ET_PLANT) TYPE  T_WERKS
 *"     REFERENCE(ET_COMP_RATIO) TYPE  /SMPL/STR_TT_TEXT30
 *"     REFERENCE(ET_ITEM) TYPE  /SMPL/STR_TT_RSPOS
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_WEIGH_ITEMS_BY_TY                         *
 * Created by      : Carolina Osorno (COSORNO)                              *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : October 23, 2018                                       *
 * Purpose         : Copy of FM ZSMPL_FM_GET_PO_ITEMS, customized for AZGA  *
 *                   to filter materials according to Liquid or Solid       *
 *                   identifier and filter out EA                           *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development         SEDK901153     COSORNO        10/23/2018     *
 * Adjust for EBR (MOD1)                      JCRAIG         10/02/2025     *
 *--------------------------------------------------------------------------*
 
  TYPES: BEGIN OF lty_sernr_filter,
            mblnr TYPE mblnr,
            mjahr TYPE mjahr,
            zeile TYPE mblpo,
            taser TYPE taser,
          END OF lty_sernr_filter.
 
  TYPES: BEGIN OF lty_mseg_comp,
            matnr TYPE matnr,
            batch TYPE charg_d,
            qty   TYPE erfmg,
            uom   TYPE erfme,
          END OF lty_mseg_comp.
 
  TYPES: BEGIN OF lty_spec,
            matnr TYPE matnr,
            bismt TYPE bismt,
          END OF lty_spec.
 
  TYPES:
     "Material alternates data
     BEGIN OF lty_matnr_results,
       matnr TYPE matnr,
       maktx TYPE maktx,
       blank TYPE maktx,
     END OF lty_matnr_results.
 
  TYPES: BEGIN OF lty_mch1,
     matnr TYPE matnr,
     charg TYPE charg_d,
     vfdat TYPE vfdat,
   END OF lty_mch1.
 
  DATA: lt_alternates TYPE TABLE OF lty_matnr_results,
         ls_alternates LIKE LINE OF lt_alternates.
 
  DATA: lt_components   TYPE STANDARD TABLE OF bapi_order_component,
         st_objects      TYPE bapi_pi_order_objects,
         lt_return       TYPE bapiret2,
         st_component    LIKE LINE OF lt_components,
         it_material     TYPE TABLE OF matnr,
         st_matnr        LIKE LINE OF it_material,
         st_sernr_filter TYPE lty_sernr_filter,
         ls_mseg_comp    TYPE lty_mseg_comp,
         lt_mseg_comp    TYPE TABLE OF lty_mseg_comp,
         lt_mseg_agg     TYPE TABLE OF lty_mseg_comp,
         ls_spec         TYPE lty_spec,
         lt_spec         TYPE TABLE OF lty_spec,
         s_lv_irserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         s_lv_orserob    TYPE STANDARD TABLE OF rserob WITH HEADER LINE,
         st_lv_orserob   LIKE LINE OF s_lv_orserob,
         count           TYPE i,
         lv_suffix       TYPE char6,
         lv_ratio        TYPE erfmg,
         lv_ratio_char   TYPE char10,
         lv_component    TYPE char30,
         lt_mch1         TYPE TABLE OF lty_mch1,
         ls_mch1         TYPE lty_mch1.
 
  CONSTANTS: cv_ser_uom TYPE erfme VALUE 'EA',
              cv_ser_qty TYPE erfmg VALUE 1,
              cv_bwart   TYPE mseg-bwart VALUE '261',
              cv_taser   TYPE rserob-taser VALUE 'SER03',
              cv_solid1  TYPE erfme VALUE 'µG',
              cv_solid2  TYPE erfme VALUE 'MG',
              cv_solid3  TYPE erfme VALUE 'G',
              cv_solid4  TYPE erfme VALUE 'KG',
              cv_iquid1  TYPE erfme VALUE 'µL',
              cv_iquid2  TYPE erfme VALUE 'ML',
              cv_iquid3  TYPE erfme VALUE 'L',
              cv_eaches  TYPE erfme VALUE 'EA',
              cv_weight  TYPE char6 VALUE 'g/kg',
              cv_volum   TYPE char6 VALUE 'mL/kg'.
 
  "MOD1
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
  "KWVP774 14/04
   IF i_order IS NOT INITIAL.
     SELECT SINGLE gamng FROM afko INTO @DATA(l_tot_qty) WHERE aufnr = @i_order.
   ENDIF.
 
  st_objects-components = abap_true.
 
  "MOD1
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
 
*  " Remove all components from a different phase as input parameter
   "MOD1
   IF gt_components[] IS NOT INITIAL.
     lt_components = gt_components.
     IF i_phase IS NOT INITIAL.
       DELETE lt_components WHERE operation <> i_phase.
     ENDIF.
 
* Remove all components with EA as unit of measure
     DELETE lt_components WHERE base_uom = cv_eaches.
 
* Remove all components with incorrect unit of measure if applicable
     IF i_mat_type = 'S'.
       DELETE lt_components WHERE base_uom = cv_iquid1
                               OR base_uom = cv_iquid2
                               OR base_uom = cv_iquid3.
       lv_suffix = cv_weight.
     ELSEIF i_mat_type = 'L'.
       DELETE lt_components WHERE base_uom = cv_solid1
                               OR base_uom = cv_solid2
                               OR base_uom = cv_solid3
                               OR base_uom = cv_solid4.
       lv_suffix = cv_volum.
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
 
    IF lt_components IS NOT INITIAL.
       SELECT matnr, charg, vfdat
         FROM mch1 INTO TABLE @lt_mch1
         FOR ALL ENTRIES IN @lt_components
         WHERE matnr = @lt_components-material and charg = @lt_components-batch.
     ENDIF.
 
    DATA lv_dat TYPE datum.
     LOOP AT lt_components INTO st_component.
 
      CLEAR: st_sernr_filter,
       s_lv_irserob,
       s_lv_orserob.
 
      READ TABLE lt_mch1 INTO ls_mch1 WITH KEY matnr = st_component-material charg = st_component-batch.
       IF sy-subrc = 0.
         lv_dat = ls_mch1-vfdat.
       ENDIF.
 
      APPEND lv_dat TO et_exp_dt.
       "MATNR is the linetype of et_material with length 40 and st_component-material is a SAP structure BAPI_ORDER_COMPONENT field of length 18
       APPEND st_component-material TO et_material. "#EC CI_FLDEXT_OK[2215424]
       APPEND st_component-material TO et_mat_alt.
       APPEND st_component-material_description TO et_mat_desc.
       APPEND st_component-batch TO et_batch.
       APPEND st_component-entry_quantity TO et_bom_quantity.
       APPEND st_component-withdrawn_quantity TO et_issued_quantity.
       APPEND st_component-entry_uom TO et_uom.
       APPEND st_component-item_number TO et_item.
 
      lv_ratio = st_component-entry_quantity / l_tot_qty.
       lv_ratio_char = lv_ratio.
       CONCATENATE lv_ratio_char lv_suffix INTO lv_component SEPARATED BY space.
       APPEND lv_component TO et_comp_ratio.
 
    ENDLOOP.
 


    "20251002 Compare Goods movement Components
     SELECT matnr, charg, erfmg, erfme  "#EC "#EC CI_NOFIRST
       FROM mseg
       INTO TABLE @lt_mseg_comp
      WHERE mseg~aufnr EQ @i_order
     "mseg~matnr is a field of internal table MSEG with length 40 and i_material is a SAP structure BAPI_ORDER_COMPONENT field of length 18
        AND mseg~werks EQ @st_component-prod_plant
        AND mseg~bwart EQ @cv_bwart.
 
    IF sy-subrc <> 0.
       "No goods movement/issued
     ELSE.
       "Aggregate duplicate MSEG entries (same material + batch)
 *      *******
       SORT lt_mseg_comp BY matnr batch.
 
      LOOP AT lt_mseg_comp INTO ls_mseg_comp.
         READ TABLE lt_mseg_agg INTO DATA(ls_agg)
              WITH KEY matnr = ls_mseg_comp-matnr
                       batch = ls_mseg_comp-batch.
         IF sy-subrc = 0.
           ls_agg-qty = ls_agg-qty + ls_mseg_comp-qty.
           MODIFY lt_mseg_agg FROM ls_agg INDEX sy-tabix.
         ELSE.
           APPEND ls_mseg_comp TO lt_mseg_agg.
         ENDIF.
       ENDLOOP.
 
      lt_mseg_comp = lt_mseg_agg.
 *      ****************
 
      LOOP AT lt_mseg_comp INTO ls_mseg_comp.
         " Matching index
         READ TABLE et_material WITH KEY table_line = ls_mseg_comp-matnr TRANSPORTING NO FIELDS.
         IF sy-subrc = 0.
           " Check if this material already exists with the same batch
           READ TABLE et_batch INDEX sy-tabix INTO DATA(lv_batch).
           IF lv_batch = ls_mseg_comp-batch.
             " Update existing line due to same batch
             DATA(lv_index) = sy-tabix.
             MODIFY et_issued_quantity FROM ls_mseg_comp-qty INDEX lv_index.
           ELSE.
             " Create new line for new batch
             APPEND ls_mseg_comp-matnr TO et_material.
             APPEND 0                  TO et_bom_quantity.
             APPEND ls_mseg_comp-qty   TO et_issued_quantity.
             APPEND ls_mseg_comp-uom   TO et_uom.
             APPEND ls_mseg_comp-batch TO et_batch.
             APPEND ls_mseg_comp-matnr TO et_mat_alt.
             DATA lv_desc4 TYPE maktx VALUE ''.
             PERFORM get_material_desc USING ls_mseg_comp-matnr CHANGING lv_desc4.
             APPEND lv_desc4 TO et_mat_desc.
             APPEND '' TO et_item.
           ENDIF.
         ELSE.
 
          "If GI does not match BOM - Check Alternates
           SELECT SINGLE bismt
             FROM mara
             INTO @DATA(lv_spec_nr)
             WHERE matnr = @ls_mseg_comp-matnr.
 
          "If material does not have alternates, append new material
           IF lv_spec_nr IS INITIAL.
             APPEND ls_mseg_comp-matnr TO et_material.
             APPEND ls_mseg_comp-matnr TO et_mat_alt.
             APPEND 0                  TO et_bom_quantity.
             APPEND ls_mseg_comp-qty   TO et_issued_quantity.
             APPEND ls_mseg_comp-uom   TO et_uom.
             APPEND ls_mseg_comp-batch TO et_batch.
             "Get material desc
             DATA lv_desc1 TYPE maktx VALUE ''.
             PERFORM get_material_desc
               USING ls_mseg_comp-matnr
               CHANGING lv_desc1.
             APPEND lv_desc1 TO et_mat_desc.
             APPEND '' TO et_item.
 
            "IF material has alternates
           ELSE.
             SELECT matnr
             FROM mara
             INTO TABLE @DATA(lt_alt_mat)
             WHERE bismt = @lv_spec_nr.
 
            " Check if any alternate is part of the BOM
             DATA(lv_found) = abap_false.
             DATA(lv_idx) = 0.
 
            LOOP AT lt_alt_mat INTO DATA(ls_alt_mat).
               READ TABLE et_material WITH KEY table_line = ls_alt_mat TRANSPORTING NO FIELDS.
               IF sy-subrc = 0.
                 lv_found = abap_true.
 *                lv_index = sy-tabix.
                 lv_idx = sy-tabix.   "20251105 JCRAIG Dump Bugfix
                 EXIT.
               ENDIF.
             ENDLOOP.
 
            IF lv_found = abap_true.
               " Update existing BOM line for the alternate
               MODIFY et_issued_quantity FROM ls_mseg_comp-qty INDEX lv_idx.
               MODIFY et_mat_alt         FROM ls_mseg_comp-matnr INDEX lv_idx.
               "Get material desc
               DATA lv_desc2 TYPE maktx VALUE ''.
               PERFORM get_material_desc
                 USING ls_mseg_comp-matnr
                 CHANGING lv_desc2.
               MODIFY et_mat_desc         FROM lv_desc2 INDEX lv_idx.
             ELSE.
               " Issued material's alternates do not match alternates found of OG - treat as new material
               APPEND ls_mseg_comp-matnr TO et_material.
               APPEND 0                  TO et_bom_quantity.
               APPEND ls_mseg_comp-qty   TO et_issued_quantity.
               APPEND ls_mseg_comp-uom   TO et_uom.
               APPEND ls_mseg_comp-batch TO et_batch.
               APPEND ls_mseg_comp-matnr TO et_mat_alt.
               "Get material desc
               DATA lv_desc3 TYPE maktx VALUE ''.
               PERFORM get_material_desc
                 USING ls_mseg_comp-matnr
                 CHANGING lv_desc3.
               APPEND lv_desc3 TO et_mat_desc.
               APPEND '' TO et_item.
             ENDIF.
 
          ENDIF.
 
        ENDIF.
       ENDLOOP.
 
    ENDIF.
 
  ENDIF.
 
  IF i_ratio IS NOT INITIAL.
     LOOP AT et_bom_quantity ASSIGNING FIELD-SYMBOL(<qty>).
       <qty> = <qty> * i_ratio.
     ENDLOOP.
 *    et_bom_quantity = i_ratio * et_bom_quantity.
   ENDIF.
 
  "20251017 addition
   IF et_material IS NOT INITIAL.
     LOOP AT et_material INTO DATA(lv_mat_temp).
       APPEND i_order TO et_order.
       APPEND i_plant TO et_plant.
       APPEND i_phase TO et_phase.
     ENDLOOP.
   ENDIF.
 
ENDFUNCTION.
 FORM get_material_desc
   USING    iv_matnr TYPE matnr
   CHANGING ev_desc TYPE maktx.
 
  SELECT SINGLE makt~maktx
     FROM mara
     INNER JOIN makt ON makt~matnr = mara~matnr
     INTO @ev_desc
     WHERE mara~matnr = @iv_matnr
       AND makt~spras = @sy-langu.
 
  IF sy-subrc <> 0.
     ev_desc = ''.
   ENDIF.
 
ENDFORM.
